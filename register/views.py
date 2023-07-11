import re

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect


from .models import Equipment, EndPoint, Consumer, Communication, Connection, Port
from .forms import forms, EndPointEditForm, ConnectionForm, ConnectionFormSet, CustomFormset
# Create your views here.


def index(request):

    # Get equipments by their types
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
            # Обработка данных из form.cleaned_data
            #(здесь мы просто присваиваем их полю due_back)
            endpoint_inst.name = form.cleaned_data['endpoint_name']
            endpoint_inst.save()
            # print('New value applied successfully: ', form.cleaned_data['endpoint_name'])

            # Переход по адресу 'all-borrowed':
            return HttpResponseRedirect(reverse('endpoint_detail', args=[str(endpoint_inst.id)]))

    # Если это GET (или какой-либо ещё), создать форму по умолчанию.
    else:
        help_msg = f"Enter new name for endpoint {endpoint_inst.name}"
        form = EndPointEditForm(initial={'endpoint_name': help_msg,})

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


# def connection_form_view(request):
#     # num_forms = 0
#     prefix = 'form'
#     if request.method == 'POST':
#         if 'add_new_extra_field' in request.POST:
#             print('add_new_extra_field')
#
#             num_forms = int(request.session.get('num_forms', 0))
#             num_forms += 1
#             request.session['num_forms'] = num_forms
#
#             print(num_forms)
#
#             connection_formset_factory = forms.formset_factory(ConnectionForm, extra=num_forms, can_delete=True)
#
#             print(request.POST)
#             data = {}
#             print('---------------------')
#             for key in request.POST:
#                 data[key] = request.POST[key]
#                 # print(key, ': ', end=' ')
#                 # print(request.POST[key])
#             print('-' * 20)
#
#             data.update({'form-TOTAL_FORMS': str(num_forms),
#                          'form-INITIAL_FORMS': str(num_forms - 1),
#                          # 'form-MIN_NUM_FORMS': 1,
#                          # 'form-MAX_NUM_FORMS': '100',
#                          })
#
#             print(data)
#             connection_formset = connection_formset_factory(data, prefix=prefix)
#
#             context = {
#                 'formset': connection_formset,
#                 'num_forms': num_forms,
#             }
#
#     else:
#         connection_formset_factory = forms.formset_factory(ConnectionForm, extra=0, can_delete=True)
#         print(connection_formset_factory.__dict__)
#         connection_formset = connection_formset_factory(prefix=prefix)
#         num_forms = 0
#         request.session['num_forms'] = num_forms
#         context = {
#             'formset': connection_formset,
#             'num_forms': num_forms,
#         }
#         print(connection_formset)
#     return render(request, 'connection_form.html', context=context)

# def connection_form_view(request):
#     connection_formset_factory = forms.formset_factory(ConnectionForm, formset=ConnectionFormSet, extra=1, can_delete=True)
#     print(connection_formset_factory.__dict__)
#     connection_formset = connection_formset_factory()
#     num_forms = 0
#     request.session['num_forms'] = num_forms
#     context = {
#         'formset': connection_formset,
#         'num_forms': num_forms,
#         'fi': connection_formset.get_forms_and_index(),
#     }
#     # print('+' * 50)
#     # print(connection_formset)
#     if request.method == 'POST':
#         if 'add_new_extra_field' in request.POST:
#             connection_formset.add_form()
#         if 'delete_first' in request.POST:
#             connection_formset.delete_form(0)
#     # print('=' * 50)
#     # print(connection_formset)
#     return render(request, 'connection_form.html', context=context)


def connection_form_view(request):
    my_formset = CustomFormset(ConnectionForm, request.POST)
    re_template = re.compile(r'delete-(\d+)')

    # print('+' * 50)
    # print(connection_formset)
    if request.method == 'POST':
        if 'add_field' in request.POST:
            print('ADD matches')
            my_formset.add_empty_form()
            # print(my_formset[0])
        if 'delete_last' in request.POST:
            my_formset.delete_form()
            print('DELETE matches')
        for field in request.POST:
            res = re_template.findall(field)
            if res:
                my_formset.delete_form(index=int(res[0]))
        if 'submit' in request.POST:
            my_formset.bound_forms()
    # print('=' * 50)
    # print(my_formset)

    context = {
        'formset': my_formset,
        'num_forms': len(my_formset)
    }
    return render(request, 'connection_form.html', context=context)
