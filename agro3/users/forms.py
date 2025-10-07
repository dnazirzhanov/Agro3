from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import UserProfile
from locations.models import Country, Region, City


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form with additional fields"""
    email = forms.EmailField(required=True, help_text=_("Required for password reset and notifications"))
    first_name = forms.CharField(max_length=30, required=True, help_text=_("Your first name"))
    last_name = forms.CharField(max_length=30, required=True, help_text=_("Your last name"))
    
    # Override password fields with better help text
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_("Create a strong password with at least 8 characters")
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_("Enter the same password as above for verification")
    )
    phone_number = forms.CharField(max_length=20, required=True, help_text=_("Your contact phone number for other farmers to reach you"))
    whatsapp_number = forms.CharField(
        max_length=20, 
        required=False, 
        help_text=_("WhatsApp number for easy communication (optional)"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+996 XXX XXX XXX'})
    )
    same_as_phone = forms.BooleanField(
        required=False,
        initial=False,
        help_text=_("Check this if your WhatsApp number is the same as your phone number"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'same_as_phone'})
    )
    
    # Profile fields required during registration
    farmer_type = forms.ChoiceField(
        choices=UserProfile.FARMER_TYPE_CHOICES,
        required=True,
        help_text=_("What type of farmer are you?")
    )
    farming_experience = forms.ChoiceField(
        choices=UserProfile.EXPERIENCE_CHOICES,
        required=True,
        help_text=_("How many years of farming experience do you have?")
    )
    # Location fields - will be handled by JavaScript
    country = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=True,
        help_text=_("Select your country (required for connecting with local farmers)"),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_country'})
    )
    region = forms.ModelChoiceField(
        queryset=None,
        required=True,
        help_text=_("Select your region/state/oblast (required for local farming network)"),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_region', 'disabled': True})
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        help_text=_("Enter your city/village/town (recommended for finding nearby farmers)"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your city or village')})
    )
    avatar_choice = forms.ChoiceField(
        choices=[('farmer_man_1', '👨‍🌾'), ('farmer_woman_1', '👩‍🌾'), ('default', 'default_user')],
        required=False,
        initial='default',
        help_text=_("Choose your profile avatar")
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show the specific countries we support
        supported_countries = ['US', 'KG', 'UZ', 'TJ', 'RU']
        self.fields['country'].queryset = Country.objects.filter(
            code__in=supported_countries
        ).order_by('code')
        self.fields['region'].queryset = Region.objects.none()
        self.fields['country'].empty_label = _("-- Select Country --")
        self.fields['region'].empty_label = _("-- Select Region --")
        # If form has data, populate dependent fields
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['region'].queryset = Region.objects.filter(country_id=country_id).order_by('name')
                self.fields['region'].widget.attrs.pop('disabled', None)
            except (ValueError, TypeError):
                pass
        # Region handling for dependent dropdown
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['region'].queryset = Region.objects.filter(country_id=self.data.get('country')).order_by('name')
                self.fields['region'].widget.attrs.pop('disabled', None)
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
                    'village_or_address': self.cleaned_data.get('city', '').strip(),
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
                profile.village_or_address = self.cleaned_data.get('city', '').strip()
                profile.avatar_choice = self.cleaned_data.get('avatar_choice', 'default')
                profile.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'phone_number', 'date_of_birth', 'avatar', 'avatar_choice', 'bio',
            'country', 'region_new', 'village_or_address', 'farmer_type',
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


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form that requires both username and email"""
    
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text=_("Enter your username"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your username'),
            'autocomplete': 'username'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update email field styling
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Enter your email address'),
            'autocomplete': 'email'
        })
        self.fields['email'].help_text = _("Enter the email address associated with your account")
    
    def clean(self):
        """Validate that username and email match an existing user"""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        
        if username and email:
            try:
                # Check if user exists with both username and email
                user = User.objects.get(username=username, email=email)
                
                # Check if user is active
                if not user.is_active:
                    raise forms.ValidationError(
                        _("This account has been deactivated. Please contact support.")
                    )
                
                # Store the validated user
                self._validated_user = user
                
            except User.DoesNotExist:
                raise forms.ValidationError(
                    _("No account found with this username and email combination. "
                      "Please check your credentials and try again.")
                )
        
        return cleaned_data
    
    def get_users(self, email):
        """Return the user that matches the username and email"""
        # If we have a validated user from clean(), return it
        if hasattr(self, '_validated_user') and self._validated_user:
            if self._validated_user.email.lower() == email.lower():
                yield self._validated_user
        else:
            # Fallback to parent behavior, but with additional username check
            username = self.cleaned_data.get('username') if hasattr(self, 'cleaned_data') else None
            if username:
                # Only return users that match both username and email
                active_users = User._default_manager.filter(
                    email__iexact=email,
                    username=username,
                    is_active=True
                )
                for user in active_users:
                    yield user