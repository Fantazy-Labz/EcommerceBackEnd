import stripe
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for handling Stripe payments."""
    
    @staticmethod
    def create_payment_intent(order, request=None):
        """Create a payment intent for an order."""
        try:
            # Create metadata for the payment intent
            metadata = {
                'order_id': order.id,
                'order_number': order.order_number,
                'user_id': order.user.id,
                'user_email': order.user.email,
            }
            
            # Calculate amount in cents/smallest currency unit
            amount = int(order.total * 100)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=settings.STRIPE_CURRENCY,
                metadata=metadata,
                description=f"Payment for order #{order.order_number}",
                receipt_email=order.user.email,
                automatic_payment_methods={'enabled': True},
            )
            
            # Update order with payment intent ID
            order.stripe_payment_intent_id = intent.id
            order.save(update_fields=['stripe_payment_intent_id'])
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            }
            
        except stripe.error.StripeError as e:
            # Handle Stripe errors
            error_message = str(e)
            return {
                'error': error_message
            }
    
    @staticmethod
    def confirm_payment(payment_intent_id):
        """Confirm a payment with Stripe."""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'status': intent.status,
                'success': intent.status == 'succeeded',
                'amount': intent.amount / 100,  # Convert back from cents
                'payment_method': intent.payment_method,
                'receipt_url': intent.charges.data[0].receipt_url if intent.charges.data else None,
            }
            
        except stripe.error.StripeError as e:
            return {
                'error': str(e),
                'success': False
            }
    
    @staticmethod
    def create_refund(payment_intent_id, amount=None, reason=None):
        """Create a refund for a payment."""
        try:
            refund_params = {
                'payment_intent': payment_intent_id,
            }
            
            if amount:
                refund_params['amount'] = int(amount * 100)
            
            if reason:
                refund_params['reason'] = reason
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                'refund_id': refund.id,
                'status': refund.status,
                'success': refund.status == 'succeeded',
                'amount': refund.amount / 100 if refund.amount else None,
            }
            
        except stripe.error.StripeError as e:
            return {
                'error': str(e),
                'success': False
            }
    
    @staticmethod
    def create_checkout_session(order, success_url, cancel_url):
        """Create a Stripe Checkout Session for an order."""
        try:
            # Prepare line items for Checkout
            line_items = []
            for item in order.items.all():
                line_items.append({
                    'price_data': {
                        'currency': settings.STRIPE_CURRENCY,
                        'product_data': {
                            'name': item.product_name,
                            'description': f"{item.product.description[:100]}..." if len(item.product.description) > 100 else item.product.description,
                            'metadata': {
                                'product_id': item.product.id,
                            }
                        },
                        'unit_amount': int(item.unit_price * 100),
                    },
                    'quantity': item.quantity,
                })
            
            # Add shipping as a line item if applicable
            if order.shipping_cost > 0:
                line_items.append({
                    'price_data': {
                        'currency': settings.STRIPE_CURRENCY,
                        'product_data': {
                            'name': 'Shipping',
                            'description': 'Shipping cost',
                        },
                        'unit_amount': int(order.shipping_cost * 100),
                    },
                    'quantity': 1,
                })
            
            # Add tax as a line item if applicable
            if order.tax > 0:
                line_items.append({
                    'price_data': {
                        'currency': settings.STRIPE_CURRENCY,
                        'product_data': {
                            'name': 'Tax',
                            'description': 'Tax amount',
                        },
                        'unit_amount': int(order.tax * 100),
                    },
                    'quantity': 1,
                })
            
            # Create the checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                metadata={
                    'order_id': order.id,
                    'order_number': order.order_number,
                },
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=order.user.email,
            )
            
            return {
                'session_id': checkout_session.id,
                'checkout_url': checkout_session.url,
            }
            
        except stripe.error.StripeError as e:
            return {
                'error': str(e),
                'success': False
            }
    
    @staticmethod
    def handle_webhook(request):
        """Handle Stripe webhook events."""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            # Handle the event based on its type
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                # Handle successful payment
                from .models import Payment
                from orders.models import Order
                
                try:
                    order = Order.objects.get(stripe_payment_intent_id=payment_intent.id)
                    order.payment_status = 'paid'
                    order.status = 'processing'
                    order.save()
                    
                    # Create payment record
                    Payment.objects.create(
                        user=order.user,
                        order=order,
                        payment_method='stripe',
                        amount=payment_intent.amount / 100,
                        status='completed',
                        transaction_id=payment_intent.charges.data[0].id if payment_intent.charges.data else None,
                        payment_intent_id=payment_intent.id
                    )
                    
                except Order.DoesNotExist:
                    # Log this issue
                    print(f"Order with payment intent {payment_intent.id} not found")
                
            elif event.type == 'payment_intent.payment_failed':
                payment_intent = event.data.object
                # Handle failed payment
                try:
                    order = Order.objects.get(stripe_payment_intent_id=payment_intent.id)
                    order.payment_status = 'failed'
                    order.save()
                    
                    # Create failed payment record
                    Payment.objects.create(
                        user=order.user,
                        order=order,
                        payment_method='stripe',
                        amount=payment_intent.amount / 100,
                        status='failed',
                        payment_intent_id=payment_intent.id,
                        error_message=payment_intent.last_payment_error.message if payment_intent.last_payment_error else 'Payment failed'
                    )
                    
                except Order.DoesNotExist:
                    # Log this issue
                    print(f"Order with payment intent {payment_intent.id} not found")
            
            # Add more event handlers as needed
            
            return HttpResponse(status=200)
            
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)