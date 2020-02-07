"""device health check"""
import urllib.request
import os
import urllib.parse
import urllib.error
from xml.dom import minidom
import json
import re
import configparser
from termcolor import colored
import shutil
import pandas as pd
import webbrowser
import matplotlib.pyplot as plt
import io
import base64
import cython 
import pylab as pl
import time
import sys
import traceback
from multiprocessing import freeze_support, Pool
""" Microsoft Visual C++ required, cython required for pandas installation, """
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
CONFIG = configparser.ConfigParser()
CONFIG.read("./Config.ini")

try: 
    if sys.argv[1]:
        HOST = sys.argv[1]
except:
    HOST = CONFIG.get("Env", "host")

try:
    if sys.argv[2]:
        TOKEN = sys.argv[2]
except:
    TOKEN = CONFIG.get("Env", "token")

try:
    if sys.argv[3]:
        if "get_network_settings:true" in sys.argv[3]:
            GET_NETWORK_SETTINGS = True
        else:
            GET_NETWORK_SETTINGS = False
except:
    if "true" in CONFIG.get("Env", "get_network_settings").lower():
        GET_NETWORK_SETTINGS = True
    else:
        GET_NETWORK_SETTINGS = False
        
try:
    if sys.argv[3]:
        if "reboot:true" in sys.argv[3]:
            REBOOT = True
        else:
            REBOOT = False
except:
    if "true" in CONFIG.get("Env", "reboot").lower():
        REBOOT = True
    else:
        REBOOT = False        
        
try:
    if sys.argv[3]:
        if "cleanup:true" in sys.argv[3]:
            CLEANUP = True
        else:
            CLEANUP = False
except:
    if "true" in CONFIG.get("Env", "cleanup").lower():
        CLEANUP = True
    else:
        CLEANUP = False
        
try:
    if sys.argv[4]:
            GET_DEVICE_PARAMETERS = sys.argv[4]
    else:
        GET_DEVICE_PARAMETERS = ""
except:
    GET_DEVICE_PARAMETERS = CONFIG.get("Env", "GET_DEVICE_PARAMETERS")


# Do not change these variable
RESOURCE_TYPE = "handsets"
START_EXECUTION = False
if GET_NETWORK_SETTINGS or REBOOT or CLEANUP:
    START_EXECUTION = True

def send_request(url):
    """send request"""
#    print("Submitting", url)
    response = urllib.request.urlopen(url.replace(" ", "%20"))
#    rc = response.getcode()
#    print("rc =", rc)
    return response

def send_request_with_json_response(url):
    """send request"""
    response = send_request(url)
    text = response.read().decode("utf-8")
    maps = json.loads(text)
    return maps

def send_request_with_xml_response(url):
    """send reqeust"""
    response = send_request(url)
    text = response.read().decode("utf-8")
    xmldoc = minidom.parseString(text)
    return xmldoc

def send_request2(url):
    """send request"""
    response = send_request(url)
    text = response.read().decode("utf-8")
    return text

def get_url(resource, resource_id, operation):
    """End execution"""
    url = "https://" + HOST + ".perfectomobile.com/services/" + resource
    if resource_id != "":
        url += "/" + resource_id
    query = urllib.parse.urlencode({"operation": operation, "securityToken": TOKEN})
    url += "?" + query
    return url

def getregex_output(response, pattern1, pattern2):
    """regex"""
    matches = re.finditer(pattern1, response, re.MULTILINE)
    for match in matches:
        match_item = str(re.findall(pattern2, match.group()))
        match_item = match_item.replace(':"', "").replace('"', "")
        match_item = match_item.replace("'", "").replace("[", "")
        match_item = match_item.replace("]", "").replace(",test", "").replace(",timer.system", "").replace('description":"','')
        return str(match_item)

def device_command(exec_id, device_id, operation):
    """Runs device command"""
    url = get_url("executions/" + str(exec_id), "", "command")
    url += "&command=" + "device"
    url += "&subcommand=" + operation
    url += "&param.deviceId=" + device_id
    send_request_with_json_response(url)

def end_execution(exec_id):
    """End execution"""
    url = get_url("executions/"+ str(exec_id), "", "end")
    send_request_with_json_response(url)

def start_execution():
    """start execution"""
    url = get_url("executions", "", "start")
    response = send_request2(url)
    exec_id = getregex_output(response, r'executionId\"\:\"[\w\d@.-]+\"', ":\".*$")
    return exec_id

