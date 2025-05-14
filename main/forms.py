from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Product
from django.core.exceptions import ValidationError
import re


class SignupForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ("enduser", "End User"),
        ("owner", "Shop Owner"),
    )

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.Select())

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2", "user_type"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if len(username) < 6:
            raise ValidationError("Username must be at least 6 characters long.")
        if not re.match(r"^\w+$", username):
            raise ValidationError(
                "Username can only contain letters, numbers, and underscores."
            )
        return username

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*()]", password):
            raise ValidationError(
                "Password must contain at least one special character (!@#$%^&*())."
            )
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", "category", "availability", "description", "image"]


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea)
    phone = forms.CharField(max_length=15)
    PAYMENT_CHOICES = [
        ("cod", "Cash on delivery"),
        ("paypal", "PayPal"),
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES, widget=forms.RadioSelect
    )
    accept_terms = forms.BooleanField(
        label="I’ve read and accept the terms & conditions", required=True
    )
