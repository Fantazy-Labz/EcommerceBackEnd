from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Endpoints para pagos y pedidos
    path('create-payment-intent/', views.CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('payment-success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Webhook de Stripe
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]