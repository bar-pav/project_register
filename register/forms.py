import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import HiddenInput
from .models import Connection, Port, Equipment, Communication, EndPoint, Consumer
from django.forms import formset_factory, inlineformset_factory
from django.db.models import Q


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = '__all__'
        # exclude = ['note']
        widgets = {'note': forms.Textarea(attrs={"cols": 50, "rows": 3})}
        labels = {'name': 'Название',
                  'endpoint': 'ИП',
                  'location': 'Расположено',
                  'type': 'Тип',
                  'endpoint_opposite': 'Противоположный ИП (для систем)'
                  }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['endpoint'].widget.attrs['class'] = 'form-control'
        self.fields['location'].widget.attrs.update({'class': 'form-control'})
        self.fields['type'].widget.attrs['class'] = 'form-control'
        self.fields['endpoint_opposite'].widget.attrs['class'] = 'form-control'


class UploadFromFileForm(forms.Form):
    file = forms.FileField()


class PortForm(forms.ModelForm):
    class Meta:
        model = Port
        fields = ['port_name', 'interface_type', 'media_type', 'note', 'frame_name']


class CreatePortForm(PortForm):
    class Meta(PortForm.Meta):
        exclude = ['note']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['port_name'].widget.attrs.update({'autocomplete': 'off', 'class': 'form-control'})
        self.fields['port_name'].label = 'Обозначение'
        self.fields['interface_type'].widget.attrs['class'] = 'form-control'
        self.fields['interface_type'].label = 'Тип интерфейса'
        self.fields['media_type'].widget.attrs['class'] = 'form-control'
        self.fields['media_type'].label = 'Тип сигнала'
        self.fields['frame_name'].widget.attrs['class'] = 'form-control'
        self.fields['frame_name'].label = 'Рамка'
        print()


class PortDetailForm(forms.Form):
    porn_name = forms.CharField(max_length=20)

    def __init__(self, instance, *args, **kwargs):
        self.instance = instance
        super(PortDetailForm, self).__init__(*args, **kwargs)


class PortBaseFormSet(forms.BaseFormSet):

    def get_form_kwargs(self, index):
        form_kwargs = super(PortBaseFormSet, self).get_form_kwargs(index)
        port_instance = None
        try:
            port_instance = form_kwargs['instances'].all()[index]
        except IndexError:
            print('Index out of range.')
        return {'instance': port_instance}


PortInlineFormsetFactory = inlineformset_factory(Equipment, Port, form=CreatePortForm, extra=0, can_delete=True, can_delete_extra=False)


def port_formset_factory(extra=None):
    return formset_factory(PortDetailForm, formset=PortBaseFormSet, can_delete=True, extra=extra)


class EndPointModelForm(forms.ModelForm):
    class Meta:
        model = EndPoint
        fields = '__all__'


class ConsumerModelForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = '__all__'


class ConnectionForm(forms.Form):
    connection_point = forms.CharField(max_length=100, help_text='max 100 symbols', required=False)
    # connection_point
    # field_2 = forms.CharField(max_length=100, help_text='max 100 symbols', required=False)


class PortModelForm(forms.Form):
    equipment = forms.ModelChoiceField(queryset=None, required=False)
    port_name = forms.ModelChoiceField(queryset=Port.objects.all(), required=False, validators=[])
    # description = forms.CharField(required=False)

    def __init__(self, reserved_ports=None, *args, **kwargs):
        super(PortModelForm, self).__init__(*args, **kwargs)
        # if self.data:
        #     self.data['port_name'] = Port.objects.get(pk=int(self.data['port_name'])).port_name
        #     print('DATA :', self.data)

        # print('---------------------------->', Port.objects.filter(equipment__exact=self.equipment))
        # print('equipment: ', type(equipment), equipment)
        print('initial', self.initial)
        self.reserved_ports = reserved_ports
        print('reserved ports', self.reserved_ports)
        self.fields['equipment'].queryset = Equipment.objects.all()
        self.fields['port_name'].queryset = self.port_queryset()

        self.fields['equipment'].widget.attrs['class'] = 'form-control'
        self.fields['port_name'].widget.attrs['class'] = 'form-control'

        print('FIELDS:', self.fields['equipment'].__dict__)


    def port_queryset(self):
        equipment_id = self.initial.get('equipment') or self.data.get('equipment')
        port_name = self.initial.get('port_name') or self.data.get('port_name')
        exclude_ports = self.reserved_ports
        # print('exclude_ports', exclude_ports)
        print('------______----____---___:', port_name)
        if equipment_id and port_name:
            return Port.objects.filter(id=port_name).all()
        if equipment_id:
            return Port.objects.filter(equipment__exact=equipment_id).filter(communication__isnull=True).filter(connected_to=None).filter(connected_from=None).all()
        else:
            return Port.objects.none()

    def clean_port_name(self):
        port_name = self.cleaned_data['port_name']
        return port_name

    def clean(self):
        cleaned_data = super().clean()
        port_name = cleaned_data['port_name']
        equipment = cleaned_data['equipment']
        if equipment is None:
            self.add_error('equipment', 'Error: Equipment is empty.')
        if port_name is None:
            self.add_error('port_name', 'Error: Port is empty.')


