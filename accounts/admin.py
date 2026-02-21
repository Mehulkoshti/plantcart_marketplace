from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ContactMessage


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "id",
        "email",
        "full_name",
        "role",
        "is_approved",
        "is_staff",
        "is_active",
    )

    list_filter = ("role", "is_approved", "is_staff", "is_active")
    list_editable = ("is_approved",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role", "is_approved")}),
        ("Shop & Verification Details", {"fields": (
            "shop_name", "business_type", "shop_address", "phone_number", 
            "shop_license", "gst_number", "identity_proof_number", 
            "years_of_experience", "shop_image", "website_url"
        )}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "full_name",
                "role",
                "password1",
                "password2",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    search_fields = ("email", "full_name")
    ordering = ("email",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)
