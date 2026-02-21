from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db import models as db_models
from .models import Category, SubCategory, Product
from cart.models import OrderItem
from .forms import ProductForm
from accounts.forms import ContactForm
from django.contrib import messages

class StorefrontHomeView(ListView):
    model = Product
    template_name = 'products/home.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(is_active=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class VendorDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Product
    template_name = 'products/vendor_dashboard.html'
    context_object_name = 'products'

    def test_func(self):
        return self.request.user.role == 'VENDOR' or self.request.user.is_staff

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_approved'] = self.request.user.is_approved
        return context

class VendorOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = OrderItem
    template_name = 'products/vendor_orders.html'
    context_object_name = 'orders'

    def test_func(self):
        return self.request.user.role == 'VENDOR' or self.request.user.is_staff

    def get_queryset(self):
        # Filter OrderItems where the product belongs to the current vendor
        return OrderItem.objects.filter(product__vendor=self.request.user).select_related('order', 'product', 'order__user').order_by('-order__created_at')

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:vendor_dashboard')

    def test_func(self):
        user = self.request.user
        return (user.role == 'VENDOR' and user.is_approved) or user.is_staff

    def form_valid(self, form):
        form.instance.vendor = self.request.user
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:vendor_dashboard')

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return (user == product.vendor and user.is_approved) or user.is_staff

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:vendor_dashboard')

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return (user == product.vendor and user.is_approved) or user.is_staff

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        try:
            product.delete()
            messages.success(request, f'"{product.name}" has been permanently deleted.')
        except db_models.ProtectedError:
            # Product is referenced by orders — soft delete instead
            product.is_active = False
            product.save()
            messages.warning(
                request,
                f'"{product.name}" has existing orders and cannot be permanently deleted. '
                f'It has been deactivated and hidden from the store instead.'
            )
        return redirect(self.success_url)

class ProductToggleStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['is_active']
    success_url = reverse_lazy('products:vendor_dashboard')

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return user == product.vendor or user.is_staff

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        status = "activated" if product.is_active else "deactivated"
        messages.success(request, f'"{product.name}" has been {status}.')
        return redirect('products:vendor_dashboard')

# Keep a simple function alias for the URL
def toggle_product_status(request, slug):
    from django.contrib.auth.decorators import login_required
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())
    product = get_object_or_404(Product, slug=slug)
    if request.user != product.vendor and not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if request.method == 'POST':
        product.is_active = not product.is_active
        product.save()
        status = "activated" if product.is_active else "deactivated"
        messages.success(request, f'"{product.name}" has been {status}.')
    return redirect('products:vendor_dashboard')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

class CategoryProductListView(ListView):
    model = Product
    template_name = 'products/category_products.html'
    context_object_name = 'products'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        queryset = Product.objects.filter(category=self.category, is_active=True)
        
        subcategory_slug = self.request.GET.get('subcategory')
        if subcategory_slug:
            self.subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category=self.category)
            queryset = queryset.filter(subcategory=self.subcategory)
        else:
            self.subcategory = None
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['selected_subcategory'] = self.subcategory
        return context


class ShopListView(ListView):
    model = Product
    template_name = 'products/shop.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).order_by('-created_at')
        
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        sort = self.request.GET.get('sort')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class AboutUsView(TemplateView):
    template_name = 'products/about_us.html'


class ContactUsView(CreateView):
    form_class = ContactForm
    template_name = 'products/contact_us.html'
    success_url = reverse_lazy('products:contact_us')

    def form_valid(self, form):
        messages.success(self.request, "Thank you for contacting us! We will get back to you soon.")
        return super().form_valid(form)


class BecomeVendorView(TemplateView):
    template_name = 'products/become_vendor.html'

def update_order_item_status(request, item_id):
    from django.contrib.auth.decorators import login_required
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())
        
    item = get_object_or_404(OrderItem, id=item_id)
    
    # Check if the current user is the vendor of the product
    if request.user != item.product.vendor and not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(OrderItem.STATUS_CHOICES):
            item.status = new_status
            item.save()
            messages.success(request, f"Status for {item.product.name} updated to {item.get_status_display()}.")
        else:
            messages.error(request, "Invalid status selected.")
            
    return redirect('products:vendor_orders')