# New connection point form TODO
class OnePointConnectionForm(forms.Form):
    endpoint = forms.ModelChoiceField(queryset=None, required=False)
    # equipment_type = forms.ModelChoiceField(queryset=None, required=False)
    equipment_type = forms.ChoiceField(choices=Equipment.type_choices, required=False,)
    equipment = forms.ModelChoiceField(queryset=None, required=False)
    port = forms.ModelChoiceField(queryset=None, required=False)

    def __init__(self, reserved_ports=None, communication_type=None, equipment_set=None, port_set=None, *args, **kwargs):
        super(OnePointConnectionForm, self).__init__(*args, **kwargs)
        print('initial', self.initial)
        self.reserved_ports = reserved_ports
        self.communication_type = communication_type
        print('reserved ports', self.reserved_ports)
        self.get_querysets()
        self.fields['endpoint'].widget.attrs.update({'class': 'filter form-control'})
        self.fields['equipment_type'].widget.attrs.update({'class': 'filter form-control'})
        self.fields['equipment'].widget.attrs.update({'class': 'filter form-control'})
        self.fields['port'].widget.attrs.update({'class': 'form-control'})

    def get_querysets(self):
        endpoint = self.initial.get('endpoint') or self.data.get('endpoint')
        equipment_type = self.initial.get('equipment_type') or self.data.get('equipment_type')
        equipment = self.initial.get('equipment') or self.data.get('equipment')
        port = self.initial.get('port') or self.data.get('port')

        if port:
            # ports = Port.objects.filter(equipment=equipment)
            ports = Port.objects.filter(equipment=equipment).exclude(~Q(pk=port) & Q(communication=None) & Q(connected_to=None))
            equipments = Equipment.objects.filter(type=equipment_type) or Equipment.objects.all()
            type_choices = Equipment.type_choices
            endpoints = EndPoint.objects.all()

        else:
            endpoints = EndPoint.objects.all()
            ports = Port.objects.none()
            equipments = Equipment.objects.none()
            type_choices = [('', '---------'), ]
            if endpoint:
                type_choices = Equipment.type_choices
                equipments = Equipment.objects.filter(endpoint=endpoint)
                if equipment_type:
                    equipments = equipments.filter(type=equipment_type)
                if equipment:
                    # ports = Port.objects.filter(equipment=equipment).filter(connected_to=None).filter(communication=None)
                    print('commun type:', self.communication_type)
                    ports = Port.objects.filter(equipment=equipment).filter(Q(connected_to__equipment__type='F') | Q(connected_to=None)).filter(communication=None)
                    if self.communication_type:
                        ports = ports.filter(interface_type=self.communication_type)

        self.fields['endpoint'].queryset = endpoints
        self.fields['equipment_type'].choices = type_choices
        self.fields['equipment'].queryset = equipments
        self.fields['port'].queryset = ports

    def clean_port_name(self):
        port_name = self.cleaned_data['port']
        return port_name

    def clean(self):
        cleaned_data = super().clean()
        port_name = cleaned_data['port']
        equipment = cleaned_data['equipment']
        if equipment is None:
            self.add_error('equipment', 'Error: Equipment field is empty.')
        if port_name is None:
            self.add_error('port', 'Error: Port field is empty.')





class ManagementForm(forms.Form):
    """
    ManagementForm используется для хранения количества форм между перезагрузками страницы.
    """
    num_of_forms = forms.IntegerField(widget=HiddenInput)
    # initial_num = forms.IntegerField(widget=HiddenInput)


