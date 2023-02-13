from django.shortcuts import render
import requests
import json
from .tasks import zoomeye_filter_host, zoomeye_filter_short, get_cve_list
from django.http import HttpResponseRedirect
from .forms import QueryForm
from zoomeye.sdk import ZoomEye
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings


@login_required
def index(request):

    #if query form has been used
    if request.method == 'POST':
        return redirect('dash_query')
        
    else :
        form = QueryForm()
        return render(request, 'index.html', {'form': form})

@login_required
def dash_query(request):

    err_dict = {} #for zoomeye errors

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = QueryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            #get form data
            query_word = form.cleaned_data['query']

            #retrieve query type
            if form.cleaned_data['query_choice'] == "ip" :
                query_type = "IP"
                query = "ip:" + str(query_word)
            elif form.cleaned_data['query_choice'] == "device" :
                query_type = "device"
            elif form.cleaned_data['query_choice'] == "hostname" :
                query_type = "hostname"
                query = "hostname:" + query_word
            else :
                query_type = "error, no query type selected"
                

            #Perform Zoomeye API Request
            headers = {
            'API-KEY': settings.ZOOMEYE_KEY
            }
           
            response = requests.get('https://api.zoomeye.org/host/search?query=' + query + '&page=0', headers=headers)
            response_data = response.text
            long_dict = json.loads(response_data)


            if response : #200
                zdata = zoomeye_filter_host(response_data)
                request.session["full_dict"] = zdata
                #show only shortened dictionary on initial list,
                #the rest is shown when selected on the next page from session dictionary
                filtered_zdata = zoomeye_filter_short(zdata)
            else : 
                zdata = {'error' : 'response not 200'}
                filtered_zdata = {}
            
                  
            #test for error codes specific to zoomeye, anything other than 60000
            if long_dict["code"] != 60000 :
                err_dict["code"] = long_dict["code"]
                err_dict["error"] = long_dict["error"]

                

            #form = QueryForm()

            context = {
                    'query_type': query_type,
                    'form' : form,
                    'zdata' : zdata,
                    'filtered_zdata': filtered_zdata,
                    'err_dict': err_dict,
                }
        else :         
            context = {
                'form' : form
            }
    else :
        form = QueryForm()
        
        context = {
            'form' : form
    }
    
            
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)




@login_required
def dash_select(request) :
    
    if request.method == 'POST' :
        #get post data
        ind = int(request.POST["selected_ind"])

        #put into session
        request.session["result_ind"] = ind


    else : #not post 
        if "result_ind" in request.session :
            ind = request.session["result_ind"]
        else :
            #redirect, no session data to show
            return redirect('dash_query')
   
    #get key-value pair - the selected dictionary from the query results
    if "full_dict" in request.session :
        test_dict = request.session['full_dict']
    
        if test_dict :
            selected_dict = test_dict[ind]
            port_dict = selected_dict["portinfo"]
           
        else :
            selected_dict = None
    else :
        selected_dict = None


    #do a search for vulnerabilities, pass list to template
    #only if app and version are retrieved for this specific selection
    if port_dict and port_dict["app"] and port_dict["version"] :
        
        cve_list = get_cve_list(port_dict["app"], port_dict["version"] )
    else : 
        cve_list = []

    context = {
        'ind' : ind,
        'selected_dict' : selected_dict,
        'port_dict' : port_dict,
        'cve_list' : cve_list,
    }


    # Render the HTML template index.html with the data in the context variable
    return render(request, 'results.html', context=context)







