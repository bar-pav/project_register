from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
# from django.http import JsonResponse, HttpResponse

from .models import Equipment, EndPoint, Consumer, Communication, Connection, Port
from .forms import (EndPointEditForm, ConnectionForm, CustomFormset, PortModelForm, ConnectionPointForm)
# ConnectionFormSet)

# Create your views here.


def index(request):
    # This view show equipments by their types.
    equipments = []
    type_choices = Equipment.type_choices
    all_equipments = Equipment.objects.all().count()
    for t in type_choices:
        equipments.append((t[1], Equipment.objects.filter(type__exact=t[0]).count()))
    context = {
        'all_equipments': all_equipments,
        'equipments': equipments,
    }
    return render(request, 'index.html', context=context)


def equipment_list(request):
    equipments_by_type = {}
    equipments_count = 0
    categories = Equipment.type_choices
    for category in categories:
        objects = Equipment.objects.filter(type__exact=category[0])
        equipments_by_type[category[1]] = (objects.all(), objects.count())
        equipments_count += objects.count()
    context = {
        'equipments': equipments_by_type,
        'equipments_count': equipments_count,
    }
    return render(request, 'equipments.html', context=context)


class EquipmentDetail(generic.DetailView):
    model = Equipment


class EndPointsListView(generic.ListView):
    model = EndPoint


class EndPointDetailView(generic.DetailView):
    model = EndPoint


class CommunicationsListView(generic.ListView):
    model = Communication
    paginate_by = 10
    ordering = ['-create_date']


class CommunicationDetailView(generic.DetailView):
    model = Communication

    # def get_queryset(self):
    #     return Communication.objects.filter(id=self.kwargs['pk'])


class ConsumersListView(generic.ListView):
    model = Consumer


class ConsumerDetailView(generic.DetailView):
    model = Consumer

    # def get_context_data(self):
    #     context = super(ConsumerDetailView, self).get_context_data()


def endpoint_edit(request, pk):
    endpoint_inst = get_object_or_404(EndPoint, pk=pk)
    # Если данный запрос типа POST, тогда
    if request.method == 'POST':
        # Создаём экземпляр формы и заполняем данными из запроса (связывание, binding):
        form = EndPointEditForm(request.POST)
        # Проверка валидности данных формы:
        if form.is_valid():
            # Обработка данных из form.cleaned_data при успешной валидации
            endpoint_inst.name = form.cleaned_data['endpoint_name']
            endpoint_inst.save()
            # Переход по адресу 'all-borrowed':
            return HttpResponseRedirect(reverse('endpoint_detail', args=[str(endpoint_inst.id)]))
    # Если это GET (или какой-либо ещё), создать форму по умолчанию.
    else:
        help_msg = f"Enter new name for endpoint {endpoint_inst.name}"
        form = EndPointEditForm(initial={'endpoint_name': help_msg})
    return render(request, 'register/endpoint_edit.html', {'form': form, 'endpoint_inst': endpoint_inst})


class CommunicationCreateView(generic.edit.CreateView):
    model = Communication
    fields = "__all__"


class CommunicationUpdateView(generic.edit.UpdateView):
    model = Communication
    fields = "__all__"
    
    def get_success_url(self):
        return self.request.GET.get('next')


class CommunicationDeleteView(generic.edit.DeleteView):
    model = Communication
    success_url = reverse_lazy('communications')


def connection_form_view(request):
    my_formset = CustomFormset(ConnectionForm, request.POST)
    my_formset.cath_action_with_form()
    context = {
        'formset': my_formset,
        'num_forms': len(my_formset)
    }
    return render(request, 'connection_edit.html', context=context)


# def get_port_set_for_communication(communication_instance):
#     connection_points = Connection.objects.filter(communication__exact=communication_instance).all()
#     # Первой добавляем запись, соответствующую полю station в модели.
#     connection_ports = [connection_points[0].station]
#     # Для остальных добавляем значения только поля line в модели.
#     connection_ports.extend((point.line for point in connection_points))
#     # print('CONNECTION PORTS-------------------------: ', connection_ports)
#     return connection_ports


def get_port_set_for_communication(communication_instance):
    connection_ports = Port.objects.filter(communication__exact=communication_instance).all()
    if connection_ports:
        # Сначала добавляем первый порт, а затем все порты, которые связаны отношением connected_to.
        ports = [connection_ports[0]]
        ports.extend([port.connected_to for port in connection_ports])
        print('connection_ports:', connection_ports)
        return ports


def release_ports_for_communication(communication):
    ports = Port.objects.filter(communication=communication).all()
    print('ports for communication', communication, ports)
    for port in ports:
        port.communication = None
        port.connected_to = None
        port.save()
    # ports = Port.objects.filter(communication=communication).all()
    # if ports:
    #     return False
    # return True

