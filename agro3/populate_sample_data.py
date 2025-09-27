#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/workspaces/Agro3/agro3')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agro_main.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from forum.models import Category, Tag, BlogPost, Comment
from crops.models import SoilType, Crop
from market.models import Product, Market, MarketPrice
from pests_diseases.models import PestOrDisease

User = get_user_model()

def populate_sample_data():
    print("Creating sample data...")
    
    # Get admin user
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("Admin user not found. Creating one...")
        admin_user = User.objects.create_superuser('admin', 'admin@agro3.com', 'admin123')
    
    # Create categories
    general_cat, created = Category.objects.get_or_create(
        name="General Discussion",
        defaults={
            'description': 'General farming topics and discussions',
            'color': '#007bff'
        }
    )
    
    crops_cat, created = Category.objects.get_or_create(
        name="Crop Management",
        defaults={
            'description': 'Topics about crop cultivation and management',
            'color': '#28a745'
        }
    )
    
    market_cat, created = Category.objects.get_or_create(
        name="Market & Prices",
        defaults={
            'description': 'Market prices and trading discussions',
            'color': '#ffc107'
        }
    )
    
    # Create tags
    intro_tag, created = Tag.objects.get_or_create(name="intro")
    tips_tag, created = Tag.objects.get_or_create(name="tips")
    question_tag, created = Tag.objects.get_or_create(name="question")
    season_tag, created = Tag.objects.get_or_create(name="seasonal")
    
    # Create blog posts
    welcome_post, created = BlogPost.objects.get_or_create(
        title="Welcome to Batken Agri-Helper Community",
        defaults={
            'author': admin_user,
            'category': general_cat,
            'short_description': 'A warm welcome to all farmers joining our community platform.',
            'content': '''
            <h2>Welcome to Our Community!</h2>
            <p>We're excited to have you join the Batken Agri-Helper community platform. This is a space where farmers, agricultural experts, and enthusiasts can come together to share knowledge, ask questions, and support each other.</p>
            
            <h3>What You Can Do Here:</h3>
            <ul>
                <li><strong>Ask Questions:</strong> Need help with crop diseases, soil issues, or market prices? Ask away!</li>
                <li><strong>Share Experience:</strong> Share your farming success stories and techniques</li>
                <li><strong>Get Expert Advice:</strong> Our agricultural experts are here to help</li>
                <li><strong>Stay Updated:</strong> Learn about the latest farming techniques and market trends</li>
            </ul>
            
            <p>Let's grow together and make farming in Batken region more productive and sustainable!</p>
            ''',
            'is_featured': True
        }
    )
    
    if created:
        welcome_post.tags.add(intro_tag)
    
    # Winter farming tips post
    winter_post, created = BlogPost.objects.get_or_create(
        title="Winter Farming Tips for Batken Region",
        defaults={
            'author': admin_user,
            'category': crops_cat,
            'short_description': 'Essential tips for successful winter farming in harsh continental climate.',
            'content': '''
            <h2>Preparing for Winter Farming</h2>
            <p>Winter farming in Batken region requires special preparation due to our continental climate with cold winters and hot summers.</p>
            
            <h3>Key Winter Crops for Our Region:</h3>
            <ul>
                <li><strong>Winter Wheat:</strong> Plant in September-October, harvest in July</li>
                <li><strong>Winter Barley:</strong> Good for animal feed and brewing</li>
                <li><strong>Garlic:</strong> Plant in October for summer harvest</li>
            </ul>
            
            <h3>Soil Preparation:</h3>
            <p>Before winter planting, ensure your soil has good drainage. Heavy clay soils in our region need organic matter added to prevent waterlogging during spring thaw.</p>
            
            <h3>Climate Considerations:</h3>
            <p>Our region experiences temperatures from -20°C in winter to +40°C in summer. Choose hardy varieties that can withstand these extremes.</p>
            ''',
            'is_featured': False
        }
    )
    
    if created:
        winter_post.tags.add(tips_tag, season_tag)
    
    # Market price discussion post
    market_post, created = BlogPost.objects.get_or_create(
        title="Understanding Local Market Prices - Spring 2024",
        defaults={
            'author': admin_user,
            'category': market_cat,
            'short_description': 'Analysis of current market trends and pricing for major crops in Batken.',
            'content': '''
            <h2>Current Market Situation</h2>
            <p>The agricultural market in Batken has seen significant changes in 2024. Here's what farmers need to know:</p>
            
            <h3>Grain Prices:</h3>
            <ul>
                <li><strong>Wheat:</strong> 25-30 som/kg (up from last year)</li>
                <li><strong>Barley:</strong> 20-25 som/kg</li>
                <li><strong>Corn:</strong> 22-28 som/kg</li>
            </ul>
            
            <h3>Vegetable Prices:</h3>
            <ul>
                <li><strong>Potatoes:</strong> 15-20 som/kg</li>
                <li><strong>Onions:</strong> 18-25 som/kg</li>
                <li><strong>Carrots:</strong> 20-30 som/kg</li>
            </ul>
            
            <h3>Market Tips:</h3>
            <p>Best times to sell are usually Tuesday and Saturday market days. Avoid selling during harvest season when prices drop due to oversupply.</p>
            ''',
            'is_featured': False
        }
    )
    
    if created:
        market_post.tags.add(tips_tag)
    
    # Create some sample soil types
    loamy_soil, created = SoilType.objects.get_or_create(
        name="Loamy Soil",
        defaults={
            'description': 'Well-balanced soil with good drainage and nutrient retention, common in valley areas',
            'texture': 'Loamy',
            'drainage': 'Good',
            'nutrient_retention': 'Excellent',
            'recommended_amendments': 'Regular compost addition to maintain organic matter levels'
        }
    )
    
    clay_soil, created = SoilType.objects.get_or_create(
        name="Clay Soil",
        defaults={
            'description': 'Heavy soil that retains water well but may have drainage issues in spring',
            'texture': 'Clay',
            'drainage': 'Poor',
            'nutrient_retention': 'Very Good',
            'recommended_amendments': 'Add sand, compost, and organic matter to improve drainage and structure'
        }
    )
    
    sandy_soil, created = SoilType.objects.get_or_create(
        name="Sandy Soil",
        defaults={
            'description': 'Light soil with excellent drainage but requires more frequent watering',
            'texture': 'Sandy',
            'drainage': 'Excellent',
            'nutrient_retention': 'Poor',
            'recommended_amendments': 'Add compost and organic matter to improve water and nutrient retention'
        }
    )
    
    # Create sample crops
    wheat_crop, created = Crop.objects.get_or_create(
        name="Winter Wheat (Batken Variety)",
        defaults={
            'scientific_name': 'Triticum aestivum',
            'description': 'Hardy winter wheat variety adapted to Batken continental climate conditions',
            'sunlight_needs': 'Full Sun',
            'water_needs': 'Medium',
            'soil_preference': loamy_soil,
            'climate_preference': 'Continental climate with cold winters and hot summers',
            'planting_seasons': 'September to October',
            'harvest_time': 'July to August',
            'nutrient_needs': 'High nitrogen, medium phosphorus and potassium',
            'recommended_usage': 'Bread making, flour production, livestock feed'
        }
    )
    
    barley_crop, created = Crop.objects.get_or_create(
        name="Spring Barley",
        defaults={
            'scientific_name': 'Hordeum vulgare',
            'description': 'Six-row spring barley suitable for animal feed and brewing',
            'sunlight_needs': 'Full Sun',
            'water_needs': 'Low to Medium',
            'soil_preference': clay_soil,
            'climate_preference': 'Tolerates drought and temperature variations',
            'planting_seasons': 'March to April',
            'harvest_time': 'July to August',
            'nutrient_needs': 'Medium nitrogen, phosphorus, and potassium',
            'recommended_usage': 'Animal feed, malting, brewing'
        }
    )
    
    # Create market data
    central_market, created = Market.objects.get_or_create(
        name="Batken Central Bazaar",
        defaults={
            'location': 'Batken City Center, near the main mosque',
            'description': 'Main agricultural market serving Batken city and surrounding villages',
            'contact_info': 'Phone: +996 (3622) 5-12-34, Open: Tue, Thu, Sat 6:00-18:00'
        }
    )
    
    village_market, created = Market.objects.get_or_create(
        name="Kyzyl-Kiya Agricultural Market",
        defaults={
            'location': 'Kyzyl-Kiya town center',
            'description': 'Regional market serving southern Batken oblast',
            'contact_info': 'Phone: +996 (3632) 4-56-78, Open: Wed, Fri, Sun 7:00-17:00'
        }
    )
    
    # Create sample products
    wheat_product, created = Product.objects.get_or_create(
        name="Wheat",
        defaults={
            'category': 'Grains',
            'description': 'Various wheat varieties and grades'
        }
    )
    
    barley_product, created = Product.objects.get_or_create(
        name="Barley",
        defaults={
            'category': 'Grains', 
            'description': 'Feed barley and malting barley'
        }
    )
    
    potato_product, created = Product.objects.get_or_create(
        name="Potatoes",
        defaults={
            'category': 'Vegetables',
            'description': 'Table potatoes and seed potatoes'
        }
    )
    
    # Create some sample pests/diseases
    aphid_pest, created = PestOrDisease.objects.get_or_create(
        name="Grain Aphid",
        defaults={
            'scientific_name': 'Sitobion avenae',
            'type': 'Pest',
            'symptoms': 'Yellowing leaves, sticky honeydew, curled leaves, reduced grain filling caused by aphid feeding',
            'causes': 'Warm weather, over-fertilizing with nitrogen, lack of natural predators',
            'identification_tips': 'Look for small green/black insects on leaves and stems, sticky honeydew substance',
            'prevention_methods': 'Encourage beneficial insects like ladybugs, avoid over-fertilizing with nitrogen, monitor crops regularly',
            'management_strategies': 'Use insecticidal soap, introduce ladybugs, apply neem oil, or use targeted insecticides if severe infestation'
        }
    )
    
    rust_disease, created = PestOrDisease.objects.get_or_create(
        name="Wheat Leaf Rust",
        defaults={
            'scientific_name': 'Puccinia triticina',
            'type': 'Disease',
            'symptoms': 'Orange-red pustules on leaf surface, yellowing and browning of leaves, premature leaf death',
            'causes': 'Fungal spores spread by wind, high humidity, moderate temperatures (15-25°C)',
            'identification_tips': 'Orange-red pustules scattered on upper leaf surfaces, spores rub off easily',
            'prevention_methods': 'Plant resistant varieties, ensure good air circulation, avoid overhead irrigation, crop rotation',
            'management_strategies': 'Apply fungicide sprays early in season, remove infected plant debris, use resistant wheat varieties'
        }
    )
    
    print("\n=== Sample Data Creation Complete! ===")
    print(f"✓ Categories created: {Category.objects.count()}")
    print(f"✓ Tags created: {Tag.objects.count()}")
    print(f"✓ Blog posts created: {BlogPost.objects.count()}")
    print(f"✓ Soil types created: {SoilType.objects.count()}")
    print(f"✓ Crops created: {Crop.objects.count()}")
    print(f"✓ Markets created: {Market.objects.count()}")
    print(f"✓ Products created: {Product.objects.count()}")
    print(f"✓ Pests/Diseases created: {PestOrDisease.objects.count()}")
    print("\nYou can now visit the forum and other sections to see the sample content!")

if __name__ == "__main__":
    populate_sample_data()