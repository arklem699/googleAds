from django.contrib import admin
from django.urls import path
from google_ads import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.get_data, name='get_data'),
    path('delete_selected_campaigns/', views.delete_selected_campaigns, name='delete_selected_campaigns'),
]