# def communication_ports(request, pk):
#     communication = Communication.objects.get(pk=pk)  # Получение записи, для которой выводится список коннекций.
#     if request.method == "GET":
#         my_formset = CustomFormset(PortModelForm,
#                                    request.POST,
#                                    # initial_data={'equipment': [port.equipment.id for port in connection_ports],
#                                    #               'port_name': [port.id for port in connection_ports]},
#                                    )
#         # ports = initial_data['port_name']
#         # forms_port = []
#         # for i in ports:
#         #     forms_port.append(PMF(instance=i))
#     if request.method == 'POST':
#         my_formset = CustomFormset(PortModelForm, request.POST)
#         my_formset.cath_action_with_form()
#         # print("connection_edit > POST catch action.", my_formset)
#         if my_formset.is_submit:
#             print('cleaned: ', my_formset.cleaned_data())
#             initial_data = get_port_set_for_communication_new(communication)
#             new_data = []
#             for form_data in my_formset.cleaned_data():
#                 new_data.append(form_data['port_name'])
#             #
#             # print(initial_data)
#             print(new_data)
#             if len(initial_data) != len(new_data):
#                 print('Is changed. Length not equal.')
#             print('has changed:', initial_data != new_data)
#             # print('has_changed: ', my_formset.has_changed())
#             if len(initial_data) == 0:
#                 if len(new_data) < 2:
#                     print('Connection must include at least 2 elements.')
#                 else:
#                     for ind, port in enumerate(new_data[:-1]):
#                         port.connected_to = new_data[ind + 1]
#                         port.communication = communication
#                         port.save()
    #
    # context = {
    #     'communication': communication,
    #     'formset': my_formset,
    #     'num_forms': len(my_formset),
    #     # 'ports': forms_port,
    # }
    # return render(request, 'communication_ports.html', context=context)


def connections_create(request, pk):
    """ This view is render set of forms, each of that corresponds to one port from connection set in Connection model.
            _______________________________________________________________________________
            station                    | line                      | communication
            -------------------------------------------------------------------------------
            port_instance_source      | port_instance_through_1    | communication_instance
            port_instance_through_1   | port_instance_through_2    | communication_instance
            port_instance_through_2   | port_instance_destination  | communication_instance
            -------------------------------------------------------------------------------

            Connection sequence looks like:
                port_instance_source > port_instance_through_1 > port_instance_through_2 > port_instance_destination
            It has 4 connection ports.
            Form set implemented as 'CustomFormset'.
            One Port form is instance of 'PortModelForm'.
        """
    communication = Communication.objects.get(pk=pk)  # Получение записи, для которой выводится список коннекций.
    my_formset = None
    if request.method == "GET":
        my_formset = CustomFormset(PortModelForm, request.POST)
    if request.method == 'POST':
        my_formset = CustomFormset(PortModelForm, request.POST)
        my_formset.cath_action_with_form()
        if my_formset.is_submit:
            if my_formset.is_valid():
                # print('cleaned: ', my_formset.cleaned_data())
                communication_ports = get_port_set_for_communication(communication)
                new_data = []
                for form_data in my_formset.cleaned_data():
                    new_data.append(form_data['port_name'])
                print(new_data)
                if not communication_ports:  # Means there is no records for this communication in DB. Create new communication.
                    # if len(communication_ports) != len(new_data):
                    #     print('Is changed. Length not equal.')
                    # print('has changed:', communication_ports != new_data)
                    # # print('has_changed: ', my_formset.has_changed())
                    if len(new_data) < 2:
                        print('Connection must include at least 2 elements.')
                    else:
                        for ind, port in enumerate(new_data[:-1]):
                            port.connected_to = new_data[ind + 1]
                            port.communication = communication
                            port.save()
                else:
                    raise ValueError("Communication '%s' already has initial data." % communication)

    context = {
        'communication': communication,
        'formset': my_formset,
        'num_forms': len(my_formset),
        # 'ports': forms_port,
    }
    return render(request, 'communication_ports.html', context=context)


