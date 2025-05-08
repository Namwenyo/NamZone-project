from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class User(AbstractUser):
    class UserType(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        REGULAR = 'REGULAR', _('Regular User')
    
    # Namibia phone number validation
    phone_regex = RegexValidator(
        regex=r'^\+264\d{9}$',
        message="Phone number must be in format: '+264812345678' (12 digits total)"
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[phone_regex],
        unique=True
    )
    
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.REGULAR
    )

    # Required for custom user model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='marketplace_users',
        blank=True,
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='marketplace_users',
        blank=True,
        verbose_name='user permissions'
    )

    def __str__(self):
        return f"{self.username} ({self.phone_number})"

    @property
    def is_admin(self):
        return self.user_type == self.UserType.ADMIN or self.is_staff


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    APPROVAL_STATUS = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    status = models.CharField(max_length=1, choices=APPROVAL_STATUS, default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} (N${self.price})"

def clean(self):
    if self.seller and self.seller.user_type != User.UserType.REGULAR:
        raise ValidationError("Only regular users can list items.")

        
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a SellerProfile for each new regular User"""
    if created and not instance.is_superuser:
        SellerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the SellerProfile when regular User is saved"""
    if not instance.is_superuser:
        SellerProfile.objects.get_or_create(user=instance)      
            