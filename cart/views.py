from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import CartItem, Wishlist, Order, OrderItem
import stripe
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock <= 0:
        messages.error(request, f"Sorry, {product.name} is out of stock.")
        return redirect('products:product_detail', slug=product.slug)

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        if cart_item.quantity + 1 > product.stock:
             messages.warning(request, f"Cannot add more {product.name}. Only {product.stock} left in stock.")
        else:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"{product.name} quantity updated in cart.")
    else:
        messages.success(request, f"{product.name} added to your cart.")
    return redirect('cart:cart_view')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    return render(request, 'cart/cart_view.html', {'cart_items': cart_items, 'total': total})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('cart:cart_view')

@login_required
def update_cart_quantity(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, "Item removed from cart.")
    return redirect('cart:cart_view')

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
    if wishlist_item.exists():
        wishlist_item.delete()
        messages.info(request, f"{product.name} removed from wishlist.")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, f"{product.name} added to wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'products:home'))

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'cart/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('products:home')

    # Stock Validation
    for item in cart_items:
        if item.product.stock < item.quantity:
            messages.error(request, f"Sorry, {item.product.name} only has {item.product.stock} items left in stock. Please adjust your cart.")
            return redirect('cart:cart_view')
    
    total = sum(item.total_price for item in cart_items)
    
    client_secret = None
    STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Create PaymentIntent for online payment setup
    if request.user.is_authenticated:
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),
                currency='inr',
                metadata={'user_id': request.user.id},
                automatic_payment_methods={'enabled': True},
            )
            client_secret = intent.client_secret
        except Exception as e:
            messages.error(request, str(e))

    if request.method == 'POST':
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        create_order_only = request.POST.get('create_order_only') == 'true'

        # If it's an AJAX request to create order before Stripe payment
        if create_order_only and payment_method == 'online':
            try:
                order = Order.objects.create(
                    user=request.user, 
                    total_amount=total, 
                    address=address, 
                    status='PENDING_PAYMENT'
                )
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    # We DO NOT reduce stock here yet, or we DO? 
                    # Usually stock is reserved. Let's reduce it.
                    # If payment fails, we might need to restore it (future improvement)
                    item.product.stock -= item.quantity
                    item.product.save()
                    item.delete()
                
                from django.http import JsonResponse
                return JsonResponse({'status': 'success', 'order_id': order.id})
            except Exception as e:
                from django.http import JsonResponse
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        # Standard POST (COD)
        status = 'PENDING'
        order = Order.objects.create(user=request.user, total_amount=total, address=address, status=status)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()
            item.delete()
            
        messages.success(request, "Order placed successfully!")
        return redirect('cart:order_success', order_id=order.id)
        
    # Get saved addresses for selection
    saved_addresses = request.user.addresses.all()
    default_address = saved_addresses.filter(is_default=True).first()

    return render(request, 'cart/checkout.html', {
        'cart_items': cart_items, 
        'total': total, 
        'client_secret': client_secret,
        'STRIPE_PUBLIC_KEY': STRIPE_PUBLIC_KEY,
        'saved_addresses': saved_addresses,
        'default_address': default_address
    })

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'cart/order_success.html', {'order': order})

@login_required
def payment_success(request):
    payment_intent_id = request.GET.get('payment_intent')
    payment_client_secret = request.GET.get('payment_intent_client_secret')
    address = request.GET.get('address')
    
    if not payment_intent_id or not payment_client_secret:
        messages.error(request, "Invalid payment confirmation.")
        return redirect('cart:checkout')

    # Retrieve the PaymentIntent to verify status
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status == 'succeeded':
            # Find the pending order for this user
            # In a real app, we might store order_id in metadata or session to be precise
            # For now, we look for the most recent PENDING_PAYMENT order
            order = Order.objects.filter(user=request.user, status='PENDING_PAYMENT').last()
            
            if order:
                order.status = 'PROCESSING'
                order.save()
                messages.success(request, "Payment successful! Your order has been placed.")
                return redirect('cart:order_success', order_id=order.id)
            else:
                 # Fallback if order creation failed or race condition
                 # In this flow, order is created in checkout POST before JS confirm
                 messages.warning(request, "Payment succeeded but order not found. Please contact support.")
                 return redirect('products:home')
        else:
            messages.warning(request, f"Payment status: {intent.status}")
            return redirect('cart:checkout')
            
    except Exception as e:
        messages.error(request, f"Error verifying payment: {str(e)}")
        return redirect('cart:checkout')

@login_required
def payment_cancel(request):
    messages.warning(request, "Payment was cancelled. Your cart items are saved.")
    return redirect('cart:checkout')

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cart/user_orders.html', {'orders': orders})