def get_device_list_response(resource, command, status, in_use):
    """get_device_list_response"""
    url = get_url(resource, "", command)
    url += "&status=" + status
    if in_use != "":
        url += "&inUse=" + in_use
    if  len(GET_DEVICE_PARAMETERS.split("=")) >= 2:
        for item in GET_DEVICE_PARAMETERS.split(";"):
            if "=" in item:
                url += "&" + item.split("=")[0] + "=" + item.split("=")[1]
    xmldoc = send_request_with_xml_response(url)
    return xmldoc

def get_device_ids(xmldoc):
    """get_device_ids"""
    device_ids = xmldoc.getElementsByTagName('deviceId')
    return device_ids

def get_handset_count(xmldoc):
    """get_handset_count"""
    handset_elements = xmldoc.getElementsByTagName('handset')
    return len(handset_elements)

def exec_command(exec_id, device_id, cmd, subcmd):
    """exec_commands"""
    url = get_url("executions/" + str(exec_id), "", "command")
    url += "&command=" + cmd
    url += "&subcommand=" + subcmd
    url += "&param.deviceId=" + device_id
    response = send_request2(url)
    status = getregex_output(response, r'(description\"\:\".*\",\"timer.system|returnValue\"\:\".*\",\"test)', ":\".*$")
    return str(status)

def get_network_setting(deviceid_color):
    """get_network_setting"""
    deviceid_color = str(deviceid_color)
    device_id = deviceid_color.split("||",1)[0]
    color = deviceid_color.split("||",1)[1];
    desc = deviceid_color.split("||",2)[2]
    fileName = device_id + '.txt'
    file = os.path.join(PROJECT_ROOT, 'results', fileName)  
    try:
        status = "Results="
                #update dictionary
        url = get_url(RESOURCE_TYPE, device_id, "info")
        xmldoc = send_request_with_xml_response(url)
        modelElements = xmldoc.getElementsByTagName('model')
        model = modelElements[0].firstChild.data
        osElements = xmldoc.getElementsByTagName('os')
        osDevice = osElements[0].firstChild.data
        osVElements = xmldoc.getElementsByTagName('osVersion')
        osVersion = osVElements[0].firstChild.data
        osVersion =  osDevice + " " + osVersion
        try:
            operatorElements = xmldoc.getElementsByTagName('operator')
            operator = operatorElements[0].childNodes[0].data
            phElements = xmldoc.getElementsByTagName('phoneNumber')
            phoneNumber = phElements[0].firstChild.data
        except:
            operator = "NA"
            phoneNumber ="NA"
        if "green"  in color:
            if START_EXECUTION:
                #Get execution id
                EXEC_ID = start_execution()
                #open device:
                device_command(EXEC_ID, device_id, "open")
                if CLEANUP:
                    if not "iOS" in osDevice: 
                        print("cleanup: " + model)
                        status += "cleaning up:" + exec_command(EXEC_ID, device_id, "device", "clean")
                        status += ";"
                    else:
                        status +="cleanup:NA;"
                if REBOOT:
                    print("rebooting: " + model)
                    status += "reboot:" + exec_command(EXEC_ID, device_id, "device", "reboot")
                if GET_NETWORK_SETTINGS:
                    print("getting network status of : " + model)
                    networkstatus = exec_command(EXEC_ID, device_id, "network.settings", "get").replace("{","").replace("}","")
                #Close device
                device_command(EXEC_ID, device_id, "close")
                #End execution
                end_execution(EXEC_ID)
        else:
            networkstatus = ",,"

        if GET_NETWORK_SETTINGS:
                final_string =  "status=" + desc + ", deviceId='" + device_id + "', model=" + str(model) + ", version=" + str(osVersion) + ", operator="+ \
                str(operator) + ", phoneNumber=" + str(phoneNumber) + ", " + str(networkstatus) + ", " + str(status)
        else:
            final_string = "status=" + desc + ", deviceId='" + device_id + "', model=" + str(model) + ", version=" + str(osVersion) + ", operator="+ \
            str(operator) + ", phoneNumber=" + str(phoneNumber) + ",,,, " + str(status)
        final_string = re.sub(r"^'|'$", '', final_string)
        f= open(file,"w+")
        f.write(str(final_string))
        f.close() 
        return final_string
    except Exception as e:
        raise Exception("Oops!" , e )
        
        if not os.path.isfile('results/' + device_id + '.txt'):
            if GET_NETWORK_SETTINGS:
                final_string =  "status=ERROR" + ",deviceId='" + device_id + "',,,,,,,,"
            else:
                final_string = "status=ERROR" + ",deviceId='" + device_id + "',,,,,"
            f= open(file,"w+")
            f.write(str(final_string))
            f.close() 
        return final_string

