from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from datetime import datetime
from google_ads.utils import create_spreadsheet, update_spreadsheet_values


@api_view(['GET'])
def get_data(request):
    service, spreadsheet, link = create_spreadsheet()
    camp_id = request.GET.get('camp_id')
    conversion_name = request.GET.get('conversion_name')
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if camp_id:
        url = 'https://luck2you.ru/jl8sn.php?page=Stats&camp_id={}&group1=290&group2=1&group3=1&date=6&api_key=80000019bdb5f8f0830a2523952418bb6eccb13'.format(camp_id)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                return render(request, 'index.html', {'error_message': "Ошибка: {}".format(data['error'])})
            else:
                data = [{"name": entry['name'], "conversion_name": conversion_name, "datetime": current_datetime} for entry in data]
                update_spreadsheet_values(service, spreadsheet, data)
                return render(request, 'index.html', {'link': link})
        else:
            return Response("Ошибка при получении данных: {}".format(response.status_code), status=response.status_code)
    else:
        return render(request, 'index.html')