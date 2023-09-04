import re

import django.db.utils
from django.db.models.deletion import RestrictedError
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse


from .models import Equipment, EndPoint, Consumer, Communication, Port
from .forms import (
    # EndPointEditForm,
    ConnectionForm,
    CustomFormset,
    # PortModelForm,
    # DeletePortForm,
    port_formset_factory,
    EndPointModelForm,
    ConsumerModelForm,
    EquipmentForm,
    PortInlineFormsetFactory,
    PortForm,
    CreatePortForm,
    OnePointConnectionForm,
    UploadFromFileForm,
    )
from .utils import CreateEquipment


# Create your views here.


models = {'EndPoint': EndPoint,
          'Consumer': Consumer,
          'Communication': Communication}

forms = {
    'EndPoint': EndPointModelForm,
    'Consumer': ConsumerModelForm,
}

template_detail = {
    'EndPoint': EndPointModelForm,
    'Consumer': ConsumerModelForm,
}


def index(request):
    equipment_count = Equipment.objects.filter(type__exact='E').count()
    optical_frame_count = Equipment.objects.filter(type__exact='О').count()
    context = {
        'equipment_count': equipment_count,
        'optical_frame_count': optical_frame_count,
    }
    return render(request, 'index.html', context=context)


def equipment_list(request):
    if 't' in request.GET:
        equipment_type = request.GET.get('t')
    equipments_by_type = {}
    equipments_count = 0
    categories = Equipment.type_choices.copy()
    categories.pop()
    for category in categories:
        objects = Equipment.objects.filter(type__exact=category[0])
        equipments_by_type[category[1]] = (objects.all(), objects.count())
        equipments_count += objects.count()
    active_tab = categories[0][1]
    upload_form = UploadFromFileForm()
    context = {
        'equipments': equipments_by_type,
        'equipments_count': equipments_count,
        'active_tab': active_tab,
        'upload_form': upload_form,
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
            self.object = form.save()
            messages.add_message(self.request, message=f"Добавлено '{self.object.name}'.", level=messages.SUCCESS)
            print('self.object', self.object)
            for port_form in port_formset:
                port = port_form.save(commit=False)
                port.equipment = self.object
                port.save()
            return redirect('equipment_detail', pk=self.object.id)
        return render(self.request, 'equipment_create.html', self.get_context_data())

    def form_invalid(self, form):
        return render(self.request, 'equipment_create.html', self.get_context_data())


class EquipmentUpdateView(generic.edit.UpdateView):
    model = Equipment
    context_object_name = 'equipment_form'
    fields = "__all__"
    # TODO. For now this function use default template 'register/equipment_form.html'
    # template_name = 'equipment_create.html'


def upload_from_file(request):
    if request.method == 'POST':
        print('Upload function view -> request', request.FILES)
        upload_form = UploadFromFileForm(request.POST, request.FILES)
        print('Upload function view -> upload_form:', upload_form)

        if upload_form.is_valid():
            print('Valid form:')
            # print_file(request.FILES['file'])
            create_equipment = CreateEquipment(request.FILES['file'])
            return HttpResponseRedirect(reverse('equipment_detail', args=[create_equipment.equipment.id]))
        else:
            print('Invalid form:')
    return HttpResponse('OK')


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

    def get_context_data(self, **kwargs):
        ctx = super(EquipmentDetail, self).get_context_data(**kwargs)
        port_count = self.object.ports.count()
        print(port_count)
        empty_port_count = self.object.ports.filter(communication=None).count()
        print(empty_port_count)
        ctx['port_count'] = port_count
        ctx['empty_port_count'] = empty_port_count
        try:
            ctx['usage_percent'] = '%.0d' % (empty_port_count / port_count * 100)
        except ZeroDivisionError:
            ctx['usage_percent'] = 0

        return ctx


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
    """ Возвращает название портов, если указан диапазон"""
    # re_result = re.findall(r'([a-zA-Z0-9а-яА-Я -_\\]+)(\{.+?\})?', name_range)
    re_result = re.findall(r'([a-zA-Z0-9а-яА-Я -_\\]+)(\{.+?})?', name_range)
    port_names = []
    if re_result:
        re_result.reverse()
        boards = re_result.pop()
        board_name, board_range = boards[0], get_range(boards[1])
        ports = None
        port_range = None
        port_name = None
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
    """ Функция добавляет новый порт к оборудованию по переданному индексу."""
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
    return redirect('equipment_ports', pk=pk)
    # return render(request, 'equipment_detail_table.html', context=context)


def delete_port_from_equipment(request, pk):  # TODO на данный момент удаление реализовано с помощью formset для Port.
    if request.method == 'POST':
        form = PortForm(request)
        print(form.cleaned_data())
    return redirect('equipment_detail', pk=pk)


class EndPointsListView(generic.ListView):
    model = EndPoint


class EndPointDetailView(generic.DetailView):
    model = EndPoint


def get_model_detail(request):
    """ Общая функция представления для моделей 'EndPoint' и 'Consumer'. """
    print('get_model_detail > request:', request.GET)
    if request.method == 'GET':
        object_id = request.GET.get('object_id')
        model = request.GET.get('model')
        print(object_id, model)
        obj = models[model].objects.get(pk=int(object_id))
        if model == 'EndPoint':
            context = {
                'endpoint': obj,
            }
            return render(request, 'register/endpoint_detail_ajax.html', context=context)
        elif model == 'Consumer':
            context = {
                'consumer': obj,
            }
            return render(request, 'register/consumer_detail_ajax.html', context=context)


class CommunicationsListView(generic.ListView):
    model = Communication
    # paginate_by = 25
    ordering = ['-create_date']


class CommunicationDetailView(generic.DetailView):
    model = Communication


class ConsumersListView(generic.ListView):
    model = Consumer


class ConsumerDetailView(generic.DetailView):
    model = Consumer


def consumer_create_update(request, pk=None):  # TODO Сделать общую функцию с 'endpoint_create_update'
    title = 'Create Consumer'
    prev_page = request.GET['next'] if 'next' in request.GET else ''
    form = None

    if request.method == 'POST':
        if pk:
            consumer = Consumer.objects.get(pk=pk)
            form = ConsumerModelForm(request.POST, instance=consumer)
            # return HttpResponseRedirect(reverse('endpoint_detail', args=[str(pk)]))
        else:
            form = ConsumerModelForm(request.POST)
        if form.is_valid():
            obj = form.save()
            print('OBJECT FROM FORM', obj)
            pk = obj.id
            # if prev_page:
            #     return HttpResponseRedirect(prev_page)
            return HttpResponseRedirect(reverse('consumer_detail', args=[str(pk)]))
        # else:
        #     # return render(request, 'register/consumer_edit.html', {'form': form, 'title': ''})
    elif request.method == 'GET':
        if "delete" in request.GET:
            consumer = Consumer.objects.get(pk=pk)
            consumer_name = consumer.name
            try:
                consumer.delete()
            except RestrictedError:
                messages.add_message(request, messages.ERROR,
                                     f"Невозможно удалить '{consumer.name}', так как есть действующие связи.")
            else:
                messages.add_message(request, messages.SUCCESS,
                                     f"Запись '{consumer.name}' успешно удалена.")
            return redirect('consumers')
        if pk:
            consumer_object = Consumer.objects.get(pk=pk)
            form = ConsumerModelForm(instance=consumer_object)
            title = 'Edit Consumer'
        else:
            form = ConsumerModelForm()
    return render(request, 'register/consumer_edit.html', {'form': form, 'title': title})


def endpoint_create_update(request, pk=None, model=None):
    title = 'Create Endpoin'  # mutual
    prev_page = request.GET['next'] if 'next' in request.GET else ''
    form = None
    if request.method == 'POST':
        if pk:
            record = models[model].objects.get(pk=pk)
            form = forms[model](request.POST, instance=record)
            # return HttpResponseRedirect(reverse('endpoint_detail', args=[str(pk)]))
        else:
            form = forms[model](request.POST)
        if form.is_valid():
            obj = form.save()
            print('OBJECT FROM FORM', obj)
            pk = obj.id
            # if prev_page:
            #     return HttpResponseRedirect(prev_page)
            return HttpResponseRedirect(reverse(f'{model.lower()}_detail', args=[str(pk)]))

        # else:
        #     # return render(request, 'register/consumer_edit.html', {'form': form, 'title': ''})
    elif request.method == 'GET':
        if "delete" in request.GET:
            record = models[model].objects.get(pk=pk)
            object_name = record.name
            try:
                record.delete()
            except RestrictedError:
                messages.add_message(request, messages.ERROR,
                                     f"Невозможно удалить '{record.name}', так как есть связанные записи.")
            else:
                messages.add_message(request, messages.SUCCESS,
                                     f"Запись '{record.name}' успешно удалена.")
            return redirect(f'{model.lower()}')
        if pk:
            record = models[model].objects.get(pk=pk)
            form = forms[model](instance=record)
            title = f'Edit {model}'
            print('Uses form with instance', pk)
        else:
            print('Uses form without instance', pk)
            form = forms[model]()
    return render(request, f'register/{model.lower()}_edit.html', {'form': form, 'title': title})

# def endpoint_create_update(request, pk=None):
#     if request.method == 'POST':
#         if "delete" in request.POST:
#             EndPoint.objects.get(pk=pk).delete()
#             return redirect('endpoints')
#         # Создаём экземпляр формы и заполняем данными из запроса (связывание, binding):
#         form = EndPointModelForm(request.POST)
#         # Проверка валидности данных формы:
#         if form.is_valid():
#             # Обработка данных из form.cleaned_data при успешной валидации
#             if pk:
#                 EndPoint.objects.filter(pk=pk).update(**form.cleaned_data)
#                 # return HttpResponseRedirect(reverse('endpoint_detail', args=[str(pk)]))
#             else:
#                 obj = form.save()
#                 pk = obj.id
#         return HttpResponseRedirect(reverse('endpoint_detail', args=[str(pk)]))
#
#     # Если это GET (или какой-либо ещё), создать форму по умолчанию.
#     else:
#         if pk:
#             endpoint_object = EndPoint.objects.get(pk=pk)
#             form = EndPointModelForm(instance=endpoint_object)
#             title = 'Edit End Point'
#         else:
#             form = EndPointModelForm()
#             title = 'Create End Point'
#         return render(request, 'register/endpoint_edit.html', {'form': form, 'title': title})


class CommunicationCreateView(generic.edit.CreateView):
    model = Communication
    fields = "__all__"


class CommunicationUpdateView(generic.edit.UpdateView):
    """ Class UpdateView для обновления записи 'Communication'."""
    model = Communication
    fields = "__all__"
    
    def get_success_url(self):
        return self.request.GET.get('next')


class CommunicationDeleteView(generic.edit.DeleteView):
    model = Communication
    success_url = reverse_lazy('communications')


def communication_delete(request, pk=None):
    """ Из AJAX получаем id связей в виде строки с разделителем '$', которые нужно удалить. """
    to_delete = request.GET.get('to_delete')
    print('to_delete:', to_delete)
    print(to_delete.split('$'))
    to_delete = to_delete.split("$")
    if to_delete:
        success = []
        error = []
        communication = None
        for comm_id in to_delete:
            try:
                communication = get_object_or_404(Communication, pk=comm_id)
                communication.ports.clear()
                communication.delete()
            except RestrictedError as e:
                print(e)
                error.append(communication.name)
            else:
                success.append(communication.name)
        if success:
            messages.add_message(request, messages.SUCCESS,
                                 f"Записи '{','.join(success)}' успешно удалены.")
        if error:
            messages.add_message(request, messages.ERROR,
                                 f"Невозможно удалить '{','.join(error)}'.")

    objects = Communication.objects.all()

    context = {'communication_list': objects,
               'title': Communication.get_model_name(plural=True),
               'model': 'Communication'}
    return render(request, 'communications_table.html', context=context)


def objects_list_view(request, model):

    objects = models[model].objects.all()

    context = {'objects': objects,
               'title': models[model].get_model_name(plural=True),
               'model': model}
    return render(request, 'list_view.html', context=context)


def connection_form_view(request):
    my_formset = CustomFormset(ConnectionForm, request.POST)
    my_formset.cath_action_with_form()
    context = {
        'formset': my_formset,
        'num_forms': len(my_formset)
    }
    return render(request, 'connection_edit.html', context=context)


def get_port_set_for_communication(communication_instance):
    return Port.objects.filter(communication__exact=communication_instance).all()


def release_ports_for_communication(communication):
    ports = Port.objects.filter(communication=communication).all()
    for port in ports:
        port.communication = None
        port.connected_to = None
        port.save()


def connections_delete(request, pk):

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
    """ OLD VERSION!
    This view is render set of forms, each of that corresponds to one port from connection set in Connection model.
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
    pass
    # communication = Communication.objects.get(pk=pk)  # Получение записи, для которой выводится список коннекций.
    # connection_ports = get_port_set_for_communication(communication)
    # my_formset = None
    # if request.method == "GET":
    #     my_formset = CustomFormset(PortModelForm,
    #                                request.POST,
    #                                initial_data={'equipment': [port.equipment.id for port in connection_ports],
    #                                              'port_name': [port.id for port in connection_ports]},
    #                                )
    # if request.method == 'POST':
    #     my_formset = CustomFormset(PortModelForm, request.POST)
    #     my_formset.cath_action_with_form()
    #     # print("connection_edit > POST catch action.", my_formset)
    #     if my_formset.is_submit:
    #         print('cleaned: ', my_formset.cleaned_data())
    #         initial_data = get_port_set_for_communication(communication)
    #         new_data = []
    #         for form_data in my_formset.cleaned_data():
    #             new_data.append(form_data['port_name'])
    #         print(initial_data)
    #         print(new_data)
    #         if len(initial_data) != len(new_data):
    #             print('Is changed. Length not equal.')
    #         print('has changed:', initial_data != new_data)
    # context = {
    #     'communication': communication,
    #     'formset': my_formset,
    #     'num_forms': len(my_formset),
    # }
    # return render(request, 'connection_edit.html', context=context)


# def get_ports(request):
#     return
#     field_id = request.GET.get('id').split('_')[1]
#     print('get_ports > request:', request)
#     port_name = [int(port_id) for port_id in request.GET.get('port_name').split(',') if port_id]
#     print('port_name ajax:', port_name)
#     if request.method == 'GET':
#         if request.GET.get('equipment') == '':
#             equipment = ''
#         else:
#             equipment = Equipment.objects.get(pk=int(request.GET.get('equipment')))
#
#         form = PortModelForm(initial={'equipment': equipment},
#                              # equipment=equipment,
#                              auto_id=CustomFormset.get_auto_id(field_id),
#                              reserved_ports=port_name)
#         # form.reserved_ports = port_name
#         context = {
#             'form': [form, field_id]
#         }
#         return render(request, 'connection_edit_ajax_response.html', context=context)
#     # else:
#     #     print('get_ports > request > equipment:', request.GET.get('equipment'))
#     #
#     #     form = PortModelForm(initial={'equipment': None},
#     #                          auto_id=CustomFormset.get_auto_id(field_id))
#     #     print('NO EQUIPMENT')
#     #     context = {
#     #         'form': [form, field_id]
#     #     }
#     #     return render(request, 'connection_edit_ajax_response.html', context=context)def get_ports(request):
#

def get_ports_test(request):
    """ Получает данные из AJAX запроса для формы выбора порта. """
    print('request GET:', request.GET)
    endpoint_id = request.GET.get('endpoint')
    equipment_type = request.GET.get('equipment_type')
    equipment_id = request.GET.get('equipment')
    form_index = request.GET.get('id').split('_')[1]
    communication_type = request.GET.get('communication_type')
    if request.method == 'GET':
        form = OnePointConnectionForm(initial={'endpoint': endpoint_id,
                                               'equipment_type': equipment_type,
                                               'equipment': equipment_id,
                                               },
                                      # equipment=equipment,
                                      auto_id=CustomFormset.get_auto_id(form_index),
                                      reserved_ports=None,
                                      communication_type=communication_type,
                                      )
        form.index = form_index
        # # form.reserved_ports = port_name
        context = {
            'form': form
        }
        return render(request, 'connection_edit_ajax_response.html', context=context)


def is_ports_empty(ports):
    if isinstance(ports, list):
        return all([port.is_empty() for port in ports])
    else:
        return ports.is_empty()


def busy_ports(ports):
    if isinstance(ports, list):
        return [port for port in ports if not port.is_empty()]
    else:
        return ports if not ports.is_empty() else []


def connection_edit_with_filter(request, pk):
    """ This view is render set of forms.

                Connection sequence looks like:
                    port_source - port_through_1 - port_through_2 - port_destination
                In example it has 4 connection ports.
                Form set implemented as 'CustomFormset'.
                One Port form is instance of 'OnePointConnectionForm'.
            """
    communication = get_object_or_404(Communication, pk=pk)  # Получение записи, для которой выводится список коннекций.
    related_ports = get_port_set_for_communication(communication)  # Получаем порты, через которые проходит данная связь
    my_formset = None
    if request.method == "GET":
        if related_ports:
            print('com type 1: ', communication.communication_type)
            my_formset = CustomFormset(OnePointConnectionForm,
                                       request.POST,
                                       initial_data={'endpoint': [port.equipment.endpoint.id if port.equipment.endpoint else None for port in related_ports],
                                                     'equipment_type': [port.equipment.type if port else None for port in related_ports],
                                                     'equipment': [port.equipment if port else None for port in related_ports],
                                                     'port': [port.id if port else None for port in related_ports]},
                                       communication_type=communication.communication_type
                                       )
        else:
            my_formset = CustomFormset(OnePointConnectionForm,
                                       request.POST,
                                       communication_type=communication.communication_type)
    if request.method == 'POST':
        my_formset = CustomFormset(OnePointConnectionForm, request.POST, communication_type=communication.communication_type)
        my_formset.cath_action_with_form()
        if my_formset.is_submit:
            if my_formset.is_valid():
                print('cleaned: ', my_formset.cleaned_data())
                ports = []
                for form_data in my_formset.cleaned_data():
                    ports.append(form_data['port'])
                print('NEW DATA:', ports)
                if related_ports:
                    release_ports_for_communication(communication)
                if is_ports_empty(ports):
                    if len(ports) == 1:
                        ports[0].communication = communication
                        ports[0].save()
                    elif len(ports) >= 2:
                        for port, next_port in zip(range(len(ports) - 1), range(1, len(ports))):
                            ports[port].connected_to = ports[next_port]
                            ports[port].communication = communication
                            ports[next_port].communication = communication
                            ports[port].save()
                            ports[next_port].save()
                    return redirect('communication_detail', pk=communication.id)
                # else:
                #     messages.add_message(request, messages.ERROR, f'Порт "{busy_ports(ports)}" занят.')

    context = {
        'communication': communication,
        'formset': my_formset,
        'num_forms': len(my_formset),
    }
    return render(request, 'connection_edit_with_filter.html', context=context)


def search_communication(request):
    search = request.GET.get('search').strip()
    if search:
        communications = Communication.objects.filter(Q(name__icontains=search) | Q(name__exact=search) | Q(direction_from__name__icontains=search) | Q(direction_to__name__icontains=search) | Q(direction_from__code__iexact=search) | Q(direction_to__code__iexact=search))
    else:
        communications = Communication.objects.all()
    context = {
        'communication_list': communications
    }
    return render(request, 'communications_table.html', context=context)




