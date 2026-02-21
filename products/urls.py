from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.StorefrontHomeView.as_view(), name='home'),
    path('vendor/dashboard/', views.VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('vendor/orders/', views.VendorOrderListView.as_view(), name='vendor_orders'),
    path('vendor/orders/update/<int:item_id>/', views.update_order_item_status, name='update_order_item_status'),
    path('product/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('product/<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('product/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('product/<slug:slug>/toggle-status/', views.toggle_product_status, name='product_toggle_status'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/', views.CategoryProductListView.as_view(), name='category_products'),
    path('shop/', views.ShopListView.as_view(), name='all_products'),

    path('about/', views.AboutUsView.as_view(), name='about'),
    path('contact/', views.ContactUsView.as_view(), name='contact_us'),
    path('become-vendor/', views.BecomeVendorView.as_view(), name='become_vendor'),
]
