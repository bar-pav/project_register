from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('equipments/', views.equipment_list, name='equipments'),
    path('equipment/create', views.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/upload_create', views.upload_from_file, name='upload_from_file'),
    re_path(r'^equipment/(?P<pk>\d+)/update$', views.EquipmentUpdateView.as_view(), name='equipment_update'),
    re_path(r'^equipment/(?P<pk>\d+)/delete$', views.equipment_delete, name='equipment_delete'),
    re_path(r'^equipment/(?P<pk>\d+)$', views.EquipmentDetail.as_view(), name='equipment_detail'),
    re_path(r'^equipment/(?P<pk>\d+)/ports$', views.equipment_ports, name='equipment_ports'),
    re_path(r'^equipment/(?P<pk>\d+)/add_port$', views.add_port, name='add_port'),
    re_path(r'^equipment/(?P<pk>\d+)/delete_port$', views.delete_port_from_equipment, name='delete_port'),

    path('communications/', views.CommunicationsListView.as_view(), name='communications'),
    re_path(r'^communication/(?P<pk>\d+)$', views.CommunicationDetailView.as_view(), name='communication_detail'),
    path('communication/create', views.CommunicationCreateView.as_view(), name='communication_create'),
    path('communication/<pk>/update', views.CommunicationUpdateView.as_view(), name='communication_update'),
    path('communication/<pk>/delete', views.communication_delete, name='communication_delete'),
    path('consumers/', views.objects_list_view, kwargs={'model': 'Consumer'}, name='consumers'),
    re_path(r'^consumer/(?P<pk>\d+)$', views.ConsumerDetailView.as_view(), name='consumer_detail'),
    re_path(r'^consumer/(?P<pk>\d+)/update$', views.consumer_create_update, name='consumer_edit'),
    path('consumer/create', views.consumer_create_update, name='consumer_create'),
    path('endpoints/', views.objects_list_view, kwargs={'model': 'EndPoint'}, name='endpoints'),
    re_path(r'^endpoint/(?P<pk>\d+)$', views.EndPointDetailView.as_view(), name='endpoint_detail'),
    re_path(r'^endpoint/(?P<pk>\d+)/edit$', views.endpoint_create_update, kwargs={'model': 'EndPoint'}, name='endpoint_edit'),
    path('endpoint/create', views.endpoint_create_update, kwargs={'model': 'EndPoint'}, name='endpoint_create'),

    path('connection_form', views.connection_form_view, name='connection_form'),
    path('communication/<pk>/connections_delete', views.connections_delete, name='connections_delete'),
    path('communication/<pk>/connection_edit_with_filter', views.connection_edit_with_filter, name='connection_edit_with_filter'),

    # AJAX requests URLs
    path('get_ports_for_equipment_test', views.get_ports_test, name='get_ports_test'),
    path('get_edit_port_form', views.get_edit_port_form, name='get_edit_port_form'),
    path('update_port', views.update_port, name='update_port'),
    path('get_endpoint_detail', views.get_model_detail, name='get_endpoint_detail'),
    path('get_consumer_detail', views.get_model_detail, name='get_consumer_detail'),
    path('search_communication', views.search_communication, name="search_communication"),

]
