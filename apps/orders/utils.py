import uuid

class SessionCart:
    SESSION_KEY = 'cart'

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(self.SESSION_KEY, {})

    def add(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.session.modified = True

    def save(self):
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True

    def get_items(self):
        return self.cart

    def total_count(self):
        return sum(self.cart.values())


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
