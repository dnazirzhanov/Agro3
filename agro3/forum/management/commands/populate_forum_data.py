"""
Management command to populate sample multilingual forum data.

Creates sample categories, tags, and blog posts in English, Russian, and Kyrgyz
to demonstrate the multilingual forum functionality.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from forum.models import Category, Tag, BlogPost
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate sample multilingual forum data'

    def handle(self, *args, **options):
        self.stdout.write('Creating multilingual forum data...')

        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )

        # Create multilingual categories
        categories_data = [
            {
                'name_en': 'Crop Management',
                'name_ru': 'Управление культурами',
                'name_ky': 'Өсүмдүк башкаруу',
                'description_en': 'Best practices for growing and managing crops',
                'description_ru': 'Лучшие практики выращивания и управления культурами',
                'description_ky': 'Өсүмдүктөрдү өстүрүү жана башкаруунун эң жакшы тажрыйбалары',
                'color': '#28a745',
                'slug': 'crop-management'
            },
            {
                'name_en': 'Market Analysis',
                'name_ru': 'Анализ рынка',
                'name_ky': 'Базар анализи',
                'description_en': 'Market trends and price analysis',
                'description_ru': 'Рыночные тенденции и анализ цен',
                'description_ky': 'Базар тренддери жана баа анализи',
                'color': '#007bff',
                'slug': 'market-analysis'
            },
            {
                'name_en': 'Pest Control',
                'name_ru': 'Борьба с вредителями',
                'name_ky': 'Зыянкечтер менен күрөшүү',
                'description_en': 'Effective pest and disease management',
                'description_ru': 'Эффективная борьба с вредителями и болезнями',
                'description_ky': 'Зыянкечтер жана оорулар менен натыйжалуу күрөшүү',
                'color': '#dc3545',
                'slug': 'pest-control'
            },
            {
                'name_en': 'Technology',
                'name_ru': 'Технологии',
                'name_ky': 'Технологиялар',
                'description_en': 'Modern agricultural technologies',
                'description_ru': 'Современные сельскохозяйственные технологии',
                'description_ky': 'Заманбап айыл чарба технологиялары',
                'color': '#6f42c1',
                'slug': 'technology'
            }
        ]

        created_categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name_en'],
                    'name_en': cat_data['name_en'],
                    'name_ru': cat_data['name_ru'],
                    'name_ky': cat_data['name_ky'],
                    'description': cat_data['description_en'],
                    'description_en': cat_data['description_en'],
                    'description_ru': cat_data['description_ru'],
                    'description_ky': cat_data['description_ky'],
                    'color': cat_data['color']
                }
            )
            created_categories.append(category)
            self.stdout.write(f'  {"Created" if created else "Found"} category: {category.name}')

        # Create multilingual tags
        tags_data = [
            {'name_en': 'wheat', 'name_ru': 'пшеница', 'name_ky': 'буудай'},
            {'name_en': 'corn', 'name_ru': 'кукуруза', 'name_ky': 'жүгөрү'},
            {'name_en': 'irrigation', 'name_ru': 'ирригация', 'name_ky': 'сугат'},
            {'name_en': 'organic', 'name_ru': 'органический', 'name_ky': 'органикалык'},
            {'name_en': 'sustainable', 'name_ru': 'устойчивый', 'name_ky': 'туруктуу'},
        ]

        created_tags = []
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name_en'],
                defaults={
                    'name_en': tag_data['name_en'],
                    'name_ru': tag_data['name_ru'],
                    'name_ky': tag_data['name_ky'],
                }
            )
            created_tags.append(tag)
            self.stdout.write(f'  {"Created" if created else "Found"} tag: {tag.name}')

        # Create multilingual blog posts
        posts_data = [
            {
                'title_en': 'Sustainable Wheat Farming Techniques',
                'title_ru': 'Устойчивые методы выращивания пшеницы',
                'title_ky': 'Буудай өстүрүүнүн туруктуу ыкмалары',
                'short_description_en': 'Learn modern sustainable approaches to wheat cultivation',
                'short_description_ru': 'Изучите современные устойчивые подходы к выращиванию пшеницы',
                'short_description_ky': 'Буудай өстүрүүнүн заманбап туруктуу ыкмаларын үйрөнүңүз',
                'content_en': 'Sustainable wheat farming involves using practices that protect the environment while maintaining profitability. This includes crop rotation, integrated pest management, and efficient water use.',
                'content_ru': 'Устойчивое выращивание пшеницы включает использование практик, которые защищают окружающую среду, сохраняя при этом прибыльность. Это включает севооборот, интегрированную борьбу с вредителями и эффективное использование воды.',
                'content_ky': 'Буудайды туруктуу өстүрүү айлана-чөйрөнү коргогон жана ошол эле учурда пайдалуулукту сактаган практикаларды колдонууну камтыйт. Буга өсүмдүк алмашуу, зыянкечтер менен комплекстүү күрөшүү жана сууну натыйжалуу пайдалануу кирет.',
                'category_index': 0,  # Crop Management
                'tags': [0, 3, 4]  # wheat, organic, sustainable
            },
            {
                'title_en': 'Market Trends in Central Asian Agriculture',
                'title_ru': 'Рыночные тенденции в сельском хозяйстве Центральной Азии',
                'title_ky': 'Борбор Азиядагы айыл чарбанын базар тенденциялары',
                'short_description_en': 'Analysis of current market conditions and future outlook',
                'short_description_ru': 'Анализ текущих рыночных условий и будущих перспектив',
                'short_description_ky': 'Учурдагы базар шарттарынын анализи жана келечектеги көрүнүш',
                'content_en': 'The agricultural market in Central Asia is experiencing significant changes due to climate change, technological adoption, and shifting trade relationships.',
                'content_ru': 'Сельскохозяйственный рынок в Центральной Азии переживает значительные изменения из-за изменения климата, внедрения технологий и изменения торговых отношений.',
                'content_ky': 'Борбор Азиядагы айыл чарба базары климаттын өзгөрүшү, технологияларды киргизүү жана соода мамилелеринин өзгөрүшү себептүү олуттуу өзгөрүүлөрдү баштан кечирүүдө.',
                'category_index': 1,  # Market Analysis
                'tags': []
            },
            {
                'title_en': 'Integrated Pest Management for Corn',
                'title_ru': 'Интегрированная борьба с вредителями кукурузы',
                'title_ky': 'Жүгөрү үчүн зыянкечтер менен комплекстүү күрөшүү',
                'short_description_en': 'Effective strategies to protect corn crops from pests',
                'short_description_ru': 'Эффективные стратегии защиты кукурузы от вредителей',
                'short_description_ky': 'Жүгөрү түшүмүн зыянкечтерден коргоонун натыйжалуу стратегиялары',
                'content_en': 'Integrated Pest Management (IPM) combines biological, cultural, and chemical control methods to manage pest populations effectively while minimizing environmental impact.',
                'content_ru': 'Интегрированная борьба с вредителями (ИБВ) сочетает биологические, культурные и химические методы контроля для эффективного управления популяциями вредителей при минимизации воздействия на окружающую среду.',
                'content_ky': 'Зыянкечтер менен комплекстүү күрөшүү (ЗКК) айлана-чөйрөгө болгон таасирди азайтып, зыянкечтердин популяциясын натыйжалуу башкаруу үчүн биологиялык, маданий жана химиялык көзөмөл ыкмаларын айкалыштырат.',
                'category_index': 2,  # Pest Control
                'tags': [1]  # corn
            }
        ]

        for post_data in posts_data:
            post, created = BlogPost.objects.get_or_create(
                slug=post_data['title_en'].lower().replace(' ', '-'),
                defaults={
                    'title': post_data['title_en'],
                    'title_en': post_data['title_en'],
                    'title_ru': post_data['title_ru'],
                    'title_ky': post_data['title_ky'],
                    'short_description': post_data['short_description_en'],
                    'short_description_en': post_data['short_description_en'],
                    'short_description_ru': post_data['short_description_ru'],
                    'short_description_ky': post_data['short_description_ky'],
                    'content': post_data['content_en'],
                    'content_en': post_data['content_en'],
                    'content_ru': post_data['content_ru'],
                    'content_ky': post_data['content_ky'],
                    'author': admin_user,
                    'category': created_categories[post_data['category_index']],
                    'publication_date': timezone.now(),
                    'is_published': True,
                    'is_featured': True
                }
            )
            
            # Add tags
            if post_data['tags']:
                for tag_index in post_data['tags']:
                    post.tags.add(created_tags[tag_index])
            
            self.stdout.write(f'  {"Created" if created else "Found"} post: {post.title}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated multilingual forum data!')
        )