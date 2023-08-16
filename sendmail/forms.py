from django import forms


class MailForm(forms.Form):
    recipient = forms.EmailField(label='Email', required=True)
    subject = forms.CharField(label='Тема', required=True)
    message = forms.CharField(label='Сообщение', required=True)