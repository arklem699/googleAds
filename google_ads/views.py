from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from google_ads.utils import create_spreadsheet, update_spreadsheet_values, fetch_data_from_api


# Получение данных и заполнение ими новой гугл-таблицы
@api_view(['GET'])
def get_data(request):
    service, spreadsheet, link = create_spreadsheet()
    camp_id = request.GET.get('camp_id')
    conversion_name = request.GET.get('conversion_name')

    if camp_id:
        data = fetch_data_from_api(camp_id)
        if data is not None:
            if 'error' in data:
                return render(request, 'index.html', {'error_message': "Ошибка: {}".format(data['error'])})
            else:
                formatted_data = [{"name": entry['name'], "conversion_name": conversion_name} for entry in data]
                update_spreadsheet_values(service, spreadsheet, formatted_data)
                return render(request, 'index.html', {'link': link})
        else:
            return Response("Ошибка при получении данных", status=500)
    else:
        return render(request, 'index.html')