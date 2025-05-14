from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, Cart, CartItem, Order, OrderItem
from .forms import SignupForm, AddProductForm, CheckoutForm
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied


def is_enduser(user):
    return user.is_authenticated and user.user_type == "enduser"


def is_owner(user):
    return user.is_authenticated and user.user_type == "owner"


def is_admin(user):
    return user.is_authenticated and user.user_type == "admin"


@login_required(login_url="login")
def home_view(request):
    products = Product.objects.all().order_by("-id")[
        :8
    ]  # Orders by the 'id', most recent 8 first
    context = {
        "products": products,
    }
    return render(request, "main/index.html", context)


@login_required(login_url="login")
def shop_view(request):
    products = Product.objects.all()
    latest_products = Product.objects.all().order_by("-id")[:12]

    context = {
        "products": products,
        "latest_products": latest_products,
    }
    return render(request, "main/shop.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
    return render(request, "main/login.html", {})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You have been successfully registered! Welcome!")
            return redirect("home")
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, f"{error}")
    else:
        form = SignupForm()
    return render(request, "main/register.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out!")
        return redirect("login")
    else:
        return redirect("home")


@login_required(login_url="login")
@user_passes_test(lambda user: is_owner(user) or is_admin(user))
def add_product_view(request):
    if request.user.is_authenticated:
        form = AddProductForm(request.POST, request.FILES)
        if request.method == "POST":
            if form.is_valid():
                form.save()
                messages.success(request, "New item added successfully!")
                return redirect("home")
            else:
                messages.error(request, "Invalid data!")
        return render(request, "main/add_product.html", {"form": form})


def product_detail_view(request, pk):
    product = Product.objects.get(id=pk)
    context = {
        "product": product,
    }
    return render(request, "main/product_details.html", context)


@login_required(login_url="login")
@user_passes_test(lambda user: is_enduser(user))
def add_to_cart_view(request, pk):
    product = get_object_or_404(Product, id=pk)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


@login_required(login_url="login")
@user_passes_test(lambda user: is_enduser(user))
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    print(items)
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, "main/cart.html", {"items": items, "total": total})


@login_required(login_url="login")
@user_passes_test(lambda user: is_enduser(user))
def checkout_view(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.items.all()
    subtotal = sum(item.product.price * item.quantity for item in items)
    shipping = 50  # fixed
    total = subtotal + shipping

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data["full_name"],
                address=form.cleaned_data["address"],
                phone=form.cleaned_data["phone"],
                payment_method=form.cleaned_data["payment_method"],
                total_price=total,
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )
            cart.items.all().delete()

            return redirect("confirmation")
    else:
        form = CheckoutForm()

    return render(
        request,
        "main/checkout.html",
        {
            "form": form,
            "items": items,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": total,
        },
    )


@login_required(login_url="login")
@user_passes_test(lambda user: is_enduser(user))
def confirmation_view(request):
    order = Order.objects.filter(user=request.user).last()
    items = order.items.all() if order else []
    return render(request, "main/confirmation.html", {"order": order, "items": items})


@login_required(login_url="login")
@user_passes_test(lambda user: is_owner(user) or is_admin(user))
def delete_product_view(request, pk):
    product = get_object_or_404(Product, id=pk)

    if request.user.user_type == "owner":
        if not hasattr(product, "added_by") or product.added_by != request.user:
            return HttpResponseForbidden("You are not allowed to delete this item.")
    elif request.user.user_type != "admin":
        return HttpResponseForbidden("You are not allowed to delete this item.")

    if request.method == "POST":
        product.delete()
        return redirect("shop")

    return render(request, "main/delete_product.html", {"product": product})


@login_required(login_url="login")
@user_passes_test(lambda user: is_owner(user) or is_admin(user))
def update_product_view(request, pk):
    product = Product.objects.get(id=pk)

    if not (request.user.user_type == "admin" or product.added_by == request.user):
        raise PermissionDenied

    form = AddProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Product Data Has Been Updated!")
            return redirect("product_detail", pk=pk)
        else:
            messages.error(request, "Product Data Has Not Been Updated!")
            return redirect("update_product", pk=pk)

    return render(request, "main/update_product.html", {"form": form})


@login_required(login_url="login")
def order_history_view(request):
    user = request.user

    if user.user_type == "admin":
        orders = (
            Order.objects.all()
            .prefetch_related("items__product", "items__product__added_by")
            .select_related("user")
            .order_by("-created_at")
        )
        for order in orders:
            order.filtered_items = order.items.all()

    elif user.user_type == "owner":
        orders = (
            Order.objects.filter(items__product__added_by=user)
            .prefetch_related("items__product", "items__product__added_by")
            .select_related("user")
            .distinct()
            .order_by("-created_at")
        )

        # Keep only the items the owner added
        for order in orders:
            order.filtered_items = [
                item for item in order.items.all() if item.product.added_by == user
            ]

    else:  # customer
        orders = (
            Order.objects.filter(user=user)
            .prefetch_related("items__product", "items__product__added_by")
            .order_by("-created_at")
        )
        for order in orders:
            order.filtered_items = order.items.all()

    return render(request, "main/order_history.html", {"orders": orders})
