from django.apps import AppConfig


class ExamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exam'

    def ready(self):
        import exam.signals  # Asegúrate de importar tu archivo de signals