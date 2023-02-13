from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('dash_query/', views.dash_query, name='dash_query'),
  path('dash_select/', views.dash_select, name='dash_select'),
]
