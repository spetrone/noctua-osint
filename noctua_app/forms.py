from django import forms
from django.core.validators import validate_ipv46_address
from django.core.exceptions import ValidationError
import re




class QueryForm(forms.Form):
    QUERY_CHOICES= [
    ('ip', 'IP'),
    ('hostname', 'Host Name'),
    ('device', 'Device')
    ]
    query_choice= forms.CharField(label='Type of query:', widget=forms.Select(choices=QUERY_CHOICES))
    query = forms.CharField(label=' ', max_length=100, required=True)

    #validate ip addresses and domain names
    def clean_query(self):

        data = self.cleaned_data['query']

        #validate ip addresses
        if self.cleaned_data['query_choice'] == 'ip' :
            try:
                validate_ipv46_address(data) # Success
            except :
                raise ValidationError("Invalid IP Address")

        #validate hostnames
        elif self.cleaned_data['query_choice'] == 'hostname' :
            if data[-1] == ".":
                data = data[:-1] 
            allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
            if not all(allowed.match(x) for x in data.split(".")) :
                raise ValidationError("invalid hostname")
 
        # return data
        return data



   