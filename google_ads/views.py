from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from google_ads.utils import create_spreadsheet, update_spreadsheet_values, fetch_data_from_api
from google_ads.models import Campaign
from google_ads.serializers import CampaignSerializer


# Получение данных и заполнение ими новой гугл-таблицы или выдача ссылки на существующую
@api_view(['GET'])
def get_data(request):
    camp_id = request.GET.get('camp_id')
    conversion_name = request.GET.get('conversion_name')

    if camp_id:
        data = fetch_data_from_api(camp_id)

        if data is not None:
            campaign = Campaign.objects.filter(campaign_id=camp_id).first()

            if campaign:
                return render(request, 'index.html', {'link': campaign.spreadsheet_link})

            service, spreadsheet, link = create_spreadsheet()

            if data != "no_clicks":
                formatted_data = [{"name": entry['name'], "conversion_name": conversion_name} for entry in data]
                update_spreadsheet_values(service, spreadsheet, formatted_data)

            campaign_data = {'campaign_id': camp_id, 'spreadsheet_link': link}
            serializer = CampaignSerializer(data=campaign_data)
            if serializer.is_valid():
                serializer.save()
                return render(request, 'index.html', {'link': link})
            else:
                return Response(serializer.errors, status=400)

    return render(request, 'index.html')