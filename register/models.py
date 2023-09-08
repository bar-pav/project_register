from django.db import models
from django.urls import reverse


class PortTypeMismatch(Exception):
    """ Возникает при попытке соединить два порта с разными типами интерфейса или среды передачи."""

# Create your models here.


class Equipment(models.Model):
    type_choices = [
        ('E', 'Оборудование'),
        ('O', 'Оптические кроссы'),
        ('F', 'Рамки'),
        ('V', 'Виртуальные объекты'),
        ('S', 'Системы'),
        ('-', 'Другое'),
        ('', '---------'),
    ]

    name = models.CharField(max_length=100)
    endpoint = models.ForeignKey('EndPoint', on_delete=models.RESTRICT, default=None, null=True, related_name='equipments')
    location = models.CharField(max_length=100, null=True)
    note = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=1, choices=type_choices, default='-')

    endpoint_opposite = models.ForeignKey('EndPoint', on_delete=models.RESTRICT, default=None, null=True, blank=True, related_name='systems')

    def get_absolute_url(self):
        return reverse('equipment_detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.name}"

    class Meta:
        unique_together = ('name', 'type',)


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
    frame_name = models.CharField(max_length=30, blank=True)  # Информация о рамке, на которой расшит порт (вместо frame с OneToOneField).

    connected_to = models.OneToOneField('Port', on_delete=models.RESTRICT, related_name='connected_from', blank=True, null=True)
    frame = models.OneToOneField('Port', on_delete=models.RESTRICT, related_name='port', blank=True, null=True)
    communication = models.ForeignKey('Communication', on_delete=models.RESTRICT, null=True, blank=True, related_name='ports')

    def __str__(self):
        return f"{self.port_name}"

    def get_port_name(self):
        return f"({self.equipment.endpoint})[{self.equipment}]{self.port_name}"

    def is_empty(self):
        return not self.connected_to and not self.communication

    def connect_to(self, obj):
        if isinstance(obj, Port):
            if self.interface_type == obj.interface_type and self.media_type == obj.media_type:
                self.connected_to = obj
            else:
                raise PortTypeMismatch(f"Не совпадают тип интерфейса или среды на портах '{self}' '{obj}'")
        else:
            raise TypeError(f"Объект '{obj}' не является экземпляром Port.")

    class Meta:
        unique_together = ('port_name', 'equipment',)


class EndPoint(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse('endpoint_detail', args=[str(self.id)])

    @staticmethod
    def get_model_name(plural=None):
        return 'ИП'


class Consumer(models.Model):

    name = models.CharField(max_length=100, unique=True)
    telephone = models.TextField(max_length=1000, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse('consumer_detail', args=[str(self.id)])

    @staticmethod
    def get_model_name(plural=None):
        if plural:
            return 'Потребители'
        else:
            return 'Потребитель'


class Communication(models.Model):
    service_status_choices = [
        ('E', 'enabled'),
        ('D', 'disabled')
    ]

    name = models.CharField(max_length=150, null=False)
    service_status = models.CharField(max_length=1, choices=service_status_choices, default='E')
    create_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True, blank=True)

    direction_from = models.ForeignKey(EndPoint, on_delete=models.RESTRICT, null=True, related_name='direction_from')
    direction_to = models.ForeignKey(EndPoint, on_delete=models.RESTRICT, null=True, related_name='direction_to')
    consumer = models.ForeignKey(Consumer, on_delete=models.RESTRICT, related_name='communications')
    communication_type = models.ForeignKey(InterfaceType, null=True, on_delete=models.SET_NULL, related_name='communications')

    class Meta:
        unique_together = ('name', 'direction_from', 'direction_to', 'consumer', 'communication_type')

    def __str__(self):
        return f"{self.name} (#{self.id})"

    def __repr__(self):
        return f"Communication({self.name}, {self.note}, {self.direction_from}, {self.direction_to}, {self.consumer}, {self.communication_type},"

    def get_absolute_url(self):
        return reverse('communication_detail', args=[str(self.id)])

    @staticmethod
    def get_model_name(plural=False):
        return 'Связи'






























class Connection(models.Model):
    station = models.OneToOneField(Port, on_delete=models.RESTRICT, related_name='station')
    line = models.OneToOneField(Port, on_delete=models.RESTRICT, related_name='line')
    # connect = models.ForeignKey(Port, on_delete=models.RESTRICT, null=True, blank=True, related_name='connect')
    communication = models.ForeignKey(Communication, on_delete=models.RESTRICT, null=True, blank=True, related_name='connection')
    create_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Connection '{self.communication}': '{self.station} - {self.line}'"
