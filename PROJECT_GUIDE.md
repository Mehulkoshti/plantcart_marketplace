# 🌿 PlantCart: Comprehensive Project Guide

Welcome to the **PlantCart** project documentation. This guide provides a detailed overview of the marketplace architecture, user roles, technical features, and system workflows.

---

## 1. Project Overview
PlantCart is a premium, multi-vendor e-commerce marketplace specifically designed for plant enthusiasts and nurseries. It features a "God-Level" premium aesthetic, glassmorphism UI elements, and a mobile-first responsive design.

---

## 2. User Roles & Permissions

The platform supports three distinct user roles, each with specific capabilities:

### 👤 Customer (Buyer)
The primary user of the platform.
- **Browsing**: Explore the home page, shop catalog, and category-specific listings.
- **Engagement**: Add products to a personal **Wishlist** for later.
- **Shopping**: Manage a dynamic **Shopping Cart** (add/remove/update quantities).
- **Checkout**: Place orders using **Online Payment (Stripe)** or **Cash on Delivery (COD)**.
- **Orders**: Track order history and current status (Pending, processing, etc.).
- **Profile**: Manage personal account details and shipping addresses.

### 🏪 Vendor (Seller)
Verified sellers or nurseries who manage their own micro-shops.
- **Onboarding**: Register with advanced details (License, GST, Website, Experience).
- **Approval**: Vendors must be approved by an Admin (`is_approved`) before they can list products.
- **Dashboard**: A dedicated workspace to see active products and recent sales.
- **Product Management**: Full CRUD (Create, Read, Update, Delete) for their own plants.
- **Order Management**: Track and update the status (Shipped, Delivered, etc.) of individual order items sold from their shop.

### 🛡️ Admin (Superuser)
System administrators who manage the overall platform.
- **Oversight**: Full access to the Django Admin panel at `/admin/`.
- **User Management**: Approve/Suspend vendors and manage customer accounts.
- **Content Management**: Create/Edit global **Categories** and **Subcategories**.
- **System Health**: Monitor all transactions and site-wide messages.

---

## 3. Core Features & Technical Stack

### 💻 Technology Stack
- **Backend**: Python 3.11+ / Django 4.2.
- **Frontend**: HTML5, CSS3 (Vanilla + Custom Premium Variables), Bootstrap 5.3.
- **Icons**: Font Awesome 6.
- **Database**: MySQL (Development).
- **Payment**: **Stripe API** (Online Card & UPI payments).

### 💳 Stripe Integration (Online Payments)
PlantCart uses a sophisticated checkout flow:
1. **PaymentIntent**: Created on the server-side as soon as a user reaches the checkout page.
2. **AJAX Order Creation**: Before the Stripe payment is finalized, the system creates a `PENDING_PAYMENT` order via AJAX to ensure no data is lost during transit.
3. **Stock Management**: Inventory is automatically reduced upon successful payment verification.
4. **Security**: Uses CSRF protection and Stripe's secure `confirmPayment` client-side JS.

### 🔍 Search & Discovery
- **Dynamic Filters**: Sort by "Price: Low to High", "Price: High to Low", or "Newest First".
- **Category Hierarchy**: Deep organization with Categories (e.g., Indoor Plants) and Subcategories (e.g., Succulents).
- **Plant Concierge**: Detailed plant profiles including Scientific Name, Sunlight requirements, Watering frequency, and Pet-safety status.

---

## 4. Page Guide (Sitemap)

| Page | URL Pattern | Description |
| :--- | :--- | :--- |
| **Home** | `/` | Hero section, Category grid, and Best Sellers. |
| **Shop** | `/shop/` | Main product catalog with category and price sorting. |
| **Category View** | `/category/<slug>/` | Filtered products belonging to a specific category. |
| **Product Detail** | `/product/<slug>/` | Full care instructions, maintenance tips, and vendor info. |
| **Vendor Dashboard** | `/dashboard/` | Private area for Sellers to manage inventory. |
| **Vendor Orders** | `/vendor/orders/` | List of items sold by the vendor with status toggles. |
| **Cart** | `/cart/` | Itemized summary with quantity controls. |
| **Checkout** | `/cart/checkout/` | Shipping address entry and payment gateway. |
| **My Orders** | `/accounts/orders/` | Customer's order history and status tracking. |
| **Profile** | `/accounts/profile/` | Role-based user settings. |

---

## 5. Design Aesthetics
The project follows a **Premium/Elite design system**:
- **Typography**: Uses modern, readable fonts with tracking-wider headers.
- **Colors**: Deep Forest Green (`#0F3D2E`) and Fresh Leaf Green (`#3FA34D`).
- **Cards**: Soft-rounded edges (28px - 32px) with subtle luxury shadows.
- **Glassmorphism**: Transparent, blurred backgrounds for navbars and modal elements.
- **Mobile Optimizations**: 1-column product grids on mobile for high-impact imagery.

---

## 6. How to Run & Setup
For a detailed step-by-step guide on how to set up this project on a **New PC**, please refer to the dedicated guide:

👉 **[NEW_PC_SETUP_GUIDE.md](file:///d:/plant_marketplace/NEW_PC_SETUP_GUIDE.md)**

### Quick Start:
1. **Environment**: `python -m venv venv`
2. **Dependencies**: `pip install -r requirements.txt`
3. **Database**: Create MySQL DB `plant_marketplace_db` and run `python manage.py migrate`.
4. **Admin**: `python manage.py createsuperuser`.
5. **Start**: `python manage.py runserver`.
