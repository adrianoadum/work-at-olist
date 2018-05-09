from django.urls import path
from . import views

urlpatterns = [
    path('phonecalls/', views.phonecall_list, name='phonecall-list'),
]
