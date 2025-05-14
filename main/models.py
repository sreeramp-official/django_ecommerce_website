from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("admin", "Admin"),
        ("owner", "Shop Owner"),
        ("enduser", "End User"),
    )
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default="enduser"
    )


class Product(models.Model):
    AVAILABILITY_CHOICES = [
        ("in_stock", "In Stock"),
        ("out_of_stock", "Out of Stock"),
    ]

    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.CharField(max_length=15)
    availability = models.CharField(
        max_length=12, choices=AVAILABILITY_CHOICES, default="in_stock"
    )
    description = models.TextField(null=True)
    image = models.ImageField(upload_to="product_images/", blank=True, null=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products_added",
    )

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    PAYMENT_CHOICES = [
        ("cod", "Cash on delivery"),
        ("paypal", "PayPal"),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def order_number(self):
        return f"{self.id:05d}"

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) - Order #{self.order.id} by {self.order.user.username}"
