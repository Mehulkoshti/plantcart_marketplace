from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth
from accounts.models import User, ContactMessage
from products.models import Product, Category, SubCategory
from cart.models import Order
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

def admin_required(user):
    return user.is_authenticated

class AdminRequiredMixin(LoginRequiredMixin):
    pass

@user_passes_test(admin_required, login_url='admin_panel:login')
def admin_dashboard(request):
    total_customers = User.objects.filter(role='CUSTOMER').count()
    total_vendors = User.objects.filter(role='VENDOR').count()
    total_plants = Product.objects.count()
    
    # Total Marketplace Sales (Excluding Cancelled)
    total_sales = Order.objects.exclude(status='CANCELLED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    # Admin Revenue (10% Commission)
    admin_revenue = float(total_sales) * 0.1
    
    recent_orders = Order.objects.order_by('-created_at')[:5]
    pending_vendors = User.objects.filter(role='VENDOR', is_approved=False).count()
    
    context = {
        'total_customers': total_customers,
        'total_vendors': total_vendors,
        'total_plants': total_plants,
        'total_sales': total_sales,
        'admin_revenue': admin_revenue,
        'recent_orders': recent_orders,
        'pending_vendors': pending_vendors,
    }
    return render(request, 'admin_panel/dashboard.html', context)

class AdminLoginView(LoginView):
    template_name = 'admin_panel/login.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_panel:dashboard')

admin_login = AdminLoginView.as_view()

@user_passes_test(admin_required, login_url='admin_panel:login')
def vendor_list(request):
    vendors = User.objects.filter(role='VENDOR').order_by('-id')
    return render(request, 'admin_panel/vendors.html', {'vendors': vendors})

@user_passes_test(admin_required, login_url='admin_panel:login')
def vendor_detail(request, pk):
    vendor = get_object_or_404(User, pk=pk, role='VENDOR')
    return render(request, 'admin_panel/vendor_detail.html', {'vendor': vendor})

@user_passes_test(admin_required, login_url='admin_panel:login')
def approve_vendor(request, pk):
    vendor = get_object_or_404(User, pk=pk, role='VENDOR')
    vendor.is_approved = True
    vendor.save()
    messages.success(request, f"Vendor {vendor.shop_name} has been approved.")
    return redirect('admin_panel:vendor_list')

@user_passes_test(admin_required, login_url='admin_panel:login')
def reject_vendor(request, pk):
    vendor = get_object_or_404(User, pk=pk, role='VENDOR')
    vendor.is_approved = False
    vendor.save()
    messages.warning(request, f"Vendor {vendor.shop_name} status set to Unapproved.")
    return redirect('admin_panel:vendor_list')

@user_passes_test(admin_required, login_url='admin_panel:login')
def category_list(request):
    categories = Category.objects.all().annotate(product_count=Count('products'))
    return render(request, 'admin_panel/categories.html', {'categories': categories})

@user_passes_test(admin_required, login_url='admin_panel:login')
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        if name:
            Category.objects.create(name=name, description=description, image=image)
            messages.success(request, "Category created successfully.")
            return redirect('admin_panel:category_list')
    return render(request, 'admin_panel/category_form.html')

@user_passes_test(admin_required, login_url='admin_panel:login')
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        if request.FILES.get('image'):
            category.image = request.FILES.get('image')
        category.save()
        messages.success(request, "Category updated successfully.")
        return redirect('admin_panel:category_list')
    return render(request, 'admin_panel/category_form.html', {'category': category})

@user_passes_test(admin_required, login_url='admin_panel:login')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted successfully.")
    return redirect('admin_panel:category_list')

@user_passes_test(admin_required, login_url='admin_panel:login')
def subcategory_list(request):
    subcategories = SubCategory.objects.all().select_related('category').annotate(product_count=Count('products'))
    return render(request, 'admin_panel/subcategories.html', {'subcategories': subcategories})

