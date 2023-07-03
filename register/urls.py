from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('communications/', views.CommunicationsListView.as_view(), name='communications'),
    path('communication/<pk>', views.CommunicationDetailView.as_view(), name='communication_detail'),
    path('consumers/', views.ConsumersListView.as_view(), name='consumers'),
    path('consumer/<pk>', views.ConsumerDetailView.as_view(), name='consumer_detail'),
]
