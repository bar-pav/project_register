import re

from django import forms
from django.forms.widgets import HiddenInput
from .models import Connection, Port, Equipment


class ConnectionPointForm(forms.Form):
    equipment = forms.ModelChoiceField(queryset=Equipment.objects.all(), required=False)
    port_name = forms.ModelChoiceField(queryset=Port.objects.all(), required=False)

    fields = ['equipment', 'port_name']


class EndPointEditForm(forms.Form):
    endpoint_name = forms.CharField(max_length=100, help_text="Maximum 100 characters.")

    def clean_endpoint_name(self):
        name = self.cleaned_data['endpoint_name']

        if not name:
            raise forms.ValidationError("Field can't be empty.")
        
        return name
    

class ConnectionForm(forms.Form):
    connection_point = forms.CharField(max_length=100, help_text='max 100 symbols', required=False)
    # connection_point
    # field_2 = forms.CharField(max_length=100, help_text='max 100 symbols', required=False)


class PortModelForm(forms.ModelForm):
    port_name = forms.ModelChoiceField(queryset=Port.objects.all(), required=False)

    class Meta:
        model = Port
        fields = ['equipment', 'port_name']


class ManagementForm(forms.Form):
    """
    Uses for save information between page reloading.
    """
    num_of_forms = forms.IntegerField(widget=HiddenInput)


class CustomFormset:
    def __init__(self, form_class, request_post, initial_data=None, prefix='form'):
        self.form_class = form_class
        self.initial_data = initial_data
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
        if 'fields' in self.form_class.__dict__:
            print("get_form_fields > ", self.form_class.fields)
            return self.form_class.fields
        else:
            fields = self.form_class.__dict__['declared_fields'].keys() or self.form_class.__dict__['base_fields'].keys()
            print("get_form_fields > ", list(fields))
            return list(fields)

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
            'num_of_forms': self.num_of_forms
        })

    def get_num_of_forms(self):
        return self.get_management_form().cleaned_data['num_of_forms']

    def bound_forms(self, delete_index=None):
        self.forms = [[self.create_form(data=self.get_form_kwargs(index, delete_index=delete_index),
                                        auto_id=f'id_{index}_%s'), index] for index in range(self.num_of_forms)]

    def fill_initial(self, delete_index=None):
        self.forms = [[self.create_form(initial=self.get_form_kwargs(index, delete_index=delete_index),
                                        auto_id=f'id_{index}_%s'), index] for index in range(self.num_of_forms)]

    def get_form_kwargs(self, index, delete_index=None):
        # print('get_from_kwargs > ', self.request_post.getlist('equipment'))
        if delete_index is not None:
            if index >= delete_index:
                index += 1
        if self.initial_data:
            return {field: self.request_post[field][index] for field in self.initial_data}
        form_kwargs = {}
        for field in self.form_fields:
            field_list = self.request_post.getlist(field)
            if field_list and index < len(field_list):
                form_kwargs[field] = field_list[index]
        return form_kwargs

    def create_forms(self):
        self.management_form = self.update_management_form()
        return [[self.create_form(self.get_form_kwargs(index=i), auto_id=f'id_{i}_%s'), i] for i in range(self.num_of_forms)]

    def create_form(self, initial=None, data=None, auto_id=None):
        return self.form_class(initial=initial, data=data, auto_id=auto_id)

    def add_empty_form(self):
        print("add_empty_form method")
        self.fill_initial()
        self.forms.append([self.create_form(auto_id=f'id_{self.num_of_forms}_%s'), self.num_of_forms])
        self.num_of_forms += 1
        self.management_form = self.update_management_form()

    def insert_empty_form(self, index):
        self.fill_initial()
        for i in self.forms[index:]:
            i[1] += 1
        self.forms.insert(index, [self.create_form(auto_id=f'id_{index}_%s'), index])
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
        for form in self.forms:
            form[0].full_clean()
        if self.is_valid():
            return [form[0].cleaned_data for form in self.forms]
        raise AttributeError(
                "'%s' object does not pass validation" % self.__class__.__name__
            )

    def is_valid(self):
        return all([form[0].is_valid() for form in self.forms])

    def add_prefix(self, index):
        return "%s-%s" % (self.prefix, index)

    @staticmethod
    def add_id(self, field, index):
        return 'id_%s_%s' % (field, index)

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
            print('bounding form')
            self.bound_forms()
            # if self.is_valid():
            print('cath_action_with_form > cleaned data: ', self.cleaned_data())



