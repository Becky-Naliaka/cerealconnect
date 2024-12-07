from django.apps import AppConfig


class CerealconnectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cerealconnect'

class CerealConnectConfig(AppConfig):
    name = 'cerealconnect'

    def ready(self):
        import cerealconnect.signals