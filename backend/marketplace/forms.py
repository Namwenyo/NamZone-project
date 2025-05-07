
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import User, Item, Category
import re
from .models import SellerProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full border p-2 rounded',
            'placeholder': 'example@email.com',
            'autocomplete': 'email'
        }),
        help_text="Required. Enter a valid email address."
    )
    
    phone_number = forms.CharField(  # Changed from 'phone' to match model
        required=True,  # Changed from False to True
        widget=forms.TextInput(attrs={
            'class': 'w-full border p-2 rounded',
            'placeholder': '+264811234567',  # Removed spaces for better pattern matching
            'autocomplete': 'tel'
        }),
        help_text="Required. Namibian format: +264812345678",
        validators=[
            RegexValidator(
                regex=r'^\+264\d{9}$',  # Stricter pattern for Namibia
                message="Phone number must be in format: '+264811234567'. 12 digits starting with +264."
            )
        ]
    )
    

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')  # Updated to phone_number
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Field customizations
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Choose a username',
            'minlength': '4',
            'maxlength': '30'
        })
        self.fields['username'].help_text = "Required. 4-30 characters. Letters, digits and @/./+/-/_ only."
        
        for field in ['password1', 'password2']:
            self.fields[field].widget.attrs.update({
                'placeholder': '••••••••',
                'minlength': '8'
            })
        
        self.fields['password1'].help_text = """
            <ul class="list-disc pl-5 mt-1 text-xs">
                <li>At least 8 characters</li>
                <li>Not entirely numeric</li>
                <li>Not too common</li>
            </ul>
        """

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("This phone number is already registered.")
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise ValidationError(
                "Username can only contain letters, numbers and @/./+/-/_ characters."
            )
        return username

class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show active categories
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        
        # Add Tailwind classes to all fields
        for field_name, field in self.fields.items():
            base_classes = 'w-full border p-2 rounded'
            
            if field_name == 'description':
                field.widget.attrs.update({
                    'class': f'{base_classes} h-32',
                    'rows': 4
                })
            elif field_name == 'image':
                field.widget.attrs.update({
                    'class': f'{base_classes} p-1',
                    'accept': 'image/*'
                })
            else:
                field.widget.attrs.update({
                    'class': base_classes
                })
                
            if field_name == 'price':
                field.widget.attrs.update({
                    'min': '0.01',
                    'step': '0.01',
                    'placeholder': '0.00'
                })

    class Meta:
        model = Item
        fields = ['title', 'category', 'description', 'price', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter item title',
                'minlength': '10',
                'maxlength': '200'
            }),
            'category': forms.Select(attrs={
                'placeholder': 'Select category'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your item in detail',
                'minlength': '20'
            }),
            'price': forms.NumberInput(),
            'image': forms.ClearableFileInput(attrs={
                'aria-label': 'Upload item image'
            }),
        }
        labels = {
            'image': 'Item Image',
            'price': 'Price (N$)'
        }
        help_texts = {
            'title': 'Clear, descriptive titles work best (10-200 characters)',
            'description': 'Include details like condition, features, and reason for selling (minimum 20 characters)',
            'image': 'Upload a clear photo of your item (max 5MB)'
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise ValidationError("Title must be at least 10 characters long.")
        return title.strip()

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 20:
            raise ValidationError("Description must be at least 20 characters long.")
        return description.strip()

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError("Price must be greater than zero.")
        return round(price, 2)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("Image size must be less than 5MB.")
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                raise ValidationError("Only JPG, PNG, or WEBP images are allowed.")
        return image

class SellerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = SellerProfile.objects.get(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.email = self.cleaned_data['email']
            profile.save()
            
            # Set password properly
            user.set_password(self.cleaned_data['password1'])
            user.save()
        return user   