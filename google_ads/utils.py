import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'genuine-flight-417318-36aacf4a1fc2.json'  # Имя файла с закрытым ключом

def permissions(spreadsheet, httpAuth):
    driveService = googleapiclient.discovery.build('drive', 'v3', http = httpAuth)
    shareRes = driveService.permissions().create(
        fileId = spreadsheet['spreadsheetId'],
        body = {'type': 'anyone', 'role': 'reader'},  # Доступ на чтение кому угодно
        fields = 'id'
    ).execute()

    return shareRes


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


def update_spreadsheet_values(service, spreadsheet, data):
    # Формируем данные для обновления
    values = [[entry['name'], entry['conversion_name'], entry['datetime']] for entry in data]
    data_to_update = {
        "range": "A1:C{}".format(len(values)),  
        "majorDimension": "ROWS",  
        "values": values  
    }

    # Выполняем обновление таблицы
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet['spreadsheetId'], body={
        "valueInputOption": "USER_ENTERED",
        "data": [data_to_update]  # Передаем только один элемент в списке data, который содержит данные для заполнения
    }).execute()

    return results