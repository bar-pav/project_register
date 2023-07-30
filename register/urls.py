from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('equipments/', views.equipment_list, name='equipments'),
    re_path(r'^equipment/(?P<pk>\d+)$', views.EquipmentDetail.as_view(), name='equipment_detail'),
    path('communications/', views.CommunicationsListView.as_view(), name='communications'),
    re_path(r'^communication/(?P<pk>\d+)$', views.CommunicationDetailView.as_view(), name='communication_detail'),
    path('communication/create', views.CommunicationCreateView.as_view(), name='communication_create'),
    path('communication/<pk>/update', views.CommunicationUpdateView.as_view(), name='communication_update'),
    path('communication/<pk>/delete', views.CommunicationDeleteView.as_view(), name='communication_delete'),
    path('communication/<pk>/connection', views.connection_edit, name='connection_edit'),
    # path('communication/<pk>/ports', views.communication_ports, name='communication_ports'),

    path('consumers/', views.ConsumersListView.as_view(), name='consumers'),
    path('consumer/<pk>', views.ConsumerDetailView.as_view(), name='consumer_detail'),
    path('endpoints/', views.EndPointsListView.as_view(), name='endpoints'),
    path('endpoint/<pk>', views.EndPointDetailView.as_view(), name='endpoint_detail'),
    path('endpoints/<pk>/edit', views.endpoint_edit, name='endpoint_edit'),
    path('connection_form', views.connection_form_view, name='connection_form'),
    path('communication/<pk>/connections_create', views.connections_create, name='connections_create'),
    path('communication/<pk>/connections_edit', views.connections_edit, name='connections_edit'),

    path('get_ports_for_equipment', views.get_ports, name='get_ports')

]
