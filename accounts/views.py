from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# accounts/views.py
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
import requests
import json
from django.conf import settings 

 
@login_required
def display_account(request) :

    user = request.user

    #get ZoomEye credit data
    #Perform Zoomeye API Request
    headers = {
        'API-KEY': settings.ZOOMEYE_KEY
    }
    
    response = requests.get('https://api.zoomeye.org/resources-info', headers=headers)
    response_data = response.text
    z_dict = json.loads(response_data)
    zoomeye_resources = {"userID" : z_dict["user_info"]["name"], 
                        "role" :  z_dict["user_info"]["role"], 
                        "credits" : z_dict["quota_info"]["remain_total_quota"] 
                        }


    context = {
        'user' : user,
        'zoomeye_resources' : zoomeye_resources,
    }


    # Render the HTML template index.html with the data in the context variable
    return render(request, 'account_profile.html', context=context)


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
