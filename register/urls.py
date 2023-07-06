from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('communications/', views.CommunicationsListView.as_view(), name='communications'),
    re_path('^communication/(?P<pk>\d+)$', views.CommunicationDetailView.as_view(), name='communication_detail'),
    path('communication/create', views.CommunicationCreateView.as_view(), name='communication_create'),
    path('communication/<pk>/update', views.CommunicationUpdateView.as_view(), name='communication_update'),
    path('communication/<pk>/delete', views.CommunicationDeleteView.as_view(), name='communication_delete'),
    path('consumers/', views.ConsumersListView.as_view(), name='consumers'),
    path('consumer/<pk>', views.ConsumerDetailView.as_view(), name='consumer_detail'),
    path('endpoints/', views.EndPointsListView.as_view(), name='endpoints'),
    path('endpoint/<pk>', views.EndPointDetailView.as_view(), name='endpoint_detail'),
    path('endpoints/<pk>/edit', views.endpoint_edit, name='endpoint_edit'),

]
