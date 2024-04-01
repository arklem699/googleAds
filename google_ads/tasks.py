from celery import shared_task
from .utils import fetch_data_from_api, update_spreadsheet_values, filter_data
from .models import Campaign
from google.oauth2 import service_account
import googleapiclient.discovery


CREDENTIALS_FILE = 'genuine-flight-417318-36aacf4a1fc2.json'  # Имя файла с закрытым ключом

@shared_task
def update_google_spreadsheet():
    # Получение данных из БД
    campaigns = Campaign.objects.all()

    for campaign in campaigns:
        camp_id = campaign.campaign_id
        domen = campaign.domen
        link = campaign.spreadsheet_link
        conversion_name = campaign.conversion_name
        api_key = campaign.api_key

        credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets',
                                                                                                        'https://www.googleapis.com/auth/drive'])
        service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)

        # Получение данных из API
        data = fetch_data_from_api(camp_id, api_key)

        if data is not None and data != "no_clicks":
            new_data = filter_data(data, domen)
            formatted_data = [{"name": item['name'], "conversion_name": conversion_name} for item in new_data]
            update_spreadsheet_values(service, link, formatted_data)

        elif data == "no_clicks":
            spreadsheet_id = link.split('/')[-2]
            
            service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range="",
                body={}
            ).execute()