from django.shortcuts import render, HttpResponse, redirect
from django.core.mail import send_mail, BadHeaderError

# Create your views here.
from .forms import MailForm
from django.conf import settings


def send_email(request):
    if request.method == 'GET':
        form = MailForm()
    elif request.method == 'POST':
        form = MailForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
                return redirect('success', permanent=True)
            except BadHeaderError:
                HttpResponse('--------------- Bad headers in massage. --------------')
    else:
        return HttpResponse('------- Incorrect request----------')
    return render(request, 'email.html', {'form': form})


def success(request):
    return HttpResponse('Message send.')
