from rest_framework import generics, permissions
from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer
from apps.users.permisions import IsAdminOrReadOnly

# -------------------- Categorías --------------------

# GET /categories/       (listar categorías)
# POST /categories/      (crear categoría)
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by('created_at')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

# GET /categories/<pk>/      (ver detalle)
# PUT/PATCH /categories/<pk>/ (actualizar)
# DELETE /categories/<pk>/   (eliminar)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all().order_by('created_at')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

# -------------------- Productos --------------------

# GET /products/       (listar productos)
# POST /products/      (crear producto)
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(is_active=True).order_by('created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

# GET /products/<pk>/      (ver detalle)
# PUT/PATCH /products/<pk>/ (actualizar)
# DELETE /products/<pk>/   (eliminar)
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.filter(is_active=True).order_by('created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

# -------------------- Reseñas --------------------

# GET /reviews/       (listar reseñas)
# POST /reviews/      (crear reseña)
class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all().order_by('created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrReadOnly]

# GET /reviews/<pk>/      (ver detalle)
# PUT/PATCH /reviews/<pk>/ (actualizar)
# DELETE /reviews/<pk>/   (eliminar)
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all().order_by('created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrReadOnly]

