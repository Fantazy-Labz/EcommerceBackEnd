from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from apps.products.models import Product
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .utils import SessionCart, OrderManager
from decimal import Decimal

class CartView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = SessionCart(request)
        return Response({"items": cart.get_items(), "count": cart.total_count()})

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        cart = SessionCart(request)
        cart.add(product_id, quantity)
        return Response({"message": "Item added to cart"})

    def delete(self, request):
        product_id = request.data.get("product_id")
        cart = SessionCart(request)
        cart.remove(product_id)
        return Response({"message": "Item removed"})


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = SessionCart(request)
        items = cart.get_items()

        if not items:
            return Response({"error": "Cart is empty"}, status=400)

        total = 0
        order_items = []

        for product_id, quantity in items.items():
            product = Product.objects.get(id=product_id)
            unit_price = product.price
            total_price = unit_price * quantity
            total += total_price
            order_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price
            })

        order = Order.objects.create(
            user=request.user,
            address=request.user.addresses.first(),  # puedes ajustarlo
            total_amount=total,
            order_number=OrderManager.generate_order_number()
        )

        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total_price=item['total_price']
            )

        cart.clear()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
