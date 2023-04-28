from django.urls import path

from . import views

app_name = 'fbot'

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),

    path("registerapp/", views.registerapp, name="registerapp"),
    path('stop1/', views.stopprocess, name='stopprocess'),
    path('test/', views.test, name='test'),
    path('getremain/', views.getremain, name='getremain'),

]
