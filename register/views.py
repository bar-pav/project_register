import re

import django.db.utils
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.http import JsonResponse, HttpResponse


from django.db.models.deletion import RestrictedError

from .models import Equipment, EndPoint, Consumer, Communication, Connection, Port
from .forms import (EndPointEditForm,
                    ConnectionForm,
                    CustomFormset,
                    PortModelForm,
                    ConnectionPointForm,
                    # DeletePortForm,
                    port_formset_factory,
                    EndPointModelForm,
                    ConsumerModelForm,
                    EquipmentForm,
                    PortInlineFormsetFactory,
                    PortForm,
                    CreatePortForm
                    )
# ConnectionFormSet)

from django.contrib import messages

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


class EquipmentCreateView(generic.edit.CreateView):
    model = Equipment
    fields = "__all__"
    template_name = "equipment_create.html"

    def get_context_data(self, **kwargs):
        print('Get context data.')
        print(self.request.POST)
        ctx = super(EquipmentCreateView, self).get_context_data(**kwargs)
        if self.request.method == 'GET':
            ctx['equipment_form'] = EquipmentForm()
            ctx['ports'] = PortInlineFormsetFactory(prefix='ports')
        elif self.request.method == 'POST':
            print('method POST.')
            ctx['equipment_form'] = EquipmentForm(self.request.POST)
            ctx['ports'] = PortInlineFormsetFactory(self.request.POST or None, prefix='ports')
        return ctx

    def form_valid(self, form):
        print('Validation, ', form)
        if form.is_valid():
            port_formset = PortInlineFormsetFactory(self.request.POST or None, prefix='ports')
            print('PORT FORMSET:', port_formset)
            if not port_formset.is_valid():
                print("Error")
                print('FORMSET ERRORS:', port_formset.errors)
                print('CONTEXT DATA formset:', self.get_context_data()['ports'])
                return render(self.request, 'equipment_create.html', self.get_context_data())
            messages.add_message(self.request, message='TEST message.', level=messages.INFO)
            self.object = form.save()
            print('self.object', self.object)
            for port_form in port_formset:
                port = port_form.save(commit=False)
                port.equipment = self.object
                port.save()
            return redirect('equipment_detail', pk=self.object.id)
        return render(self.request, 'equipment_create.html', self.get_context_data())

    def form_invalid(self, form):
        print('FORM INVALID')
        print(form.errors)
        print(self.get_context_data()['equipment_form'])

        return render(self.request, 'equipment_create.html', self.get_context_data())


class EquipmentUpdateView(generic.edit.UpdateView):
    model = Equipment
    context_object_name = 'equipment_form'
    fields = "__all__"


def equipment_delete(request, pk):
    try:
        equipment = Equipment.objects.get(pk=pk)
        equipment.delete()
    except RestrictedError:
        messages.add_message(request, level=messages.ERROR, message='Оборудование не может быть удалено, так как имеет подключения.')
        return HttpResponseRedirect(reverse('equipment_detail', args=[pk]))
    return redirect(reverse_lazy('equipments'))


# def equipment_create_view(request):
#     # if request.method == 'GET':
#     print('Equipment create view +++++++++++++++++++++')
#     port_formset = PortInlineFormsetFactory
#     equipment_form = EquipmentForm(prefix='port')
#     # if request.method == 'GET':
#     context = {
#         'equipment_form': equipment_form,
#         'port_formset': PortInlineFormsetFactory,
#     }
#
#     return render(request, 'equipment_create.html', context=context)


class EquipmentDetail(generic.DetailView):
    model = Equipment
    template_name = 'equipment_detail.html'

    # def get_context_data(self, **kwargs):
    #     ctx = super(EquipmentDetail, self).get_context_data(**kwargs)
    #     ports = Equipment.objects.get(id=self.object.id).ports.all()
    #     PortFormset = port_formset_factory(extra=len(ports))
    #     create_port_form = PortForm()
    #     port_formset = PortFormset(form_kwargs={'instances': ports})
    #     ctx['port_formset'] = port_formset
    #     ctx['create_port_form'] = create_port_form
    #     return ctx


# def equipment_detail(request, pk):
#     equipment = Equipment.objects.get(id=pk)
#     ports = Equipment.objects.get(id=pk).ports.all()
#                 print('DELETE instance:', deleted_form.instance.id)
#                 print('DELETE, cleaned data: ', deleted_form.cleaned_data)
#                 try:
#                     print(deleted_form.instance.__dict__)
#                     deleted_form.instance.delete()
#                     ports = Equipment.objects.get(id=pk).ports.all()
#                     PortFormset = port_formset_factory(extra=len(ports))
#                     port_formset = PortFormset(form_kwargs={'instances': ports})
#                     print('PORTS:', ports)
#                 except:
#                     print('Error!!!')
#         return redirect('equipment_detail', pk=equipment.id)
#
#     context = {
#         'equipment': equipment,
#         'port_formset': port_formset,
#         'create_port_form': create_port_form,
#     }
#     return render(request, 'equipment_detail.html', context=context)


