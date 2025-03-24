from django.apps import AppConfig

class CoreBankingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_banking'

    def ready(self):
        import core_banking.signals  # Import signals so they get registered
