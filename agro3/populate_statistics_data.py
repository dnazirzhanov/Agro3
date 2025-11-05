#!/usr/bin/env python
"""
Sample data script for agro_statistics app.

This script creates sample categories and statistics with multilingual content
to test the Statistics functionality.
"""
import os
import sys
import django
from django.core.files import File

# Add the parent directory to the path so we can import Django modules
sys.path.append('/workspaces/Agro3/agro3')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agro_main.settings')
django.setup()

from agro_statistics.models import StatisticCategory, Statistic
from django.utils.text import slugify
from datetime import datetime


def create_sample_data():
    """Create sample categories and statistics with HTML files."""
    print("Creating sample data for Statistics app...")
    
    # Create categories with multilingual names
    category_data = [
        {
            'name_en': 'Agricultural Production',
            'name_ru': 'Сельскохозяйственное производство',
            'name_ky': 'Айыл чарба өндүрүшү',
            'description_en': 'Statistics on crop production, yields, and agricultural output across different regions.',
            'description_ru': 'Статистика по производству сельскохозяйственных культур, урожайности и сельскохозяйственной продукции в различных регионах.',
            'description_ky': 'Ар кайсы аймактардагы эгин өндүрүү, түшүмдүүлүк жана айыл чарба өнүмдөрү боюнча статистика.',
        },
        {
            'name_en': 'Livestock & Animal Husbandry',
            'name_ru': 'Животноводство',
            'name_ky': 'Мал чарбачылык',
            'description_en': 'Comprehensive data on livestock populations, animal products, and pastoral activities.',
            'description_ru': 'Комплексные данные о поголовье скота, продуктах животноводства и пастбищной деятельности.',
            'description_ky': 'Мал басы, мал чарбачылык өнүмдөрү жана жайыт иштери боюнча комплекстүү маалыматтар.',
        },
        {
            'name_en': 'Economic Analysis',
            'name_ru': 'Экономический анализ',
            'name_ky': 'Экономикалык анализ',
            'description_en': 'Economic indicators, market trends, and financial analysis of agricultural sector.',
            'description_ru': 'Экономические показатели, рыночные тенденции и финансовый анализ сельскохозяйственного сектора.',
            'description_ky': 'Айыл чарба секторунун экономикалык көрсөткүчтөрү, базар тенденциялары жана каржылык анализи.',
        }
    ]
    
    # Create categories
    categories = {}
    for cat_data in category_data:
        category, created = StatisticCategory.objects.get_or_create(
            name_en=cat_data['name_en'],
            defaults={
                'name_ru': cat_data['name_ru'],
                'name_ky': cat_data['name_ky'],
                'description_en': cat_data['description_en'],
                'description_ru': cat_data['description_ru'],
                'description_ky': cat_data['description_ky'],
                'is_active': True,
            }
        )
        categories[cat_data['name_en']] = category
        action = "Created" if created else "Found existing"
        print(f"{action} category: {cat_data['name_en']}")
    
    # Create statistics with HTML files
    statistics_data = [
        {
            'category': 'Agricultural Production',
            'title_en': 'Annual Crop Production Report',
            'title_ru': 'Годовой отчет по производству сельскохозяйственных культур',
            'title_ky': 'Эгин өндүрүү боюнча жылдык отчет',
            'description_en': 'Comprehensive analysis of crop yields, production volumes, and agricultural trends.',
            'description_ru': 'Комплексный анализ урожайности, объемов производства и сельскохозяйственных тенденций.',
            'description_ky': 'Түшүмдүүлүк, өндүрүү көлөмү жана айыл чарба тенденцияларынын комплекстүү анализи.',
            'html_files': {
                'en': '/workspaces/Agro3/agro3/media/statistics_html/crop_production_en.html',
                'ru': '/workspaces/Agro3/agro3/media/statistics_html/crop_production_ru.html',
                'ky': '/workspaces/Agro3/agro3/media/statistics_html/crop_production_ky.html',
            },
            'is_featured': True,
        },
        {
            'category': 'Livestock & Animal Husbandry',
            'title_en': 'Livestock Production Statistics',
            'title_ru': 'Статистика животноводства',
            'title_ky': 'Мал чарбачылык статистикасы',
            'description_en': 'Detailed statistics on animal populations, meat and dairy production, and livestock management.',
            'description_ru': 'Подробная статистика по поголовью животных, производству мяса и молочных продуктов, управлению скотом.',
            'description_ky': 'Жаныбарлардын саны, эт жана сүт өнүмдөрүн өндүрүү, мал чарбачылыкты башкаруу боюнча деталдуу статистика.',
            'html_files': {
                'en': '/workspaces/Agro3/agro3/media/statistics_html/livestock_production_en.html',
                'ru': '/workspaces/Agro3/agro3/media/statistics_html/livestock_production_ru.html',
                'ky': '/workspaces/Agro3/agro3/media/statistics_html/livestock_production_ky.html',
            },
            'is_featured': True,
        }
    ]
    
    # Create statistics
    for stat_data in statistics_data:
        category = categories[stat_data['category']]
        
        # Create slug from English title
        slug = slugify(stat_data['title_en'])
        
        statistic, created = Statistic.objects.get_or_create(
            slug=slug,
            defaults={
                'category': category,
                'title_en': stat_data['title_en'],
                'title_ru': stat_data['title_ru'],
                'title_ky': stat_data['title_ky'],
                'description_en': stat_data['description_en'],
                'description_ru': stat_data['description_ru'],
                'description_ky': stat_data['description_ky'],
                'is_published': True,
                'is_featured': stat_data.get('is_featured', False),
                'publication_date': datetime.now(),
                'views_count': 0,
            }
        )
        
        # Attach HTML files if statistic was just created
        if created:
            for lang, file_path in stat_data['html_files'].items():
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        django_file = File(f)
                        
                        # Set the appropriate file field based on language
                        if lang == 'en':
                            statistic.html_file_en.save(
                                f"{slug}_en.html",
                                django_file,
                                save=False
                            )
                        elif lang == 'ru':
                            statistic.html_file_ru.save(
                                f"{slug}_ru.html",
                                django_file,
                                save=False
                            )
                        elif lang == 'ky':
                            statistic.html_file_ky.save(
                                f"{slug}_ky.html",
                                django_file,
                                save=False
                            )
            
            statistic.save()
        
        action = "Created" if created else "Found existing"
        print(f"{action} statistic: {stat_data['title_en']}")
    
    print("\n✅ Sample data creation completed!")
    print(f"Categories created: {StatisticCategory.objects.count()}")
    print(f"Statistics created: {Statistic.objects.count()}")
    print("\nYou can now test the Statistics section at: /en/statistics/")


if __name__ == '__main__':
    create_sample_data()