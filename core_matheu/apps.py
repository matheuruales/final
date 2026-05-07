from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_matheu'

    def ready(self):
        import core_matheu.signals  # noqa: F401
