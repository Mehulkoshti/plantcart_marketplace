from django.urls import path
from .views import (
    UserLoginView, UserRegistrationView, UserLogoutView, 
    VendorProfileUpdateView, CustomerProfileUpdateView, BecomeVendorView,
    AddressListView, AddressCreateView, delete_address, set_default_address
)

app_name = 'accounts'

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegistrationFormView.as_view() if 'UserRegistrationFormView' in locals() else UserRegistrationView.as_view(), name="register"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", VendorProfileUpdateView.as_view(), name="vendor_profile"),
    path("customer/profile/", CustomerProfileUpdateView.as_view(), name="customer_profile"),
    path("become-vendor/", BecomeVendorView.as_view(), name="become_vendor"),
    
    # Address Book
    path("addresses/", AddressListView.as_view(), name="address_list"),
    path("addresses/add/", AddressCreateView.as_view(), name="address_add"),
    path("addresses/delete/<int:pk>/", delete_address, name="address_delete"),
    path("addresses/default/<int:pk>/", set_default_address, name="address_default"),
]
