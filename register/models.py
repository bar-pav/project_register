from django.db import models
from django.urls import reverse


# Create your models here.

class Equipment(models.Model):
    type_choices = [
        ('E', 'equipment'),
        ('O', 'optical frame'),
        ('F', 'electrical frame'),
        ('V', 'virtual object'),
        ('-', 'other')
    ]

    name = models.CharField(max_length=100)
    endpoint = models.ForeignKey('EndPoint', on_delete=models.RESTRICT, default=None, null=True, related_name='equipments')
    location = models.CharField(max_length=30)
    note = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=1, choices=type_choices, default='-')

    def get_absolute_url(self):
        return reverse('equipment_detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.name}"

    class Meta:
        unique_together = ('name', 'endpoint',)


class InterfaceType(models.Model):
    type = models.CharField(max_length=15, unique=True, help_text="Enter interface type or his speed.")
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.type}"


class Port(models.Model):
    media_type_choices = [
        ('E', 'electrical'),
        ('O', 'optical'),
        ('V', 'virtual')
    ]

    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE, related_name='ports', blank=True)
    interface_type = models.ForeignKey('InterfaceType', on_delete=models.RESTRICT, related_name='ports')
    media_type = models.CharField(max_length=1, choices=media_type_choices, default='E')
    port_name = models.CharField(max_length=30, blank=True)
    note = models.TextField(null=True, blank=True)

    connected_to = models.OneToOneField('Port', on_delete=models.RESTRICT, related_name='connected_from', blank=True, null=True)
    communication = models.ForeignKey('Communication', on_delete=models.RESTRICT, null=True, blank=True, related_name='ports')

    def __str__(self):
        return f"{self.port_name}"

    class Meta:
        unique_together = ('port_name', 'equipment',)


class EndPoint(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('endpoint_detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.name}"

    class Meta:
        unique_together = ('name', 'code',)


class Consumer(models.Model):

    name = models.CharField(max_length=100)
    telephone = models.TextField(max_length=1000, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('consumer_detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.name}"


class Communication(models.Model):
    service_status_choices = [
        ('E', 'enabled'),
        ('D', 'disabled')
    ]

    name = models.CharField(max_length=150)
    direction_from = models.ForeignKey(EndPoint, on_delete=models.RESTRICT, related_name='direction_from')
    direction_to = models.ForeignKey(EndPoint, on_delete=models.RESTRICT, related_name='direction_to')
    consumer = models.ForeignKey(Consumer, on_delete=models.RESTRICT, related_name='communications')
    service_status = models.CharField(max_length=1, choices=service_status_choices, default='E')
    create_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'direction_from', 'direction_to', 'consumer')

    def get_absolute_url(self):
        return reverse('communication_detail', args=[str(self.id)])

    def __str__(self):
        return f"Communication '{self.name}': 'from {self.direction_from} - to {self.direction_to}'"


class Connection(models.Model):
    station = models.OneToOneField(Port, on_delete=models.RESTRICT, related_name='station')
    line = models.OneToOneField(Port, on_delete=models.RESTRICT, related_name='line')
    # connect = models.ForeignKey(Port, on_delete=models.RESTRICT, null=True, blank=True, related_name='connect')
    communication = models.ForeignKey(Communication, on_delete=models.RESTRICT, null=True, blank=True, related_name='connection')
    create_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Connection '{self.communication}': '{self.station} - {self.line}'"
