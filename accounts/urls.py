from django.urls import path
from .views import UserLoginView, UserRegistrationView, UserLogoutView, VendorProfileUpdateView, CustomerProfileUpdateView, BecomeVendorView

app_name = 'accounts'

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", VendorProfileUpdateView.as_view(), name="vendor_profile"),
    path("customer/profile/", CustomerProfileUpdateView.as_view(), name="customer_profile"),
    path("become-vendor/", BecomeVendorView.as_view(), name="become_vendor"),
]
