import json
import requests

#define the filter set for zoomeye queries
included_keys_host = ["rdns", "ip", "ssl", "location", "os", "port", "service", "hostname", "device", "version", "portinfo"]

#keys used for function for filtering dictionary to include only those keys
filter_keys = ["rdns", "ip" , "port", "service"]


#define function for filtering host data from zoomeye
def zoomeye_filter_host(data) :
    full_dict = json.loads(data)
    match_list = full_dict.get("matches")
    filter_list = []
    for match_dict in match_list :
        filter_dict = {}
        for k in included_keys_host :
            #go an extra layer if needed
            if k in match_dict.keys() :
                filter_dict[k] = match_dict[k]
            else :
                for val in match_dict.values() :
                    if type(val) is dict and k in val.keys() :
                        filter_dict[k] = val[k]
        filter_list.append(filter_dict)
    return filter_list

    #define function for filtering host data from zoomeye for list display
    #on index.html (only shows a small subset of the attributes)
def zoomeye_filter_short(data_list) :
    filter_list = []
    for d in data_list :
        sub_dict = {}
        for k in filter_keys :
            if k in d.keys() :
                sub_dict[k] = d[k]
        filter_list.append(sub_dict)
    return filter_list



def get_cve_list(app, version) :
    
    #create a list to pass to template; will return empty list if no vulns
    cve_list = []
    
    #more input validation
    if app and version and app != "" and version != "" :

 

        #build query
        query = app + ":" + version
        cpe_name = "" #initialize empty string for testing later

        #get cpe name
        cpe_response  = requests.get("https://services.nvd.nist.gov/rest/json/cpes/2.0?cpeMatchString=cpe:2.3:a:*:" + query)
        if cpe_response :#200
            cpe_results = json.loads(cpe_response.text)
        
            if int(cpe_results["totalResults"]) > 0 :
                #use first entry
                print(cpe_results["products"][0]["cpe"]["cpeName"])
                cpe_name = cpe_results["products"][0]["cpe"]["cpeName"]

        elif not cpe_response or cpe_results["totalResults"] > 0 : # do a keyword search query instead for more generic search
                query_string = app + " " + version 
                cpe_response  = requests.get("https://services.nvd.nist.gov/rest/json/cpes/2.0?keywordSearch=" + query_string)
                cpe_results = json.loads(cpe_response.text)
    
                if int(cpe_results["totalResults"]) > 0 :
                    cpe_name = cpe_results["products"][0]["cpe"]["cpeName"]

        #continue if a cpe name was retrieved, otherwise return empty list, don't do cve search
        if cpe_name != "" :
            cve_query = "cpeName=" + cpe_name
        else :
            cve_query = "keywordSearch=" + version# the generic query built from function args 
            print(cve_query)

        nvd_response = requests.get("https://services.nvd.nist.gov/rest/json/cves/2.0?"+ cve_query)
        # nvd_response_text = nvd_response.text

        if nvd_response : #200
            response_dict = json.loads(nvd_response.text)

            #extract specific attributes and filter the dictionary
            vulnerabilities = response_dict["vulnerabilities"]

            if vulnerabilities : # if not empty

                for entry in vulnerabilities :
                    sub_dict = {}
                    #add id
                    sub_dict["id"] = entry["cve"]["id"]
                    #add severity
                    metrics = entry["cve"]["metrics"]
                    if metrics.items() :
                        if "cvssMetricV31" in metrics.keys() :
                            sub_dict["severity"] = entry["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["baseSeverity"]
                        elif "cvssMetricV2" in metrics.keys() :
                            sub_dict["severity"] = entry["cve"]["metrics"]["cvssMetricV2"][0]["baseSeverity"]
                    cve_list.append(sub_dict)
                    
    return cve_list

