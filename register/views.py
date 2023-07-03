from django.shortcuts import render
from django.views import generic

from .models import Equipment, EndPoint, Consumer, Communication, Connection
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


class CommunicationsListView(generic.ListView):
    model = Communication


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


