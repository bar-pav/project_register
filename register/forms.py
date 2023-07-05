from django import forms


class EndPointEditForm(forms.Form):
    endpoint_name = forms.CharField(max_length=100, help_text="Maximum 100 characters.")

    def clean_endpoint_name(self):
        name = self.cleaned_data['endpoint_name']

        if not name:
            raise forms.ValidationError("Field can't be empty.")
        
        return name