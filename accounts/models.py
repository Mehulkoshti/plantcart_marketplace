from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

# ✅ Step 1: Custom Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)

    # 👇 required for authenticate
    def get_by_natural_key(self, username):
        return self.get(email=username)


# ✅ Step 2: Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(
        max_length=20,
        choices=(
            ('ADMIN', 'Admin'),
            ('VENDOR', 'Vendor'),
            ('CUSTOMER', 'Customer'),
        ),
        default='CUSTOMER'
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False) # For Vendors

    # Shop Details
    shop_name = models.CharField(max_length=100, blank=True, null=True)
    shop_address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Advanced Vendor Details
    shop_license = models.CharField(max_length=100, blank=True, null=True)
    business_type = models.CharField(max_length=50, choices=(
        ('INDIVIDUAL', 'Individual'),
        ('RETAILER', 'Retailer'),
        ('NURSERY', 'Nursery/Plantation')
    ), blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0, blank=True, null=True)
    identity_proof_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Identity Proof (AADHAR/PAN)")
    shop_image = models.ImageField(upload_to='shops/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # ✅ Link custom manager
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    # ✅ Property for full name
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
