from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect


from .models import Equipment, EndPoint, Consumer, Communication, Connection
from .forms import EndPointEditForm
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


class EndPointsListView(generic.ListView):
    model = EndPoint


class EndPointDetailView(generic.DetailView):
    model = EndPoint


class CommunicationsListView(generic.ListView):
    model = Communication
    paginate_by = 5
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

    return render(request, 'register/endpoint_edit.html', {'form': form, 'endpoint_inst':endpoint_inst})