def get_list(command, status, in_use, color, desc):
    """get_list"""
    # Verifies each device id based on statuses
    i = 0
    RESPONSE = get_device_list_response(RESOURCE_TYPE, command, status, in_use)
    DEVICE_IDS = get_device_ids(RESPONSE)
    device_list = []
    if get_handset_count(RESPONSE) > 0:
         for i in range(get_handset_count(RESPONSE)):
            device_id = DEVICE_IDS[i].firstChild.data
            device_list.append(device_id + "||" + color + "||" + desc)
            device_list = [x for x in device_list if x != 0]
         if len(device_list) > 0:
            agents = 5
            chunksize = 3
            pool = Pool(processes=agents)
            try:
                print("Found " + str(len(device_list)) + " device count with status: " + desc)
                output = pool.map(get_network_setting, device_list, chunksize)
                pool.close()  
                pool.join()
            except Exception:
                pool.close()
                pool.terminate()
                print(traceback.format_exc())

def fetch_details(i, exp_number, result, exp_list):
    """ fetches details"""
    if i == exp_number:
         if "=" in result:
             exp_list = exp_list.append(result.split("=", 1)[1].replace("'","").strip())
         else:
             exp_list = exp_list.append('-')
    return exp_list

def fig_to_base64(fig):
    img = io.BytesIO()
    plt.savefig(img, format='png',
                bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.getvalue())
     
