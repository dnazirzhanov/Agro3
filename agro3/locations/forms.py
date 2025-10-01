from django import forms
from .models import Country, Region, City


class LocationWidget(forms.MultiWidget):
    """Custom widget for hierarchical location selection"""
    
    def __init__(self, attrs=None):
        widgets = [
            forms.Select(attrs={'class': 'form-select location-country', 'data-target': 'region'}),
            forms.Select(attrs={'class': 'form-select location-region', 'data-target': 'city', 'disabled': True}),
            forms.Select(attrs={'class': 'form-select location-city', 'disabled': True}),
        ]
        super().__init__(widgets, attrs)
    
    def decompress(self, value):
        if value:
            # If value is a City object or ID
            if hasattr(value, 'region'):
                city = value
                return [city.region.country.id, city.region.id, city.id]
            elif isinstance(value, (int, str)):
                try:
                    city = City.objects.select_related('region__country').get(id=value)
                    return [city.region.country.id, city.region.id, city.id]
                except City.DoesNotExist:
                    pass
        return [None, None, None]


class LocationField(forms.MultiValueField):
    """Custom field for hierarchical location selection"""
    
    def __init__(self, *args, **kwargs):
        fields = [
            forms.ModelChoiceField(
                queryset=Country.objects.all(),
                empty_label="Select Country",
                required=False
            ),
            forms.ModelChoiceField(
                queryset=Region.objects.none(),
                empty_label="Select Region/State",
                required=False
            ),
            forms.ModelChoiceField(
                queryset=City.objects.none(), 
                empty_label="Select City/Village",
                required=False
            ),
        ]
        
        kwargs['widget'] = LocationWidget()
        kwargs['require_all_fields'] = False
        super().__init__(fields, *args, **kwargs)
    
    def compress(self, data_list):
        """Return the City object if all fields are provided"""
        if data_list and data_list[2]:  # If city is selected
            return data_list[2]  # Return the City object
        return None


class LocationForm(forms.Form):
    """Standalone form for location selection"""
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        empty_label="Select Country",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_country'})
    )
    
    region = forms.ModelChoiceField(
        queryset=Region.objects.none(),
        empty_label="Select Region/State/Oblast", 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_region', 'disabled': True})
    )
    
    city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        empty_label="Select or type City/Village/Town",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_city', 'disabled': True})
    )
    
    custom_location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Or type your village/town name',
            'id': 'id_custom_location'
        }),
        help_text="If your location is not in the list, you can type it here"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If form has data, populate dependent fields
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['region'].queryset = Region.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass
        
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['city'].queryset = City.objects.filter(region_id=region_id).order_by('name')
            except (ValueError, TypeError):
                pass