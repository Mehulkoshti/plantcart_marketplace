from django import forms
from .models import Product, Category, SubCategory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'subcategory', 'name', 'scientific_name', 'price', 'stock',
            'image', 'environment', 'description', 'care_level', 'sunlight', 'watering',
            'pet_safe', 'growth_rate', 'ideal_location', 'maintenance_tips', 'benefits', 'is_active'
        ]
        widgets = {
            'environment': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your plant...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock Quantity'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'scientific_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Botanical Name'}),
            'care_level': forms.Select(attrs={'class': 'form-select'}),
            'sunlight': forms.Select(attrs={'class': 'form-select'}),
            'watering': forms.Select(attrs={'class': 'form-select'}),
            'pet_safe': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'growth_rate': forms.Select(attrs={'class': 'form-select'}),
            'ideal_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Balcony, Living Room'}),
            'maintenance_tips': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tips for keeping this plant healthy...'}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Air Purifying, Low Maintenance, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show all subcategories grouped by category
        self.fields['subcategory'].queryset = SubCategory.objects.select_related('category').order_by('category__name', 'name')
        self.fields['subcategory'].empty_label = "— Select a Sub-Category —"

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Auto-assign the category from the chosen subcategory
        if instance.subcategory:
            instance.category = instance.subcategory.category
        if commit:
            instance.save()
        return instance
