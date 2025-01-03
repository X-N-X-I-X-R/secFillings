# application/apps.py

from django.apps import AppConfig

class ApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'application'

    def ready(self):
        print("Loading Dash Apps...")
        import application.dash_apps.processing_flow  # ודא שהנתיב נכון
