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
    total_forms = forms.IntegerField(widget=HiddenInput)
    # total_forms = forms.IntegerField()


class CustomFormset:
    def __init__(self, form_class, request_post=None):
        self.form_class = form_class
        self.request_post = request_post
        self.total_forms = self.get_total_forms()
        self.management_form = self.get_management_form()

    def __iter__(self):
        return iter(self.forms())

    def __getitem__(self, index):
        return self.forms()[index]

    def __repr__(self):
        return '<total_forms> :' + str(self.total_forms)

    def __len__(self):
        return len(self.forms())

    def get_management_form(self):
        if 'total_forms' in self.request_post:
            form = ManagementForm(self.request_post)
            form.full_clean()
            return form
        form = ManagementForm(data={'total_forms': '10'})
        form.full_clean()
        return form

    def update_management_form(self):
        form = ManagementForm(data={'total_forms': self.total_forms})
        return form

    def get_total_forms(self):
        return self.get_management_form().cleaned_data['total_forms']

    def forms(self):
        return [(self.form_class(), i) for i in range(self.total_forms)]

    def empty_form(self):
        return self.form_class()

    def add_empty_form(self):
        self.total_forms += 1
        self.forms()
        self.management_form = self.update_management_form()

    def delete_form(self):
        if len(self.forms()) > 1:
            self.total_forms -= 1
            self.forms().pop()
            self.management_form = self.update_management_form()


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