def connections_edit(request, pk):
    """ This view is render set of forms, each of that corresponds to one port from connection set in Connection model.
            _______________________________________________________________________________
            station                    | line                      | communication
            -------------------------------------------------------------------------------
            port_instance_source      | port_instance_through_1    | communication_instance
            port_instance_through_1   | port_instance_through_2    | communication_instance
            port_instance_through_2   | port_instance_destination  | communication_instance
            -------------------------------------------------------------------------------

            Connection sequence looks like:
                port_instance_source > port_instance_through_1 > port_instance_through_2 > port_instance_destination
            It has 4 connection ports.
            Form set implemented as 'CustomFormset'.
            One Port form is instance of 'PortModelForm'.
        """
    communication = Communication.objects.get(pk=pk)  # Получение записи, для которой выводится список коннекций.
    connection_ports = get_port_set_for_communication(communication)
    my_formset = None
    if request.method == "GET":
        my_formset = CustomFormset(PortModelForm,
                                   request.POST,
                                   initial_data={'equipment': [port.equipment.id for port in connection_ports],
                                                 'port_name': [port.id for port in connection_ports]},
                                   )
        # ports = initial_data['port_name']
        # forms_port = []
        # for i in ports:
        #     forms_port.append(PMF(instance=i))
    if request.method == 'POST':
        my_formset = CustomFormset(PortModelForm, request.POST)
        my_formset.cath_action_with_form()
        # print("connection_edit > POST catch action.", my_formset)
        if my_formset.is_submit:
            if my_formset.is_valid():
                print('cleaned: ', my_formset.cleaned_data())
                initial_data = get_port_set_for_communication(communication)
                new_data = []
                for form_data in my_formset.cleaned_data():
                    new_data.append(form_data['port_name'])
                # print(initial_data)
                print(new_data)
                release_ports_for_communication(communication)
                # if len(initial_data) != len(new_data):
                #     print('Is changed. Length not equal.')
                #     print('has changed:', initial_data != new_data)
                # else:
                #     print('Length is matched: ', initial_data, new_data)
                if len(new_data) < 2:
                    print('Connection must include at least 2 elements.')
                else:
                    for ind, port in enumerate(new_data[:-1]):
                        port.connected_to = new_data[ind + 1]
                        port.communication = communication
                        port.save()

    context = {
        'communication': communication,
        'formset': my_formset,
        'num_forms': len(my_formset),
        # 'ports': forms_port,
    }
    return render(request, 'communication_ports.html', context=context)


# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
def connection_edit(request, pk):
    """ This view is render set of forms, each of that corresponds to one port from connection set in Connection model.
        _______________________________________________________________________________
        station                    | line                      | communication
        -------------------------------------------------------------------------------
        port_instance_source      | port_instance_through_1    | communication_instance
        port_instance_through_1   | port_instance_through_2    | communication_instance
        port_instance_through_2   | port_instance_destination  | communication_instance
        -------------------------------------------------------------------------------

        Connection sequence looks like:
            port_instance_source > port_instance_through_1 > port_instance_through_2 > port_instance_destination
        It has 4 connection ports.
        Form set implemented as 'CustomFormset'.
        One Port form is instance of 'PortModelForm'.
    """
    communication = Communication.objects.get(pk=pk)  # Получение записи, для которой выводится список коннекций.
    connection_ports = get_port_set_for_communication(communication)
    my_formset = None
    if request.method == "GET":
        my_formset = CustomFormset(PortModelForm,
                                   request.POST,
                                   initial_data={'equipment': [port.equipment.id for port in connection_ports],
                                                 'port_name': [port.id for port in connection_ports]},
                                   )
        # ports = initial_data['port_name']
        # forms_port = []
        # for i in ports:
        #     forms_port.append(PMF(instance=i))
    if request.method == 'POST':
        my_formset = CustomFormset(PortModelForm, request.POST)
        my_formset.cath_action_with_form()
        # print("connection_edit > POST catch action.", my_formset)
        if my_formset.is_submit:
            print('cleaned: ', my_formset.cleaned_data())
            initial_data = get_port_set_for_communication(communication)
            new_data = []
            for form_data in my_formset.cleaned_data():
                new_data.append(form_data['port_name'])

            print(initial_data)
            print(new_data)
            if len(initial_data) != len(new_data):
                print('Is changed. Length not equal.')
            print('has changed:', initial_data != new_data)
            # print('has_changed: ', my_formset.has_changed())

    context = {
        'communication': communication,
        'formset': my_formset,
        'num_forms': len(my_formset),
        # 'ports': forms_port,
    }
    return render(request, 'connection_edit.html', context=context)


def get_ports(request):
    field_id = request.GET.get('id').split('_')[1]
    print('get_ports > request:', request)
    if request.method == 'GET':
        if request.GET.get('equipment') == '':
            equipment = ''
        else:
            equipment = Equipment.objects.get(pk=int(request.GET.get('equipment')))
        form = PortModelForm(initial={'equipment': equipment},
                             # equipment=equipment,
                             auto_id=CustomFormset.get_auto_id(field_id))
        context = {
            'form': [form, field_id]
        }
        return render(request, 'connection_edit_ajax_response.html', context=context)
    # else:
    #     print('get_ports > request > equipment:', request.GET.get('equipment'))
    #
    #     form = PortModelForm(initial={'equipment': None},
    #                          auto_id=CustomFormset.get_auto_id(field_id))
    #     print('NO EQUIPMENT')
    #     context = {
    #         'form': [form, field_id]
    #     }
    #     return render(request, 'connection_edit_ajax_response.html', context=context)
