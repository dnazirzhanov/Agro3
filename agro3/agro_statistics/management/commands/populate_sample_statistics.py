"""
Management command to populate sample statistics data for testing
"""

import os
from django.core.management.base import BaseCommand
from django.core.files import File
from agro_statistics.models import Statistic
from django.conf import settings


class Command(BaseCommand):
    help = 'Populate sample statistics data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate sample statistics data...'))
        
        # Clear existing data
        Statistic.objects.all().delete()
        self.stdout.write('Cleared existing statistics data')
        
        # Create crop production statistic
        crop_stat = Statistic.objects.create(
            title_en='Crop Production Statistics 2024',
            title_ru='Статистика производства сельскохозяйственных культур 2024',
            title_ky='Айыл чарба өсүмдүктөрүн өндүрүү статистикасы 2024',
            short_description_en='Comprehensive analysis of crop production performance across different regions',
            short_description_ru='Комплексный анализ показателей производства сельскохозяйственных культур в разных регионах',
            short_description_ky='Ар кайсы аймактарда айыл чарба өнүмдөрүн өндүрүү көрсөткүчтөрүнүн комплекстүү анализи',
            slug='crop-production-2024',
            is_published=True,
            is_featured=True,
            views_count=0
        )

        # Create livestock statistic
        livestock_stat = Statistic.objects.create(
            title_en='Livestock Industry Report 2024',
            title_ru='Отчет по животноводству 2024',
            title_ky='Мал чарбачылык отчету 2024',
            short_description_en='Annual report on livestock populations, production metrics and market developments',
            short_description_ru='Годовой отчет о поголовье скота, производственных показателях и развитии рынка',
            short_description_ky='Мал басы, өндүрүш көрсөткүчтөрү жана рынок өнүгүүсү боюнча жылдык отчет',
            slug='livestock-report-2024',
            is_published=True,
            is_featured=False,
            views_count=0
        )

        # Add HTML files to statistics
        media_path = os.path.join(settings.MEDIA_ROOT, 'statistics_html')
        
        # Crop production files
        crop_files = [
            ('crop_production_2024_en.html', 'html_file_en'),
            ('crop_production_2024_ru.html', 'html_file_ru'),
            ('crop_production_2024_ky.html', 'html_file_ky'),
        ]
        
        for filename, field_name in crop_files:
            file_path = os.path.join(media_path, filename)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    django_file = File(f, name=filename)
                    setattr(crop_stat, field_name, django_file)
                    crop_stat.save()
                self.stdout.write(f'Added {filename} to crop statistics')
            else:
                self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))

        # Livestock files
        livestock_files = [
            ('livestock_report_2024_en.html', 'html_file_en'),
            ('livestock_report_2024_ru.html', 'html_file_ru'),
            ('livestock_report_2024_ky.html', 'html_file_ky'),
        ]
        
        for filename, field_name in livestock_files:
            file_path = os.path.join(media_path, filename)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    django_file = File(f, name=filename)
                    setattr(livestock_stat, field_name, django_file)
                    livestock_stat.save()
                self.stdout.write(f'Added {filename} to livestock statistics')
            else:
                self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {Statistic.objects.count()} statistics\n'
                f'Sample data population completed!'
            )
        )