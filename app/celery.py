from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

# Использование конфигураций из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Установка исполнителя (pool) для Celery
app.conf.worker_pool = 'eventlet'

# Автоматическое обнаружение и регистрация задач из приложений Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)