class CustomFormset:
    """
    Упрощенная реализация formset'ов.
    """
    def __init__(self, form_class, request_post, initial_data=None, instances=None, prefix='form', communication_type=None):
        self.form_class = form_class
        self.initial_data = initial_data
        self.instances = instances
        self.is_bound = None
        self.is_submit = None
        self.communication_type = communication_type
        if initial_data:
            self.num_of_forms = len(max(initial_data.values(), key=len))
            self.request_post = {**request_post, **initial_data}
        else:
            self.request_post = request_post.copy()
            self.num_of_forms = self.get_num_of_forms()
        self.form_fields = self.get_form_fields()
        self.management_form = self.get_management_form()
        self.forms = self.create_forms()
        self.prefix = prefix

    def __iter__(self):
        return iter(self.forms)

    def __getitem__(self, index):
        return self.forms[index]

    def __repr__(self):
        return str(self.forms)

    def __len__(self):
        return len(self.forms)

    def get_form_fields(self):
        # print('********************************* fields ********************:', self.form_class.__dict__)
        form_fields = None
        look_for_fields = ['fields', 'form_fields', 'declared_fields', 'base_fields']
        for field_name in look_for_fields:
            if self.form_class.__dict__.get(field_name):
                form_fields = self.form_class.__dict__.get(field_name)
                break
        if form_fields:
            return form_fields
        raise AttributeError("'%s' has no declared fields." % self.form_class.__name__)

    def get_management_form(self):
        if 'num_of_forms' in self.request_post:
            form = ManagementForm(self.request_post)
            form.full_clean()
            return form
        form = ManagementForm(data={
            'num_of_forms': '0',
        })
        form.full_clean()
        return form

    def update_management_form(self):
        return ManagementForm(data={
            'num_of_forms': self.num_of_forms,
        })

    def get_num_of_forms(self):
        return self.get_management_form().cleaned_data['num_of_forms']

    def fill_initial(self, delete_index=None, insert_index=None):
        # print('*********************** fill_initial method ***************************')
        self.forms = [self.create_form(initial=self.get_form_kwargs(index, delete_index=delete_index),
                                       auto_id=self.get_auto_id(index, insert_index),
                                       index=index) for index in range(self.num_of_forms)]

    def bound_forms(self, delete_index=None):
        self.forms = [self.create_form(data=self.get_form_kwargs(index, delete_index=delete_index),
                                       auto_id=self.get_auto_id(index),
                                       index=index) for index in range(self.num_of_forms)]
        self.is_bound = True

    def get_form_kwargs(self, index, delete_index=None):
        # print('********************** get_from_kwargs > ', self.request_post)
        if delete_index is not None:
            if index >= delete_index:
                index += 1
        form_kwargs = {}
        if self.initial_data:
            form_kwargs.update({field_name: self.request_post[field_name][index] for field_name in self.initial_data})
            return form_kwargs
        for field in self.form_fields:
            field_list = self.request_post.getlist(field)
            if field_list and index < len(field_list):
                form_kwargs[field] = field_list[index]
        return form_kwargs

    def create_forms(self):
        self.management_form = self.update_management_form()
        return [self.create_form(initial=self.get_form_kwargs(index=i),
                                 auto_id=self.get_auto_id(i),
                                 index=i,
                                 ) for i in range(self.num_of_forms)]

    def create_form(self, initial=None, data=None, auto_id=None, index=None):
        form = self.form_class(initial=initial,
                               data=data,
                               auto_id=auto_id,
                               communication_type=self.communication_type)
        form.index = index
        return form

    def add_empty_form(self):
        # print("************* add_empty_form method **************")
        self.fill_initial()
        self.forms.append(self.create_form(auto_id=self.get_auto_id(self.num_of_forms),
                                           index=self.num_of_forms))
        self.num_of_forms += 1
        self.management_form = self.update_management_form()

    def insert_empty_form(self, index):
        self.fill_initial(insert_index=index)
        for form in self.forms[index:]:
            form.index += 1
        self.forms.insert(index, self.create_form(auto_id=self.get_auto_id(index), index=index))
        self.num_of_forms += 1
        self.management_form = self.update_management_form()

    def delete_form(self, index=None):
        if len(self.forms) > 0:
            if index is None:
                index = self.num_of_forms - 1
            self.num_of_forms -= 1
            self.fill_initial(delete_index=index)
            self.management_form = self.update_management_form()

    def cleaned_data(self):
        if self.is_valid():
            return [form.cleaned_data for form in self.forms]

    def is_valid(self):
        return all([form.is_valid() for form in self.forms])

    # def has_changed(self):
    #     return any([form.has_changed() for form in self.forms])

    def add_prefix(self, index):
        return "%s-%s" % (self.prefix, index)

    def cath_action_with_form(self):
        re_delete = re.compile(r'delete-(\d+)')
        re_add = re.compile(r'add-(\d+)')
        if 'add_field' in self.request_post:
            self.add_empty_form()
        if 'delete_last' in self.request_post:
            self.delete_form()
        for field in self.request_post:
            result_delete = re_delete.findall(field)
            result_add = re_add.findall(field)
            if result_delete:
                self.delete_form(index=int(result_delete[0]))
            if result_add:
                self.insert_empty_form(int(result_add[0]))
        if 'submit' in self.request_post:
            self.bound_forms()
            self.is_submit = True
            print('cath_action_with_form > cleaned data: ', self.cleaned_data())

    @staticmethod
    def get_auto_id(index, insert_index=None):
        if insert_index is not None and index >= insert_index:
            return f'id_{index + 1}_%s'
        return f'id_{index}_%s'


class ConnectionFormSet(forms.BaseFormSet):

    # def add_fields(self, form, index):
    #     super(ConnectionFormSet, self).add_fields(form, index)
    #     # form.fields['id'] = index
    #
    # def get_forms_and_index(self):
    #     return zip(self.forms, range(len(self.forms)))
    #
    # def delete_form(self, index):
    #     del self.forms[index]
    #     print(self.management_form['TOTAL_FORMS'])
    #     print(self.management_form['INITIAL_FORMS'])
    #
    # def add_form(self):
    #     self.management_form['TOTAL_FORMS'] = 3
    #     self.forms.append(self._construct_form(len(self.forms) + 1))
    #     print(self.management_form['TOTAL_FORMS'])
    #     print(self.management_form['INITIAL_FORMS'])
    pass


class EndPointAddFormset():
    pass
