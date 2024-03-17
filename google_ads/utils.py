import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests


CREDENTIALS_FILE = 'genuine-flight-417318-36aacf4a1fc2.json'  # Имя файла с закрытым ключом

# Получение данных со стороннего API
def fetch_data_from_api(camp_id):
    url = 'https://luck2you.ru/jl8sn.php?page=Stats&camp_id={}&group1=290&group2=1&group3=1&date=6&api_key=80000019bdb5f8f0830a2523952418bb6eccb13'.format(camp_id)
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None


# Создание гугл-таблицы
def create_spreadsheet():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)

    spreadsheet = service.spreadsheets().create(body={
        'properties': {'title': 'gclid', 'locale': 'ru_RU'},
    }).execute()

    permissions(spreadsheet, httpAuth)
    link = 'https://docs.google.com/spreadsheets/d/{}/edit'.format(spreadsheet['spreadsheetId'])

    return service, spreadsheet, link


# Разрешение на чтение гугл-таблицы для всех
def permissions(spreadsheet, httpAuth):
    driveService = googleapiclient.discovery.build('drive', 'v3', http = httpAuth)
    shareRes = driveService.permissions().create(
        fileId = spreadsheet['spreadsheetId'],
        body = {'type': 'anyone', 'role': 'reader'},  # Доступ на чтение кому угодно
        fields = 'id'
    ).execute()

    return shareRes


# Заполнение гугл-таблицы данными
def update_spreadsheet_values(service, spreadsheet, data):

    # Формируем данные для обновления
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values = [[entry['name'], entry['conversion_name'], current_datetime] for entry in data]
    data_to_update = {
        "range": "A1:C{}".format(len(values)),  
        "majorDimension": "ROWS",  
        "values": values  
    }

    # Выполняем обновление таблицы
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet['spreadsheetId'], body={
        "valueInputOption": "USER_ENTERED",
        "data": [data_to_update]
    }).execute()

    return results