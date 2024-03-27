from django.db import models


class Campaign(models.Model):
    campaign_id = models.CharField(max_length=100)  # Идентификатор кампании
    domen = models.CharField(max_length=100)  # Домен 
    conversion_name = models.CharField(max_length=100)  # Имя конверсии
    api_key = models.CharField(max_length=100)  # API-ключ
    spreadsheet_link = models.URLField()  # Ссылка на Google-таблицу