@user_passes_test(admin_required, login_url='admin_panel:login')
def subcategory_create(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        if name and category_id:
            category = get_object_or_404(Category, id=category_id)
            SubCategory.objects.create(name=name, category=category, description=description, image=image)
            messages.success(request, "Sub-category created successfully.")
            return redirect('admin_panel:subcategory_list')
    return render(request, 'admin_panel/subcategory_form.html', {'categories': categories})

@user_passes_test(admin_required, login_url='admin_panel:login')
def subcategory_update(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        subcategory.name = request.POST.get('name')
        category_id = request.POST.get('category')
        subcategory.description = request.POST.get('description')
        if category_id:
            subcategory.category = get_object_or_404(Category, id=category_id)
        if request.FILES.get('image'):
            subcategory.image = request.FILES.get('image')
        subcategory.save()
        messages.success(request, "Sub-category updated successfully.")
        return redirect('admin_panel:subcategory_list')
    return render(request, 'admin_panel/subcategory_form.html', {
        'subcategory': subcategory,
        'categories': categories
    })

@user_passes_test(admin_required, login_url='admin_panel:login')
def subcategory_delete(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    subcategory.delete()
    messages.success(request, "Sub-category deleted successfully.")
    return redirect('admin_panel:subcategory_list')

# --- Order Management ---
@user_passes_test(admin_required, login_url='admin_panel:login')
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/orders.html', {'orders': orders})

@user_passes_test(admin_required, login_url='admin_panel:login')
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'admin_panel/order_detail.html', {'order': order})

@user_passes_test(admin_required, login_url='admin_panel:login')
def generate_invoice(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'admin_panel/invoice.html', {'order': order})

# --- Product Management ---
@user_passes_test(admin_required, login_url='admin_panel:login')
def product_list(request):
    products = Product.objects.all().select_related('category', 'subcategory', 'vendor')
    
    # Filtering
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    vendor_id = request.GET.get('vendor')
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if subcategory_id:
        products = products.filter(subcategory_id=subcategory_id)
    if vendor_id:
        products = products.filter(vendor_id=vendor_id)
        
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    vendors = User.objects.filter(role='VENDOR')
    
    return render(request, 'admin_panel/products.html', {
        'products': products,
        'categories': categories,
        'subcategories': subcategories,
        'vendors': vendors
    })

@user_passes_test(admin_required, login_url='admin_panel:login')
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'admin_panel/product_detail.html', {'product': product})

# --- Analytics & Reports ---
@user_passes_test(admin_required, login_url='admin_panel:login')
def analytics_reports(request):
    # Monthly Revenue (Excluding Cancelled, showing Admin's 10% cut)
    monthly_revenue = Order.objects.exclude(status='CANCELLED') \
        .annotate(month=TruncMonth('created_at')) \
        .values('month') \
        .annotate(
            total_sales=Sum('total_amount'),
            admin_revenue=ExpressionWrapper(
                Sum(F('total_amount')) * 0.1, 
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ) \
        .order_by('month')
    
    # Top Products by sales
    top_products = Product.objects.annotate(sales_count=Count('orderitem', distinct=True)) \
        .order_by('-sales_count')[:5]
    
    # Vendor Performance (Fixing potential join multiplication by using distinct=True)
    vendor_performance = User.objects.filter(role='VENDOR') \
        .annotate(
            product_count=Count('products', distinct=True), 
            sale_count=Count('products__orderitem', distinct=True)
        ) \
        .order_by('-sale_count')[:5]
        
    return render(request, 'admin_panel/reports.html', {
        'monthly_revenue': monthly_revenue,
        'top_products': top_products,
        'vendor_performance': vendor_performance
    })

# --- Contact Messages ---
@user_passes_test(admin_required, login_url='admin_panel:login')
def contact_messages_list(request):
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/contact_messages.html', {'messages_list': messages_list})

@user_passes_test(admin_required, login_url='admin_panel:login')
def contact_message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, "Contact message deleted successfully.")
    return redirect('admin_panel:contact_messages')
