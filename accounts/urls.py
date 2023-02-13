from django.urls import path
from . import views
from .views import SignUpView

urlpatterns = [
  path("display_account/", views.display_account, name='display_account'),
  path("signup/", SignUpView.as_view(), name="signup"),
]
