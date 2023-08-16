from django.urls import path

from . import views

urlpatterns = [
    path('email/', views.send_email, name='send_email'),
    path('success/', views.success, name='success'),
]