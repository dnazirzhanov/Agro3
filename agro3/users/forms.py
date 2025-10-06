from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from locations.models import Country, Region, City
from locations.models import Country, Region, City


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form with additional fields"""
    email = forms.EmailField(required=True, help_text="Required for password reset and notifications")
    first_name = forms.CharField(max_length=30, required=True, help_text="Your first name")
    last_name = forms.CharField(max_length=30, required=True, help_text="Your last name")
    phone_number = forms.CharField(max_length=20, required=True, help_text="Your contact phone number for other farmers to reach you")
    whatsapp_number = forms.CharField(
        max_length=20, 
        required=False, 
        help_text="WhatsApp number for easy communication (optional)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+996 XXX XXX XXX'})
    )
    same_as_phone = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Check this if your WhatsApp number is the same as your phone number",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'same_as_phone'})
    )
    
    # Profile fields required during registration
    farmer_type = forms.ChoiceField(
        choices=UserProfile.FARMER_TYPE_CHOICES,
        required=True,
        help_text="What type of farmer are you?"
    )
    farming_experience = forms.ChoiceField(
        choices=UserProfile.EXPERIENCE_CHOICES,
        required=True,
        help_text="How many years of farming experience do you have?"
    )
    # Location fields - will be handled by JavaScript
    country = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=True,
        help_text={
            'en': "Select your country (required)",
            'ru': "Выберите вашу страну (обязательно)",
            'ky': "Өлкөңүздү тандаңыз (милдеттүү)"
        },
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_country'})
    )
    region = forms.ModelChoiceField(
        queryset=None,
        required=True,
        help_text={
            'en': "Select your region/state/oblast (required)",
            'ru': "Регион/область тандаңыз (обязательно)",
            'ky': "Регионду/областы тандаңыз (милдеттүү)"
        },
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_region', 'disabled': True})
    )
    city = forms.ModelChoiceField(
        queryset=None,
        required=False,
        help_text={
            'en': "Select your city/village/town (recommended)",
            'ru': "Город/поселок тандаңыз (рекомендуется)",
            'ky': "Шаарды/айылды тандаңыз (сунушталат)"
        },
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_city', 'disabled': True})
    )
    avatar_choice = forms.ChoiceField(
        choices=[('farmer_man_1', '👨‍🌾'), ('farmer_woman_1', '👩‍🌾'), ('default', 'default_user')],
        required=False,
        initial='default',
        help_text={
            'en': "Choose your avatar",
            'ru': "Аватарыңызды тандаңыз",
            'ky': "Аватарыңызды тандаңыз"
        }
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No prepopulated data in dropdowns
        self.fields['country'].queryset = Country.objects.all().order_by('name')
        self.fields['region'].queryset = Region.objects.none()
        self.fields['city'].queryset = City.objects.none()
        self.fields['country'].empty_label = None
        self.fields['region'].empty_label = None
        self.fields['city'].empty_label = None
        # If form has data, populate dependent fields
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['region'].queryset = Region.objects.filter(country_id=country_id).order_by('name')
                self.fields['region'].widget.attrs.pop('disabled', None)
            except (ValueError, TypeError):
                pass
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['city'].queryset = City.objects.filter(region_id=region_id).order_by('name')
                self.fields['city'].widget.attrs.pop('disabled', None)
            except (ValueError, TypeError):
                pass
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name in ['country', 'region', 'city']:
                continue  # These already have form-select class
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.help_text or field.label
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create or update UserProfile with registration data
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': self.cleaned_data['phone_number'],
                    'farmer_type': self.cleaned_data['farmer_type'],
                    'farming_experience': self.cleaned_data['farming_experience'],
                    'country': self.cleaned_data.get('country'),
                    'region_new': self.cleaned_data.get('region'),
                    'city': self.cleaned_data.get('city'),
                    'avatar_choice': self.cleaned_data.get('avatar_choice', 'default'),
                }
            )
            if not created:
                # Update existing profile
                profile.phone_number = self.cleaned_data['phone_number']
                profile.farmer_type = self.cleaned_data['farmer_type']
                profile.farming_experience = self.cleaned_data['farming_experience'] 
                profile.country = self.cleaned_data.get('country')
                profile.region_new = self.cleaned_data.get('region')
                profile.city = self.cleaned_data.get('city')
                profile.avatar_choice = self.cleaned_data.get('avatar_choice', 'default')
                profile.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'phone_number', 'date_of_birth', 'avatar', 'avatar_choice', 'bio',
            'country', 'region_new', 'city', 'village_or_address', 'farmer_type',
            'farming_experience', 'receive_notifications',
            'receive_market_alerts', 'preferred_language'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'


class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'