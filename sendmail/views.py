from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, HttpResponse, redirect

# Create your views here.
from .forms import MailForm


def send_email(request):
    if request.method == 'GET':
        form = MailForm()
    elif request.method == 'POST':
        print('Send mail request.', request.POST)
        form = MailForm(request.POST)
        if form.is_valid():
            print(form)
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
            except BadHeaderError:
                HttpResponse('--------------- Bad headers in massage. --------------')
            else:
                messages.add_message(request, messages.SUCCESS, "Сообщение отправлено.")
                return redirect('success', permanent=True)
                # return HttpResponse('ОK')
    else:
        return HttpResponse('------- Incorrect request----------')
    return render(request, 'email_page.html', {'form': form})


def success(request):
    return HttpResponse('Message sent.')