def equipment_ports(request, pk):
    equipment = Equipment.objects.get(id=pk)
    ports = Equipment.objects.get(id=pk).ports.all()
    PortFormset = port_formset_factory(extra=len(ports))
    create_port_form = CreatePortForm()
    # if request.method == "GET":
    port_formset = PortFormset(form_kwargs={'instances': ports})
    if request.method == 'POST':
        print('POST')
        create_port_form = PortForm(request.POST)
        port_formset = PortFormset(request.POST, form_kwargs={'instances': ports})
        if port_formset.is_valid():
            print('port_formset is VALID!')
            for deleted_form in port_formset.deleted_forms:
                print('DELETE instance:', deleted_form.instance.id)
                print('DELETE, cleaned data: ', deleted_form.cleaned_data)
                try:
                    print(deleted_form.instance.__dict__)
                    deleted_form.instance.delete()
                    ports = Equipment.objects.get(id=pk).ports.all()
                    PortFormset = port_formset_factory(extra=len(ports))
                    port_formset = PortFormset(form_kwargs={'instances': ports})
                    print('PORTS:', ports)
                except:
                    print('Error!!!')
        return redirect('equipment_ports', pk=equipment.id)

    context = {
        'equipment': equipment,
        'port_formset': port_formset,
        'create_port_form': create_port_form,
    }
    return render(request, 'equipment_ports.html', context=context)


def get_edit_port_form(request):
    port_id = request.GET.get('port_id')
    print('get_ports > request:', request)
    print(port_id)

    if request.method == 'GET':
        port = Port.objects.get(id=int(port_id))
        edit_port_form = PortForm(instance=port, prefix='update')

        context = {
            'edit_port_form': edit_port_form
        }
        print(edit_port_form.instance)
        return render(request, 'port_edit_ajax_response.html', context=context)


def update_port(request):  # TODO
    form = PortForm(request.POST)
    return HttpResponse("OK")


def get_range(s):
    rng = re.findall(r'\d+', s)
    if len(rng) == 2:
        return range(int(rng[0]), int(rng[1]) + 1)
    elif len(rng) == 1:
        return range(int(rng[0]), int(rng[0]) + 1)


def get_port_name_range(name_range):
    re_result = re.findall(r'([a-zA-Z0-9а-яА-Я -_\\]+)(\{.+?\})?', name_range)
    # print(re_result)
    port_names = []
    if re_result:
        re_result.reverse()
        boards = re_result.pop()
        board_name, board_range = boards[0], get_range(boards[1])
        ports = None
        if re_result:
            ports = re_result.pop()
            port_name, port_range = ports[0], get_range(ports[1])

        if board_range:
            for board in board_range:
                if ports:
                    if port_range:
                        for port in port_range:
                            port_names.append(f'{board_name}{board}{port_name}{port}')
                    else:
                        port_names.append(f'{board_name}{board}{port_name}')
                else:
                    port_names.append(f'{board_name}{board}')
    return port_names


def add_port(request, pk):
    print('ADD PORT FUNCTION')
    equipment = None
    existed_ports_formset = None
    create_form = PortForm(request.POST)
    equipment = Equipment.objects.get(id=pk)
    if create_form.is_valid():
        port_name = create_form.cleaned_data['port_name']
        print("CLEANED DATA", port_name)
        if "{" in port_name:
            ports = get_port_name_range(port_name)
            for port in ports:
                try:
                    Port.objects.create(port_name=port,
                                        equipment=equipment,
                                        interface_type=create_form.cleaned_data['interface_type'],
                                        media_type=create_form.cleaned_data['media_type'],
                                        note=create_form.cleaned_data['note']).save()
                except django.db.utils.IntegrityError:
                    messages.add_message(request, messages.INFO, f'Ports already exists')
        else:
            try:
                obj = create_form.save(commit=False)
                obj.equipment = equipment
                print(obj.port_name, obj.media_type)
                obj.save()
            except django.db.utils.IntegrityError:
                messages.add_message(request, messages.INFO, f'Ports already exists')
    # if request.method == "GET":
    return redirect('equipment_ports', pk=pk)
    # return render(request, 'equipment_detail_table.html', context=context)


