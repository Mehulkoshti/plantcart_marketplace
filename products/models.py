from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Sub Categories"
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.name} -> {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ENVIRONMENT_CHOICES = (
        ('INDOOR', 'Indoor'),
        ('OUTDOOR', 'Outdoor'),
        ('BOTH', 'Both (Indoor & Outdoor)'),
    )
    environment = models.CharField(max_length=20, choices=ENVIRONMENT_CHOICES, default='INDOOR')

    # Specialized Plant Details
    scientific_name = models.CharField(max_length=200, blank=True, null=True)
    care_level = models.CharField(max_length=50, choices=(
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Expert', 'Expert')
    ), default='Beginner')
    sunlight = models.CharField(max_length=100, choices=(
        ('Full Sun', 'Full Sun'),
        ('Bridge Light', 'Bright Indirect Light'),
        ('Partial Shade', 'Partial Shade'),
        ('Low Light', 'Low Light')
    ), default='Bright Indirect Light')
    watering = models.CharField(max_length=100, choices=(
        ('Frequent', 'Frequent (3-4 times/week)'),
        ('Moderate', 'Moderate (1-2 times/week)'),
        ('Occasional', 'Occasional (Every 2 weeks)'),
        ('Very Low', 'Very Low (Monthly)')
    ), default='Moderate')
    pet_safe = models.BooleanField(default=False)
    growth_rate = models.CharField(max_length=50, choices=(
        ('Slow', 'Slow'),
        ('Medium', 'Medium'),
        ('Fast', 'Fast')
    ), default='Medium')
    ideal_location = models.CharField(max_length=200, blank=True, null=True)
    maintenance_tips = models.TextField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user') # One review per user per product

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}*)"
