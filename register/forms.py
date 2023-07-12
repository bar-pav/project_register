from django import forms
from django.forms.widgets import HiddenInput
from .models import Connection, Port


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


class ManagementForm(forms.Form):
    # Uses for save information between page reloading.
    last_index = forms.IntegerField(widget=HiddenInput)
    num_of_forms = forms.IntegerField(widget=HiddenInput)


class CustomFormset:
    def __init__(self, form_class, request_post=None, prefix='form'):
        self.form_class = form_class
        self.form_fields = self.get_form_fields()
        self.request_post = request_post.copy()
        self.num_of_forms = self.get_num_of_forms()
        self.last_index = self.get_last_index()
        self.management_form = self.get_management_form()
        self.prefix = prefix
        self.forms = self.create_empty_forms()

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
            return self.form_class.fields
        else:
            return list(self.form_class.__dict__['declared_fields'].keys())

    def get_management_form(self):
        if 'last_index' in self.request_post:
            form = ManagementForm(self.request_post)
            form.full_clean()
            return form
        form = ManagementForm(data={'num_of_forms': '0', 'last_index': '0'})
        form.full_clean()
        return form

    def update_management_form(self):
        return ManagementForm(data={'last_index': self.last_index, 'num_of_forms': self.num_of_forms})

    def get_num_of_forms(self):
        return self.get_management_form().cleaned_data['num_of_forms']

    def get_last_index(self):
        return self.get_management_form().cleaned_data['last_index']

    def bound_forms(self, delete_index=None):

        # if delete_index is not None:
        #     pass
        self.forms = [[self.create_form(data=self.get_form_kwargs(index, delete_index=delete_index)), index] for index in range(self.num_of_forms)]
        for bf in self.forms:
            bf[0].full_clean()
            print('bound_forms > cleaned_data: ', bf[0].cleaned_data)
        # print(data)

    def get_form_kwargs(self, index, delete_index=None):
        print('get_form_kwargs > num_of_forms', self.num_of_forms)
        # data = {}
        # data.update(self.request_post)
        # print(data)
        # print(data['connection_point'])
        # if self.num_of_forms < 2:
        #     return self.request_post
        # print('Get kwargs')
        # print('index', index)
        # print(self.request_post)
        # print(self.form_fields)
        # print(self.request_post.get('connection_point'))
        # print({field: self.request_post.getlist(field) for field in self.form_fields})
        if delete_index is not None:
            print('get_form_kwargs > delete_index', delete_index)
            print('get_form_kwargs > index before deleted form', index)
            if index >= delete_index:
                index += 1
        print('get_form_kwargs > index after deleted form: ', index)
        print('get_form_kwargs > request_data: ', self.request_post)
        print('get_form_kwargs > fields: ', {field: self.request_post.getlist(field) for field in self.form_fields})
        return {field: self.request_post.getlist(field)[index] for field in self.form_fields}

    def create_empty_forms(self):
        return [[self.create_form(), i] for i in range(self.num_of_forms)]

    def create_form(self, data=None):
        return self.form_class(data=data)

    def add_empty_form(self):
        self.bound_forms()
        self.forms.append([self.create_form(), self.num_of_forms])
        self.num_of_forms += 1
        self.management_form = self.update_management_form()
        print('add_empty_form > num_of_forms: ', self.num_of_forms)

    def insert_empty_form(self, index):
        self.bound_forms()
        for i in self.forms[index:]:
            i[1] += 1
        self.forms.insert(index, [self.create_form(), index])
        self.num_of_forms += 1
        self.management_form = self.update_management_form()

    def delete_form(self, index=None):
        if index is None:  # TODO Fix: Not work correctly.
            index = self.num_of_forms - 1
        self.num_of_forms -= 1
        self.bound_forms(delete_index=index)
        self.management_form = self.update_management_form()
        print('delete_form > pop index: ', index)
        print('delete_form > num_of_forms: ', self.num_of_forms)

    def is_valid(self):
        return all([form[0].is_valid() for form in self.forms])

    def cleaned_data(self):
        if self.is_valid():
            return [form[0].cleaned_data for form in self.forms]
        raise AttributeError(
                "'%s' object does not pass validation" % self.__class__.__name__
            )

    def add_prefix(self, index):
        return "%s-%s" % (self.prefix, index)


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