def delete_port_from_equipment(request, pk):
    if request.method == 'POST':
        form = PortForm(request)
        print(form.cleaned_data())
    return redirect('equipment_detail', pk=pk)


class EndPointsListView(generic.ListView):
    model = EndPoint


class EndPointDetailView(generic.DetailView):
    model = EndPoint


def endpoint_create_update(request, pk=None):
    # Если данный запрос типа POST, тогда
    if request.method == 'POST':
        if "delete" in request.POST:
            EndPoint.objects.get(pk=pk).delete()
            return redirect('endpoints')
        # Создаём экземпляр формы и заполняем данными из запроса (связывание, binding):
        form = EndPointModelForm(request.POST)
        # Проверка валидности данных формы:
        if form.is_valid():
            # Обработка данных из form.cleaned_data при успешной валидации
            if pk:
                EndPoint.objects.filter(pk=pk).update(**form.cleaned_data)
                # return HttpResponseRedirect(reverse('endpoint_detail', args=[str(pk)]))
            else:
                obj = form.save()
                pk = obj.id
        return HttpResponseRedirect(reverse('endpoint_detail', args=[str(pk)]))

    # Если это GET (или какой-либо ещё), создать форму по умолчанию.
    else:
        if pk:
            endpoint_object = EndPoint.objects.get(pk=pk)
            form = EndPointModelForm(instance=endpoint_object)
            title = 'Edit End Point'
        else:
            form = EndPointModelForm()
            title = 'Create End Point'
        return render(request, 'register/endpoint_edit.html', {'form': form, 'title': title})


def get_endpoint_detail(request):
    print('get_endpoint_detail > request:', request.GET)
    if request.method == 'GET':
        endpoint_id = request.GET.get('endpoint_id')
        print(endpoint_id)
        endpoint = EndPoint.objects.get(pk=int(endpoint_id))
        # if request.GET.get('equipment') == '':
        #     equipment = ''
        # else:
        #     equipment = Equipment.objects.get(pk=int(request.GET.get('equipment')))
        #
        # form = PortModelForm(initial={'equipment': equipment},
        #                      # equipment=equipment,
        #                      auto_id=CustomFormset.get_auto_id(field_id),
        #                      reserved_ports=port_name)
        # # form.reserved_ports = port_name
        context = {
            'endpoint': endpoint
        }
        return render(request, 'endpoint_detail_ajax.html', context=context)


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


def consumer_create_update(request, pk=None):
    # Если данный запрос типа POST, тогда
    if request.method == 'POST':
        if "delete" in request.POST:
            Consumer.objects.get(pk=pk).delete()
            return redirect('consumers')
        # Создаём экземпляр формы и заполняем данными из запроса (связывание, binding):
        form = ConsumerModelForm(request.POST)
        # Проверка валидности данных формы:
        if form.is_valid():
            # Обработка данных из form.cleaned_data при успешной валидации
            if pk:
                Consumer.objects.filter(pk=pk).update(**form.cleaned_data)
                # return HttpResponseRedirect(reverse('endpoint_detail', args=[str(pk)]))
            else:
                obj = form.save()
                pk = obj.id
        return HttpResponseRedirect(reverse('consumer_detail', args=[str(pk)]))

    # Если это GET (или какой-либо ещё), создать форму по умолчанию.
    else:
        if pk:
            consumer_object = Consumer.objects.get(pk=pk)
            form = ConsumerModelForm(instance=consumer_object)
            title = 'Edit Consumer'
        else:
            form = ConsumerModelForm()
            title = 'Create Consumer'
        return render(request, 'register/consumer_edit.html', {'form': form, 'title': title})


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
                        new_data[-1].communication = communication
                    return redirect('communication_detail', pk=communication.id)

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


from django.shortcuts import redirect

def connections_delete(request, pk):
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
    if request.method == 'GET':
        release_ports_for_communication(communication)
    # if request.method == 'POST':
    #     release_ports_for_communication(communication)
    context = {
        'communication': communication,
    }
    # return render(request, 'register/communication_detail.html', context=context)
    return redirect('communication_detail', pk=communication.id)


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
    port_name = [int(port_id) for port_id in request.GET.get('port_name').split(',') if port_id]
    print('port_name ajax:', port_name)
    if request.method == 'GET':
        if request.GET.get('equipment') == '':
            equipment = ''
        else:
            equipment = Equipment.objects.get(pk=int(request.GET.get('equipment')))

        form = PortModelForm(initial={'equipment': equipment},
                             # equipment=equipment,
                             auto_id=CustomFormset.get_auto_id(field_id),
                             reserved_ports=port_name)
        # form.reserved_ports = port_name
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

