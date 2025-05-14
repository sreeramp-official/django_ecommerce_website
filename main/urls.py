from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home_view, name="home"),
    path("shop/", views.shop_view, name="shop"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("add_product/", views.add_product_view, name="add_product"),
    path("product_detail/<str:pk>", views.product_detail_view, name="product_detail"),
    path("add_to_cart/<str:pk>", views.add_to_cart_view, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("confirmation/", views.confirmation_view, name="confirmation"),
    path("delete_product/<str:pk>", views.delete_product_view, name="delete_product"),
    path("update_product/<str:pk>", views.update_product_view, name="update_product"),
    path("order_history/", views.order_history_view, name="order_history"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
