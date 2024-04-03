from celery import shared_task
from .utils import fetch_data_from_api, update_spreadsheet_values, filter_data
from .models import Campaign
from google.oauth2 import service_account
from datetime import datetime
import pygsheets
import socket


CREDENTIALS_FILE = 'genuine-flight-417318-36aacf4a1fc2.json'  # Имя файла с закрытым ключом


old_getaddrinfo = socket.getaddrinfo

def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response for response in responses if response[0] == socket.AF_INET]

socket.getaddrinfo = new_getaddrinfo


@shared_task
def update_google_spreadsheet():
    # Аутентификация с использованием OAuth 2.0
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])

    # Создание клиента pygsheets с использованием аутентификационных данных
    gc = pygsheets.authorize(custom_credentials=credentials)

    # Получение данных из БД
    campaigns = Campaign.objects.all()

    for campaign in campaigns:
        camp_id = campaign.campaign_id
        domen = campaign.domen
        link = campaign.spreadsheet_link
        conversion_name = campaign.conversion_name
        api_key = campaign.api_key

        # Получение данных из API
        data = fetch_data_from_api(camp_id, api_key)

        if data is not None and data != "no_clicks":
            new_data = filter_data(data, domen)
            formatted_data = [{"name": item['name'], "conversion_name": conversion_name} for item in new_data]
            update_spreadsheet_values(gc, link, formatted_data)

        elif data == "no_clicks":
            # Удаление содержимого таблицы
            sh = gc.open_by_url(link)
            sh.sheet1.clear()


# Переписанный update_spreadsheet_values
def update_spreadsheet_values(gc, link, data):
    sh = gc.open_by_url(link)
    ws = sh[0]
    ws.clear()
    current_datetime = datetime.now().strftime("%d %b %Y").upper()
    values = [[entry['name'], entry['conversion_name'], current_datetime] for entry in data]
    ws.update_values('A1', values=values)