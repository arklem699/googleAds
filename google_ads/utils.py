import pygsheets
from datetime import datetime
import requests


CREDENTIALS_FILE = 'genuine-flight-417318-36aacf4a1fc2.json'  # Имя файла с закрытым ключом

# Получение данных со стороннего API
def fetch_data_from_api(camp_id, api_key):
    url = 'https://luck2you.ru/jl8sn.php?page=Stats&camp_id={}&group1=27&group2=290&date=2&num_page=1&val_page=All{}'.format(camp_id, api_key)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'error' in data:
            print(data['error'])
            return None
        return data
    return None


# Вычленение нужных данных из всех
def filter_data(data, domain):
    flag = False
    new_data = []

    for item in data:
        if item['level'] == '1' and item['name'] == domain:
            flag = True
        elif item['level'] == '2' and flag:
            new_data.append(item)
        elif item['level'] == '1' and flag:
            break

    return new_data


# Создание гугл-таблицы
def create_spreadsheet():
    gc = pygsheets.authorize(service_file=CREDENTIALS_FILE)
    sh = gc.create('gclid')
    sh.share('', role='reader', type='anyone')
    return sh.url


# Заполнение гугл-таблицы данными
def update_spreadsheet_values(link, data):
    gc = pygsheets.authorize(service_file=CREDENTIALS_FILE)
    sh = gc.open_by_url(link)
    ws = sh[0]
    ws.clear()
    current_datetime = datetime.now().strftime("%d %b %Y").upper()
    values = [[entry['name'], entry['conversion_name'], current_datetime] for entry in data]
    ws.update_values('A1', values=values)