def prepare_html():
    """ prepare_html """
    print(colored("Final Devices list:", "magenta"))
    #copies all device status to final summary
    for r, d, f in os.walk(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'results')):
        for file in f:
            if ".txt" in file:
                with open(os.path.join(r, file)) as f:
                    with open(os.path.join(r, "Final_Summary.txt"), "a") as f1:
                        for line in f:
                            f1.write("\n")
                            f1.write(line)                        
    file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'results', 'Final_Summary.txt')
    try:
        f= open(file,"r")
    except Exception as e:
        raise Exception("Oops!" , e  ,"occured." + 'No devices found/ Error in fetching devices!')
    result = f.read()
    f.close() 
    results = result.split("\n")
    #export to CSV
    new_dict = {}
    deviceids = []
    status = []
    model = []
    osVersion = []
    operator = []
    phonenumber = []
    airplanemode = []
    wifi = []
    data = []
    action_results = []
    for result in results:
        if len(result) > 0:
            new_result = result.split(",")
            new_list = []
            i = 0
            for result in new_result:
                fetch_details(i, 0, result, status)
                fetch_details(i, 1, result, deviceids)
                fetch_details(i, 2, result, model)
                fetch_details(i, 3, result, osVersion)
                fetch_details(i, 4, result, operator)
                fetch_details(i, 5, result, phonenumber)
                fetch_details(i, 6, result, airplanemode)
                fetch_details(i, 7, result, wifi)
                fetch_details(i, 8, result, data)
                fetch_details(i, 9, result, action_results)
                new_list.append(result)
                i = i + 1
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 100)
    pd.set_option('colheader_justify', 'center') 
    if GET_NETWORK_SETTINGS or REBOOT or CLEANUP:
        new_dict =  {'Status': status, 'Device Id': deviceids, 'Model': model, 'OS Version': osVersion, 'Operator': operator, 'Phone number': phonenumber, 'AirplaneMode' : airplanemode, 'Wifi': wifi, 'Data': data, 'Results' : action_results}
    else:
        new_dict =  {'Status': status, 'Device Id': deviceids, 'Model': model, 'OS Version': osVersion, 'Operator': operator, 'Phone number': phonenumber}
    df = pd.DataFrame(new_dict)
    df = df.sort_values(by ='Model')
    df = df.sort_values(by ='Status')
    df.reset_index(drop=True, inplace=True)
    pl.figure()
    pl.suptitle("Device Models")
    df['Model'].value_counts().plot(kind='barh', stacked=True)
    encoded = fig_to_base64('results/model.png')
    model = '<img src="data:image/png;base64, {}"'.format(encoded.decode('utf-8'))
    pl.figure()
    pl.suptitle("Device Status")
    df['Status'].value_counts().plot(kind='barh', stacked=True)
    encoded = fig_to_base64('results/status.png')
    barh = '<img src="data:image/png;base64, {}"'.format(encoded.decode('utf-8'))
    pl.figure()
    pl.suptitle("OS Versions")
    df['OS Version'].value_counts().plot(kind='barh', stacked=True)
    encoded = fig_to_base64('results/version.png')
    version = '<img src="data:image/png;base64, {}"'.format(encoded.decode('utf-8'))
    pl.figure()
    pl.suptitle("SIM Operators")
    df['Operator'].value_counts().plot(kind='barh', stacked=True)
    encoded = fig_to_base64('results/operator.png')
    operator = '<img src="data:image/png;base64, {}"'.format(encoded.decode('utf-8'))
    df = df.sort_values(by ='Model')
    df = df.sort_values(by ='Status')
    df.to_csv('results/output.csv', index=False)
    html_string = '''
    <html>
      <head>
	  <meta name="viewport" content="width=device-width, initial-scale=1">
       <meta content="text/html; charset=iso-8859-2" http-equiv="Content-Type">
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
		     <head><title>''' + HOST.upper() + ''' Device Status Report</title>
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
        <script>
        $(document).ready(function(){{
          $("#myInput").on("keyup", function() {{
            var value = $(this).val().toLowerCase();
            $("tbody tr").filter(function() {{
              $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            }});
          }});
        }});
        </script>
		<script type="text/javascript">
	           $(document).ready(function(){{
               $("#slideshow > div:gt(0)").hide();

               setInterval(function() {{
                 $('#slideshow > div:first')
                   .fadeOut(500)
                   .next()
                   .fadeIn(500)
                   .end()
                   .appendTo('#slideshow');
               }}, 4000);
                   var InfiniteRotator =
                     {{
                         init: function()
                         {{
                             //initial fade-in time (in milliseconds)
                             var initialFadeIn = 1000;
                             //interval between items (in milliseconds)
                             var itemInterval = 4000;
                             //cross-fade time (in milliseconds)
                             var fadeTime = 400;
                             //count number of items
                             var numberOfItems = $('#slideshow').length;
                             //set current item
                             var currentItem = 0;
                             //show first item
                             $('#slideshow').eq(currentItem).fadeIn(initialFadeIn);
                             //loop through the items
                             var infiniteLoop = setInterval(function(){{
                                 $('#slideshow').eq(currentItem).fadeOut(fadeTime);
                                 if(currentItem == numberOfItems -1){{
                                     currentItem = 0;
                                 }}else{{
                                     currentItem++;
                                 }}
                                 $('#slideshow').eq(currentItem).fadeIn(fadeTime);
                             }}, itemInterval);
                         }}
                     }};
                     InfiniteRotator.init();
				$("tbody tr:contains('Disconnected')").css('background-color','#fcc');
				$("tbody tr:contains('ERROR')").css('background-color','#fcc');
				$("tbody tr:contains('Un-available')").css('background-color','#fcc');
				$("tbody tr:contains('Busy')").css('background-color','#fcc');
                var table = document.getElementsByTagName("table")[0];
				var rowCount = table.rows.length;
				for (var i = 0; i < rowCount; i++) {{
					if ( i >=1){{
                    available_column_number = 0;
                    device_id_column_number = 1;
						if (table.rows[i].cells[available_column_number].innerHTML == "Available") {{
                            for(j = 0; j < table.rows[0].cells.length; j++) {{
								table.rows[i].cells[j].style.backgroundColor = '#e6fff0';
                                    if(j=table.rows[0].cells.length){{
                                            if (table.rows[i].cells[(table.rows[0].cells.length - 1)].innerHTML.includes("failed")) {{
                                                    table.rows[i].cells[j].style.color = '#660001';
                                                    table.rows[i].cells[j].style.backgroundColor = '#FFC2B5';
                                            }}
							}}
                             }}
							var txt = table.rows[i].cells[device_id_column_number].innerHTML;
							var url = 'https://''' + HOST.upper() + '''.perfectomobile.com/nexperience/main.jsp?applicationName=Interactive&id=' + txt;
							var row = $('<tr></tr>')
							var link = document.createElement("a");
							link.href = url;
							link.innerHTML = txt;
							link.target = "_blank";
							table.rows[i].cells[device_id_column_number].innerHTML = "";
							table.rows[i].cells[device_id_column_number].append(link);
						}}else{{
							for(j = 0; j < table.rows[0].cells.length; j++) {{
								table.rows[i].cells[j].style.color = '#660001';
                                     table.rows[i].cells[j].style.backgroundColor = '#FFC2B5';
							}}
						}}
					}}
				}}
             }});
             function myFunction() {{
              var x = document.getElementById("myTopnav");
              if (x.className === "topnav") {{
                x.className += " responsive";
              }} else {{
                x.className = "topnav";
              }}
            }}
		</script>
		<meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
      <link rel="stylesheet" type="text/css" href="../df_style.css"/>
      <div class="bg"></div>
    	<div class="bg bg2"></div>
    	<div class="bg bg3"></div>
    	<div>
      <body bgcolor="#FFFFED">
	  	<div class="topnav" id="myTopnav">
		  <a href="output.html" class="active">Home</a>
		  <a href="https://''' + HOST.upper() + '''.perfectomobile.com" target="_blank" class="active">''' + HOST.upper() + ''' Cloud</a>
          <a href="https://developers.perfectomobile.com" target="_blank" class="active">Docs</a>
          <a href="https://www.perfecto.io/services/professional-services-implementation" target="_blank" class="active">Professional Services</a>
		  <a href="https://support.perfecto.io/" target="_blank" class="active">Perfecto Support</a>
		  <a href="javascript:void(0);" class="icon" onclick="myFunction()">
			<i class="fa fa-bars"></i>
		  </a>
		</div>
        <div style="text-align: center">
        <h3> <font color=#333 ><b>''' + HOST.upper() + ''' Cloud's Device Status Report</font></h3></b>
         <a href="https://perfecto.io/" target="_blank" class="site-logo"><img src="https://www.perfecto.io/sites/perfecto.io/themes/custom/perfecto/logo.svg" alt="Perfecto support"></a>
         </br></br>
		 <input id="myInput" type="text" placeholder="Filter.."><br><br>
         <div style="overflow-x:auto;">
         {table}
         <p align="center" style="font-size:10px;font-family: "Trebuchet MS", Helvetica, sans-serif;" >Device query parameters: <i>''' + GET_DEVICE_PARAMETERS + ''' </i></p> <br>
        <div class="container" align="center" id="slideshow" >
          <div class="mySlides">
            <div class="numbertext">4 / 4</div>
            ''' + barh + ''' alt="Device Status" style="width:90%;">
          </div>     
          <div class="mySlides">
            <div class="numbertext">1 / 4</div>
          ''' + model + ''' alt="Model" style="width:90%;">
          </div>
          <div class="mySlides">
          <div class="numbertext">2 / 4</div>
          ''' + version + ''' alt="Version" style="width:90%;">
          </div>          
          <div class="mySlides">
          <div class="numbertext">3 / 4</div>
          ''' + operator + ''' alt="Operator" style="width:90%;">
          </div>       
          </div>
        </div>
          <footer>
          <p>Best viewed in Chrome/Safari.</p>
          </footer>
      </body>
      </div>
    </html>
    '''
    
    # OUTPUT AN HTML FILE
    with open('results/output.html', 'w') as f:
        f.write(html_string.format(table=df.to_html(classes='mystyle', index=False)))
    time.sleep(3)
    webbrowser.open('file://' + os.path.realpath('results/output.html'))
    i = 0
    results.sort()
    for i in range(len(results)):
        if "Available" in results[i]:
            print(colored(results[i], "green"))
        else:
            print(colored(results[i], "red"))
        i = i + 1     
    print('Results: file://' + os.path.realpath('results/output.html'))
    

if __name__ == '__main__':
    freeze_support()    
    #create results path
    directory = 'results'
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        shutil.rmtree(directory)
        os.makedirs(directory)
 
#    shutil.copyfile('df_style.css','results/df_style.css')
    get_list("list", "connected", "true", "red", "Busy")     
    get_list("list", "disconnected", "", "red",  "Disconnected")
    get_list("list", "unavailable", "", "red", "Un-available")
    get_list("list", "connected", "false", "green", "Available")
    prepare_html()
