from django.db import models


class Campaign(models.Model):
    campaign_id = models.CharField(max_length=100)  # Идентификатор кампании
    domen = models.CharField(max_length=100)  # Домен 
    spreadsheet_link = models.URLField()  # Ссылка на Google-таблицу