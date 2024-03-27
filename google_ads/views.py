from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from google_ads.utils import create_spreadsheet, update_spreadsheet_values, fetch_data_from_api, filter_data
from google_ads.models import Campaign
from google_ads.serializers import CampaignSerializer


# Получение данных и заполнение ими новой гугл-таблицы или выдача ссылки на существующую
@api_view(['GET'])
def get_data(request):
    camp_id = request.GET.get('camp_id')
    domen = request.GET.get('domen')
    conversion_name = request.GET.get('conversion_name')
    api_key = request.GET.get('api_key')

    campaigns = Campaign.objects.all()

    if camp_id:
        data = fetch_data_from_api(camp_id, api_key)

        if data is not None:
            campaign = Campaign.objects.filter(campaign_id=camp_id, domen=domen).first()

            if campaign:
                return render(request, 'index.html', {'link': campaign.spreadsheet_link, 'campaigns': campaigns})

            service, spreadsheet, link = create_spreadsheet()

            if data != "no_clicks":

                new_data = filter_data(data, domen)
                formatted_data = [{"name": item['name'], "conversion_name": conversion_name} for item in new_data]
                update_spreadsheet_values(service, spreadsheet, formatted_data)

            campaign_data = {'campaign_id': camp_id, 'domen': domen, 'conversion_name': conversion_name, 'api_key': api_key, 'spreadsheet_link': link}
            serializer = CampaignSerializer(data=campaign_data)

            if serializer.is_valid():
                serializer.save()
                return render(request, 'index.html', {'link': link, 'campaigns': campaigns})
            else:
                return Response(serializer.errors, status=400)

    return render(request, 'index.html', {'campaigns': campaigns})


# Удаление выбранных записей
@api_view(['POST'])
def delete_selected_campaigns(request):
    ids = request.POST.getlist('ids[]')
    ids = [int(id) for id in ids]
    Campaign.objects.filter(id__in=ids).delete()
    return redirect('get_data')