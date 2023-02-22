from django.test import TestCase, Client
from django.conf import settings
import json
import os.path
from .forms import QueryForm
from http import HTTPStatus
from django.contrib.auth.models import User
from django.urls import reverse
from .tasks import *


# FORM tests
class QueryFormUnitTests(TestCase):

    def test_invalid_ip(self):
        form = QueryForm(data={"query": "100abc", "query_choice": "ip"})

        self.assertEqual(
            form.errors["query"], ["Invalid IP Address"]
        )

    def test_valid_ipv4(self):
        ip = "127.0.0.1"
        form = QueryForm(data={"query": ip, "query_choice": "ip"})

        self.assertTrue(form.is_valid())


    def test_valid_ipv6(self):
        ip = "2001:db8:3333:4444:5555:6666:7777:8888"
        form = QueryForm(data={"query": ip, "query_choice": "ip"})

        self.assertTrue(form.is_valid())
    

    def test_invalid_hostname(self):
        invalid_hostname = "-.test.com/wrong"
        form = QueryForm(data={"query": invalid_hostname, "query_choice": "hostname"})

        self.assertEqual(
            form.errors["query"], ["invalid hostname"]
        )


    def test_valid_hostname(self):
        valid_hostname = "test.test.com"
        form = QueryForm(data={"query": valid_hostname, "query_choice": "hostname"})

        self.assertTrue(form.is_valid())


class DashboardIntegrationTests(TestCase):
    #use an authorized client for testing
    def setUp(self):
        self.user = User.objects.create(username='testuser', password="TESTPA$$1234")
        self.user.save()
        self.client = Client()

        self.client.force_login(self.user)

    #test get request to dashboard
    def test_get(self):
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed('index.html')

    #test post from initial page load with IP search
    def test_dash_post_success(self):
        response = self.client.post("/dashboard/", data={"query_choice" : "ip", "query": "128.2.42.10"})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response["Location"], "/dashboard/dash_query/")
        self.assertTemplateUsed('index.html')

        #test post from initial page load, with hostname search
    def test_dash_host_post_success(self):
        response = self.client.post("/dashboard/", data={"query_choice" : "hostname", "query": "google.ca"})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response["Location"], "/dashboard/dash_query/")
        self.assertTemplateUsed('index.html')
    
    #test from search on /dashboard/dash_query/ URL, with IP search
    def test_dash_research_post_success(self):
        response = self.client.post("/dashboard/dash_query/", data={"query_choice" : "ip", "query": "128.2.42.10"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed('index.html')

        #test from search on /dashboard/dash_query/ URL, with hostname search
    def test_dash_research_post_success(self):
        response = self.client.post("/dashboard/dash_query/", data={"query_choice" : "ip", "query": "128.2.42.10"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed('index.html')



class DashSearchIntegrationTests(TestCase):
#use an authorized client for testing
    def setUp(self):
        self.user = User.objects.create(username='testuser', password="TESTPA$$1234")
        self.user.save()
        self.client = Client()

        self.client.force_login(self.user)

#test that view returns context
    def test_results_lists(self):
        response = self.client.get(reverse("dash_query"))
        self.assertIsNotNone(response.context)




# TASKS TESTS

#test functions used in search to filter API responses from ZoomEye
class TasksUnitTests(TestCase):

    #use test JSON to test tasks that filter data 
    def test_zoomeye_filters(self):

        with open(os.path.join(settings.BASE_DIR, 'static/test_data_zoomeye.json')) as test_file :
            test_dict = test_file.read()
            filtered_list = zoomeye_filter_host(test_dict)

            #get the keys from the filtered dictionary
            filtered_keys = list(filtered_list[0].keys())

            #test that there are 20 entries in the dictionary (the number of entries
            # in test_data_zoomeye.json)
            self.assertEqual(len(filtered_list), 20)

            #test that the fields extracted match the key list in tasks.py
            self.assertEqual(filtered_keys, included_keys_host)

            #now test the filter function that further filters results for the results list
            minimal_list = zoomeye_filter_short(filtered_list)
            minimal_keys = list(minimal_list[0].keys())

            #test that there ate still 20 entries
            self.assertEqual(len(minimal_list), 20)

            #test the keys match from tasks.py 
            self.assertEqual(minimal_keys, filter_keys)

    #test that uses a keyword search succesfully
    #a known vulnerable system - should not return empty dict
    def test_get_cve_list_keyword_search(self):
        result = get_cve_list("Apache", "2.2.4")
        self.assertIsNotNone(result)

    #test that uses an exact CPE match succesfully
    #a known vulnerable system - should not return empty dict
    #uses parameters that should match with initial CPE API query
    def test_get_cve_list_matched_cpe_name(self):
        result = get_cve_list("http_server", "2.2.4")
        self.assertIsNotNone(result)

    #test that an empty dictionary is returned with an invalid name given
    def test_get_cve_list_unmatched_cpe_name(self):
        result = get_cve_list("NonExistantName123456", "nonexistant application")
        self.assertEqual(len(result), 0)


class DashSelectIntegrationTests(TestCase):

    #use an authorized client for testing
    def setUp(self):
        self.user = User.objects.create(username='testuser', password="TESTPA$$1234")
        self.user.save()
        self.client = Client()

        self.client.force_login(self.user)

        #set up session data
        with open(os.path.join(settings.BASE_DIR, 'static/test_data_zoomeye.json')) as test_file :
            test_dict = test_file.read()
            
            session = self.client.session
            session['full_dict']  = zoomeye_filter_host(test_dict)
            session.save()

    #test post from list on dashboard
    def test_select_post_success(self):
        response = self.client.post(reverse("dash_select"), data={"id" : "result_sel_form", "selected_ind": "0"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "results.html")

        #ensure context is containing proper items
        correct_context_keys = {'ind', 'selected_dict', 'port_dict', 'cve_list'}
        self.assertTrue(correct_context_keys <= set( response.context.keys()) )
        

        #using knowne test data from setup in session, test that 
        #the correct item was selected
        self.assertEqual(response.context["selected_dict"]["ip"], "179.125.32.13")

        #ensure CVE list is detected for selection (#0 an Apache server 2.4.54)
        self.assertFalse(len(response.context["cve_list"]) == 0)

    def test_device_empty_cve_list(self):
        response = self.client.post(reverse("dash_select"), data={"id" : "result_sel_form", "selected_ind": "3"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "results.html")
    
        #ensure CVE list is empty because based on the test data it should be
        self.assertTrue(len(response.context["cve_list"]) == 0)