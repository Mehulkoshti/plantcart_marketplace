from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import User, Address
from .forms import UserRegistrationForm, VendorProfileForm, CustomerProfileForm, AddressForm

class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = "register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        if user.role == 'VENDOR':
            user.is_approved = False
            # Basic validation check for shop details if role is VENDOR
            required_fields = ['shop_name', 'shop_address', 'business_type', 'phone_number']
            for field in required_fields:
                if not form.cleaned_data.get(field):
                    form.add_error(field, f'{field.replace("_", " ").capitalize()} is required for vendors.')
                    return self.form_invalid(form)
        user.save()
        if user.role == 'VENDOR':
            messages.success(self.request, "Account created successfully! Admin will approve your vendor status soon.")
        else:
            messages.success(self.request, "Account created successfully! You can now login.")
        return super().form_valid(form)

class UserLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")
class UserLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        user = self.request.user

        if user.role == "ADMIN":
            return reverse_lazy("admin_panel:dashboard")
        elif user.role == "VENDOR":
            return reverse_lazy("products:vendor_dashboard")
        else:
            return reverse_lazy("products:home")

class VendorProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = VendorProfileForm
    template_name = "vendor_profile.html"
    success_url = reverse_lazy("accounts:vendor_profile")

    def test_func(self):
        return self.request.user.role == 'VENDOR'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

class CustomerProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomerProfileForm
    template_name = "customer_profile.html"
    success_url = reverse_lazy("accounts:customer_profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

class BecomeVendorView(TemplateView):
    template_name = "become_vendor.html"

# --- Address Book Views ---

class AddressListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/address_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = self.request.user.addresses.all().order_by('-is_default', '-created_at')
        return context

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = "accounts/address_form.html"
    success_url = reverse_lazy('accounts:address_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Address added successfully!")
        return super().form_valid(form)

def delete_address(request, pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    from .models import Address
    address = Address.objects.get(pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Address deleted.")
    return redirect('accounts:address_list')

def set_default_address(request, pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    from .models import Address
    address = Address.objects.get(pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, f"'{address.full_name}' set as default address.")
    return redirect('accounts:address_list')
