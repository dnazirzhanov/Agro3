"""
Django management command to ensure translations are always working properly.
This command can be run periodically or after deployments to fix translation issues.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Ensure translations are compiled and working properly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-recompile',
            action='store_true',
            help='Force recompilation of all translation files',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌍 Fixing and ensuring translation consistency...'))
        
        # Get the base directory
        base_dir = settings.BASE_DIR
        
        if options['force_recompile']:
            self.stdout.write('🔄 Force recompiling all translations...')
            # Remove existing .mo files
            locale_dir = base_dir / 'locale'
            if locale_dir.exists():
                for mo_file in locale_dir.glob('**/LC_MESSAGES/*.mo'):
                    try:
                        mo_file.unlink()
                        self.stdout.write(f'🗑️  Removed: {mo_file}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Could not remove {mo_file}: {e}')
                        )
        
        # Compile all messages
        self.stdout.write('🔨 Compiling translation messages...')
        try:
            call_command('compilemessages', verbosity=1)
            self.stdout.write(self.style.SUCCESS('✅ Translation compilation completed'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error compiling messages: {e}')
            )
            return
        
        # Verify translations exist
        self.stdout.write('🔍 Verifying translation files...')
        expected_files = [
            'locale/ru/LC_MESSAGES/django.mo',
            'locale/ky/LC_MESSAGES/django.mo'
        ]
        
        all_good = True
        for file_path in expected_files:
            full_path = base_dir / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                self.stdout.write(f'✅ {file_path} exists ({size} bytes)')
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ {file_path} MISSING!')
                )
                all_good = False
        
        if all_good:
            self.stdout.write(
                self.style.SUCCESS('🎉 All translations are working properly!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('⚠️  Some translation files are missing. Please check your setup.')
            )
            
        self.stdout.write('\n💡 Tips for maintaining translations:')
        self.stdout.write('   • Run this command after updating .po files')
        self.stdout.write('   • Restart Django server after translation changes')
        self.stdout.write('   • Clear browser cache if translations don\'t appear')