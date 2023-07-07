from django import forms
from .models import Connection, Port


class EndPointEditForm(forms.Form):
    endpoint_name = forms.CharField(max_length=100, help_text="Maximum 100 characters.")

    def clean_endpoint_name(self):
        name = self.cleaned_data['endpoint_name']

        if not name:
            raise forms.ValidationError("Field can't be empty.")
        
        return name
    

class ConnectionForm(forms.Form):
    choises = Port.objects.all
    connection_point = forms.ChoiceField(choices=(('a','1'), ('b','2'), ('c','3'),))


# class EndPoointAddFormset()