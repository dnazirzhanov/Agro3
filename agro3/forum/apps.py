from django.apps import AppConfig


class ForumConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "forum"
    
    def ready(self):
        """Import translation registry when app is ready."""
        # This ensures translation.py is loaded before admin.py
        import forum.translation  # noqa
