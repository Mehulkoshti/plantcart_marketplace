from .models import Category
from cart.models import Wishlist

def category_context(request):
    return {
        'all_categories': Category.objects.prefetch_related('subcategories').all()
    }

def wishlist_context(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        return {
            'wishlist_count': wishlist_items.count(),
            'wishlisted_product_ids': wishlist_items.values_list('product_id', flat=True)
        }
    return {
        'wishlist_count': 0,
        'wishlisted_product_ids': []
    }
