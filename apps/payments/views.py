from django.shortcuts import render

# Create your views here.
import stripe
import json
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.orders.models import Order, OrderItem
from .models import Payment
from .serializers import CheckoutSerializer
from apps.orders.serializers import OrderSerializer
from apps.orders.models import Cart, CartItem
from apps.orders.utils import SessionCart
from apps.products.models import Product

# Configurar Stripe con la clave secreta
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    """
    Crea un payment intent de Stripe para iniciar el proceso de pago
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Obtener el carrito del usuario
            cart_manager = SessionCart(request)
            cart = cart_manager.get_cart()
            items = cart_manager.get_items()
            
            if not items:
                return Response({
                    'status': 'error',
                    'message': 'No hay productos en el carrito'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Calcular el total
            total_amount = cart.total_price
            
            # Crear un payment intent en Stripe
            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Stripe usa céntimos
                currency='mxn',
                metadata={'user_id': request.user.id, 'cart_id': cart.id},
            )
            
            # Crear registro de pago en base de datos
            payment = Payment.objects.create(
                user=request.user,
                cart=cart,
                stripe_payment_intent_id=intent.id,
                amount=Decimal(total_amount),
                currency='MXN',
                status='PENDING'
            )
            
            return Response({
                'status': 'success',
                'client_secret': intent.client_secret,
                'payment_id': payment.id
            })
            
        except stripe.error.StripeError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentSuccessView(APIView):
    """
    Maneja la confirmación de pago exitoso desde el frontend
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id')
        
        if not payment_intent_id:
            return Response({
                'status': 'error',
                'message': 'No se proporcionó el ID del payment intent'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verificar que el payment intent existe en Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status != 'succeeded':
                return Response({
                    'status': 'error',
                    'message': 'El pago no se ha completado correctamente'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener el pago de la base de datos
            payment = get_object_or_404(Payment, stripe_payment_intent_id=payment_intent_id)
            
            # Actualizar estado del pago
            payment.status = 'COMPLETED'
            payment.save()
            
            # Crear el pedido a partir del carrito
            if payment.cart:
                cart_items = CartItem.objects.filter(cart=payment.cart)
                
                order_data = {
                    'user': request.user,
                    'payment': payment,
                    'total_amount': payment.amount,
                    'status': 'PAID',
                    'shipping_address': request.data.get('shipping_address', ''),
                    'contact_phone': request.data.get('contact_phone', '')
                }
                
                order = Order.objects.create(**order_data)
                
                # Crear los items del pedido
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product_name=cart_item.product.name,
                        product_id=cart_item.product.id,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                    
                    # Actualizar el stock del producto
                    product = cart_item.product
                    product.stock -= cart_item.quantity
                    product.save()
                
                # Vaciar el carrito
                cart_manager = SessionCart(request)
                cart_manager.clear()
                
                # Serializar el pedido para la respuesta
                serializer = OrderSerializer(order)
                
                return Response({
                    'status': 'success',
                    'message': 'Pago procesado correctamente',
                    'order': serializer.data
                })
            
            return Response({
                'status': 'success',
                'message': 'Pago procesado correctamente, pero no se creó un pedido'
            })
            
        except stripe.error.StripeError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_view(request):
    """
    Procesa el checkout, creando un pedido y preparando el pago
    """
    serializer = CheckoutSerializer(data=request.data)
    
    if serializer.is_valid():
        # Obtener el carrito del usuario
        cart_manager = SessionCart(request)
        cart = cart_manager.get_cart()
        items = cart_manager.get_items()
        
        if not items:
            return Response({
                'status': 'error',
                'message': 'No hay productos en el carrito'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar disponibilidad de stock
        for item in items:
            if item.quantity > item.product.stock:
                return Response({
                    'status': 'error',
                    'message': f'No hay suficiente stock para {item.product.name}. Disponible: {item.product.stock}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear un payment intent en Stripe
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(cart.total_price * 100),  # Stripe usa céntimos
                currency='mxn',
                metadata={'user_id': request.user.id, 'cart_id': cart.id},
            )
            
            # Guardar pago en la base de datos
            payment = Payment.objects.create(
                user=request.user,
                cart=cart,
                stripe_payment_intent_id=intent.id,
                amount=cart.total_price,
                currency='MXN',
                status='PENDING',
                payment_method=serializer.validated_data.get('payment_method', 'card')
            )
            
            # Crear un pedido pre-pago
            order_data = {
                'user': request.user,
                'payment': payment,
                'total_amount': cart.total_price,
                'status': 'CREATED',
                'shipping_address': serializer.validated_data['shipping_address'],
                'contact_phone': serializer.validated_data['contact_phone']
            }
            
            # Crear el pedido con sus items
            items_data = []
            for item in items:
                items_data.append({
                    'product_name': item.product.name,
                    'product_id': item.product.id,
                    'quantity': item.quantity,
                    'price': item.product.price
                })
            
            order_serializer = OrderSerializer(data=order_data, context={'items': items_data})
            
            if order_serializer.is_valid():
                order = order_serializer.save()
                
                return Response({
                    'status': 'success',
                    'client_secret': intent.client_secret,
                    'payment_id': payment.id,
                    'order_id': order.id
                })
            else:
                # Si hay un error en la creación del pedido, cancelamos el payment intent
                stripe.PaymentIntent.cancel(intent.id)
                payment.status = 'FAILED'
                payment.save()
                
                return Response({
                    'status': 'error',
                    'message': 'Error al crear el pedido',
                    'errors': order_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except stripe.error.StripeError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'status': 'error',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_history(request):
    """
    Obtiene el historial de pedidos del usuario
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response({
        'status': 'success',
        'orders': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """
    Obtiene los detalles de un pedido específico
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    serializer = OrderSerializer(order)
    return Response({
        'status': 'success',
        'order': serializer.data
    })


@csrf_exempt
def stripe_webhook(request):
    """
    Webhook para recibir notificaciones de eventos de Stripe
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Payload inválido
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Firma inválida
        return HttpResponse(status=400)
    
    # Manejar el evento
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        # Actualizar el pago en la base de datos
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.status = 'COMPLETED'
            payment.save()
            
            # Actualizar el pedido si existe
            order = Order.objects.filter(payment=payment).first()
            if order:
                order.status = 'PAID'
                order.save()
                
        except Payment.DoesNotExist:
            pass  # Manejar caso donde no se encuentra el pago
            
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        
        # Actualizar el pago en la base de datos
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.status = 'FAILED'
            payment.save()
            
            # Actualizar el pedido si existe
            order = Order.objects.filter(payment=payment).first()
            if order:
                order.status = 'CANCELED'
                order.save()
                
        except Payment.DoesNotExist:
            pass  # Manejar caso donde no se encuentra el pago
    
    return HttpResponse(status=200)