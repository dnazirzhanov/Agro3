from django.apps import AppConfig


class AgroSuppliesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "agro_supplies"
    
    def ready(self):
        # Import translations to ensure they are registered
        from . import translation