# Working version
# class CustomFormset:
#     def __init__(self, form_class, request_post, initial_data=None, prefix='form'):
#         self.form_class = form_class
#         self.initial_data = initial_data
#         if initial_data:
#             self.num_of_forms = len(max(initial_data.values(), key=len))
#             self.request_post = {**request_post, **initial_data}
#             # self.num_of_forms
#         else:
#             self.request_post = request_post.copy()
#             self.num_of_forms = self.get_num_of_forms()
#         self.form_fields = self.get_form_fields()
#         self.management_form = self.get_management_form()
#         self.forms = self.create_forms()
#         self.prefix = prefix
#
#     def __iter__(self):
#         return iter(self.forms)
#
#     def __getitem__(self, index):
#         return self.forms[index]
#
#     def __repr__(self):
#         return str(self.forms)
#
#     def __len__(self):
#         return len(self.forms)
#
#     def get_form_fields(self):
#         if 'fields' in self.form_class.__dict__:
#             return self.form_class.fields
#         else:
#             return list(self.form_class.__dict__['declared_fields'].keys())
#
#     def get_management_form(self):
#         if 'num_of_forms' in self.request_post:
#             form = ManagementForm(self.request_post)
#             form.full_clean()
#             return form
#         form = ManagementForm(data={
#             'num_of_forms': '0',
#         })
#         form.full_clean()
#         return form
#
#     def update_management_form(self):
#         return ManagementForm(data={
#             'num_of_forms': self.num_of_forms
#         })
#
#     def get_num_of_forms(self):
#         return self.get_management_form().cleaned_data['num_of_forms']
#
#     def bound_forms(self, delete_index=None, initial_data=None):
#         self.forms = [[self.create_form(data=self.get_form_kwargs(index, delete_index=delete_index)), index] for index in range(self.num_of_forms)]
#         for bf in self.forms:
#             bf[0].full_clean()
#
#     def get_form_kwargs(self, index, delete_index=None):
#         if delete_index is not None:
#             if index >= delete_index:
#                 index += 1
#         if self.initial_data:
#             return {field: self.request_post[field][index] for field in self.initial_data}
#         return {field: self.request_post.getlist(field)[index] for field in self.form_fields}
#
#     def create_forms(self):
#         self.management_form = self.update_management_form()
#         return [[self.create_form(self.get_form_kwargs(index=i)), i] for i in range(self.num_of_forms)]
#
#     def create_form(self, data=None):
#         return self.form_class(data=data)
#
#     def add_empty_form(self):
#         self.bound_forms()
#         self.forms.append([self.create_form(), self.num_of_forms])
#         self.num_of_forms += 1
#         self.management_form = self.update_management_form()
#
#     def insert_empty_form(self, index):
#         self.bound_forms()
#         for i in self.forms[index:]:
#             i[1] += 1
#         self.forms.insert(index, [self.create_form(), index])
#         self.num_of_forms += 1
#         self.management_form = self.update_management_form()
#
#     def delete_form(self, index=None):
#         if len(self.forms) > 0:
#             if index is None:
#                 index = self.num_of_forms - 1
#             self.num_of_forms -= 1
#             self.bound_forms(delete_index=index)
#             self.management_form = self.update_management_form()
#
#     def is_valid(self):
#         return all([form[0].is_valid() for form in self.forms])
#
#     def cleaned_data(self):
#         if self.is_valid():
#             return [form[0].cleaned_data for form in self.forms]
#         raise AttributeError(
#                 "'%s' object does not pass validation" % self.__class__.__name__
#             )
#
#     def add_prefix(self, index):
#         return "%s-%s" % (self.prefix, index)
#
#     def cath_action_with_form(self):
#         re_delete = re.compile(r'delete-(\d+)')
#         re_add = re.compile(r'add-(\d+)')
#         if 'add_field' in self.request_post:
#             self.add_empty_form()
#         if 'delete_last' in self.request_post:
#             self.delete_form()
#         for field in self.request_post:
#             result_delete = re_delete.findall(field)
#             result_add = re_add.findall(field)
#             if result_delete:
#                 self.delete_form(index=int(result_delete[0]))
#             if result_add:
#                 self.insert_empty_form(int(result_add[0]))
#         if 'submit' in self.request_post:
#             self.bound_forms()


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
