from django.test import TestCase, Client
from django.urls import reverse


class DoseCalculatorTests(TestCase):
    """Tests for the dose calculator functionality."""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('pests_diseases:dose_calculator')
    
    def test_calculator_page_loads(self):
        """Test that the calculator page loads successfully."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chemical Dose Calculator')
    
    def test_calculator_calculation(self):
        """Test that the calculator performs correct calculations."""
        response = self.client.post(self.url, {
            'dose_per_liter': '10',
            'total_liters': '560'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '5600.0')
    
    def test_calculator_with_decimal_values(self):
        """Test calculator with decimal values."""
        response = self.client.post(self.url, {
            'dose_per_liter': '12.5',
            'total_liters': '400'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '5000.0')
    
    def test_calculator_with_invalid_input(self):
        """Test calculator handles invalid input gracefully."""
        response = self.client.post(self.url, {
            'dose_per_liter': 'invalid',
            'total_liters': '560'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter valid numbers')
    
    def test_calculator_empty_form(self):
        """Test calculator with empty form submission."""
        response = self.client.post(self.url, {
            'dose_per_liter': '',
            'total_liters': ''
        })
        self.assertEqual(response.status_code, 200)
        # Should not crash, just show no result
    
    def test_calculator_url_in_navigation(self):
        """Test that calculator link is accessible from navigation."""
        response = self.client.get(reverse('pests_diseases:list'))
        self.assertEqual(response.status_code, 200)
