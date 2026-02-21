from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ContactMessage

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=(('VENDOR', 'Vendor'), ('CUSTOMER', 'Customer')), widget=forms.RadioSelect)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "email", "first_name", "last_name", "role", 
            "shop_name", "shop_address", "phone_number", 
            "business_type", "shop_license", "gst_number", "website_url",
            "years_of_experience", "identity_proof_number", "shop_image"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs['class'] = 'form-control'


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'placeholder': 'How can we help you?', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'shop_name', 'shop_address', 
            'phone_number', 'business_type', 'shop_license', 
            'gst_number', 'website_url', 'years_of_experience', 
            'identity_proof_number', 'shop_image'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
