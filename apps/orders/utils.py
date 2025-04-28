import uuid

class OrderManager:
    
    @staticmethod
    def get_session_id(request):
        session_id = request.session.session_key
        if not session_id:
            request.session.create()  
            session_id = request.session.session_key
        return session_id

    @staticmethod
    def generate_order_number():
        return str(uuid.uuid4()).replace('-', '')[:10]
    
    @staticmethod
    def get_cart_total_price(cart):
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())
        return total_price
    
    @staticmethod
    def get_cart_items_count(cart):
        return cart.items.count()
    
    @staticmethod
    def get_order_total_price(order):
        total_price = sum(item.total_price for item in order.items.all())
        return total_price
