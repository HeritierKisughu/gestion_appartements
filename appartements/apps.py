from django.apps import AppConfig


class AppartementsConfig(AppConfig):
    name = 'appartements'

    def ready(self):

        import appartements.signals
