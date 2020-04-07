# PerfectoActions

Official documentation: https://developers.perfectomobile.com/pages/viewpage.action?pageId=50922763

  PerfectoActions can execute device operations like clean up, reboot and get network settings in parallel across all/ specific perfecto devices and showcase their results in a fully responsive, accessibility friendly, html report which has direct access to open an available device, search for devices in the displayed html table, show case direct API results for clean & restart commands, raise a perfecto support ticket, open your perfecto cloud, navigate to perfecto documentation, full devices list information in excel format and showcases device status, model, OS versions & SIM operator graphs.

## Recommended system configuration:
    
    1. 8 GB Ram and above
    
    2. 2.20 GHz multi core processors and above
    

## Prerequisites:
    
  1. Install [Python](https://www.python.org/downloads/) version 3+ and make sure that python version > 3+ is set as default.
    
  2. Install [pip](https://pip.pypa.io/en/stable/installing/)
    
  3. Run the following command from command prompt/ terminal:
  
           pip3 install perfectoactions -U
    
## Usage:

    perfectoactions [-h] [-c cloud_name] [-s security_token]
                       [-d [device_list_parameters]]
                       [-t [Different types of Device Connection status]]
                       [-a [actions]] [-r [refresh]] [-o [output in html]]
                       

    optional arguments:
      -h, --help            show this help message and exit
      -c cloud_name, --cloud_name cloud_name
                            Perfecto cloud name. (E.g. demo)
      -s security_token, --security_token security_token
                            Perfecto Security Token/ Pass your Perfecto's username/email
                            and password in user:password format
      -d [device_list_parameters], --device_list_parameters [device_list_parameters]
                            Perfecto get device list API parameters to limit
                            device list. Support all API capabilities which
                            selects devices based on reg ex/strings, Leave it
                            empty to select all devices
      -t [Different types of Device Connection status], --device_status [Different types of Device Connection status]
                            Different types of Device Connection status. Values:
                            all. This will showcase all the device status like
                            Available, Disconnected, un-available & Busy. Note:
                            Only Available devices will be shown by default
      -a [actions], --actions [actions]
                            Perfecto actions seperated by semi-colon. E.g.
                            reboot:true;cleanup:true;get_network_settings:true
      -r [refresh], --refresh [refresh]
                            Refreshes the page with latest device status as per
                            provided interval in seconds
      -o [output in html], --output [output in html]
                            output in html. Values: true/false. Default is true
                        
                        
## Examples:

1. List all available devices: <br />
 
    `perfectoactions -c "<<CLOUD NAME>>" -s "<<SECURITY TOKEN>>"`
    

2. List all available devices using perfecto username and password: <br />
 
    `perfectoactions -c "<<CLOUD NAME>>" -s "<<username/email>>:<<password>>"`
    

3. List all devices irrespective on device status: <br />
 
    `perfectoactions -c "<<CLOUD NAME>>" -s "<<SECURITY TOKEN>>" -t all`
    

4. Reboot, clean up and get network settings for all devices in parallel: <br />
 
    `perfectoactions -c "<<CLOUD NAME>>" -s "<<SECURITY TOKEN>>" -t "all" -a "reboot:true;cleanup:true;get_network_settings:true"`
    

5. Limit the selection of devices by applying any/multiple Get Devices List parameters and regular expressions using the following syntax: {param1}:{value1};{param2}:{value2}
 
	`perfectoactions -c "<<CLOUD NAME>>" -s "<<SECURITY TOKEN>>" -d "model:Galaxy S.*;description:.*Genesis;dynamicField.ipa:Test-Android.*"`

6. get network settings like airplane mode, wifi and data for only available galaxy devices in parallel: <br />
 
    `perfectoactions -c "<<CLOUD NAME>>" -s "<<SECURITY TOKEN>>"  -a "get_network_settings:true" -d "model:Galaxy.*"`

7. Re-runs the same execution with a specified sleep time: <br />
 
    `perfectoactions -c "<<CLOUD NAME>>" -s "<<SECURITY TOKEN>>" -r 1`
    

8. Skip's output in html format: ( for faster results in terminal/cmd ) <br />
 
    `perfectoactions -c "<<CLOUD NAME>>" -s "<<SECURITY TOKEN>>" -o false`
    

Notes: </br>
	We recommend that you assign a unique description or dynamicField for devices that are applicable for reboot and utilize the -d parameter for reboot. See the Limit the selection of the devices example.</br>
	PerfectoActions is subject to the same restrictions and limitations as the Reboot device API, with regard to locked phones and limitations to reboot devices by certain manufacturers. For details, see Devices Restart Limitation.  </br>

### Note:

    1. Make sure active scripting is enabled in IE browser.
    2. Preferred browsers are Chrome and Safari.
    3. Kindly use python version 3 and above.

## Experimental proxy: ( Yet to be tested )
    
    Configure proxies by setting environment variables HTTP_PROXY and HTTPS_PROXY. E.g. in mac:

        export HTTP_PROXY="10.10.1.10:3128"
        export HTTPS_PROXY="10.10.1.10:1080"
    
    To use HTTPS Basic Auth with your proxy, try this: https://user:password@host:port

        export HTTP_PROXY="https://user:pass@10.10.1.10:3128/"
        export HTTPS_PROXY="https://user:pass@10.10.1.10:3128/"
    
    Note: avoid using special characters such as :,@ in username and passwords
    
## Scheduling in Windows:
    
    1. Open Task Scheduler.
    2. Create a new task.
    3. Name it as preferred.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/win/1.png" height="360" width="760"/>

    4. Click on trigger and then click on New.
    5. Set the trigger as preferred. E.g. Select daily to run daily.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/win/2.png" height="360" width="760"/>

    6. Click on Actions and then click on New.
    7. Browse the actions.bat file, a sample .bat file is found here: https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/samples/actions.bat.
    8. Make sure to edit the actions.bat file and supply your preferred arguments to perfectoactions [ line:2 ].
    9. perfectoactions will be triggered based on the trigger.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/win/3.png" height="360" width="760"/>

    10. Results will be displayed as like the image below if -o is not set to false in perfectoactions arguments.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/win/4.png" height="360" width="760"/>

## Scheduling in Mac:

    1. Type "which perfectoactions" in terminal to get the physical path of perfectoactions.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/mac/mac1.png" height="360" width="760"/>

    2. Download a sample shell file from  here: https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/samples/actions.sh.
    3. Edit the downloaded .sh file.
    4. Set the physical path of perfectoactions and applicable arguments.
    5. Open terminal and navigate to the location where the actions.sh was downloaded and run the following command:
        chmod +x ./actions.sh 
    6. You need to grant cron full disk access. Drag /usr/sbin/cron into the Full Disk Access area in System Preferences > Security & Privacy > Privacy tab.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/mac/mac2.png" height="360" width="760"/>


    7. Run the terminal command : "crontab -e”
    8. Press i.
    9. Enter the following in the below syntax:

            {cron} /{path of actions.sh}/actions.sh >/{path of logs}/stdout.log 2>/{path of error logs}/stderr.log

        E.g.:
            30 2 * * * /Users/genesisthomas/Downloads/actions.sh  >/tmp/stdout.log 2>/tmp/stderr.log

    10. Note: 30 2 * * * runs the cron job at 2:30 am everyday.
    11. Press ":wq!” to save the file and click on OK in the trailing popup.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/mac/mac3.png" height="360" width="760"/>


    12. Run the command "crontab -l" to see whether the cron job is activated/ enabled.
    13. Verify the results.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/mac/mac4.png" height="360" width="760"/>



## Scheduling from Jenkins:
    1. Login into Jenkins
    2. Go to Manage Jenkins -> Manage Plugins and install HTML Publisher plugin.
    3. Go back to Manage Jenkins page and then navigate to Script Console page.
    4. Paste the below in console and click on Run. 
        System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "")
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/jenkins/1.png" height="360" width="760"/>        
        
    5. Clear browser history and cache, restart browser and login into Jenkins.
    6. Create a new free style job in Jenkins.
    7. Enable Build periodically under Build triggers section.
    8. Enter your preferred cron schedule under schedule section.
        E.g. "30 2 * * *" will run the job at 2:30 am everyday
    9. Enable "Delete workspace before build starts" under Build Environment section.
    10. WINDOWS:
        Add a build step: Execute Windows batch command and add the below commands inside it:
        
            pip install -U perfectoactions
            del /s /q "C:\Users\<<Windows user name>>\AppData\Local\Temp\output\*.*"
            perfectoactions -c <<CLOUD NAME, e.g. demo>>  -s "<<SECURITY TOKEN>>" <<ADDITIONAL ARGUMENTS AS APPLICABLE>>
            xcopy /s "C:\Users\<<Windows user name>>\AppData\Local\Temp\output" .
            EXIT /B
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/jenkins/2.png" height="360" width="760"/>        
   
        MAC:
        Add a build step: Execute shell and add the below commands inside it:
            <<PATH TO PIP>>/pip3 install -U perfectoactions
            rm -rf "/tmp/output/*.*"
            perfectoactions -c <<CLOUD NAME, e.g. demo>> -s "<<SECURITY TOKEN>>" <<ADDITIONAL ARGUMENTS AS APPLICABLE>>
            cp /tmp/output/result.html .
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/jenkins/3.png" height="360" width="760"/>   

    Note: 
       1. Update preferred values within <<>> as applicable
       2. Use which command in terminal to find path of pip3/perfectoactions. E.g. "which pip3" will show the path of pip3.
       
    11. Add post-build Actions: Archive the artifacts with files to archive: result.html (Screenshots above)
    12. Add post-build Actions: Publish HTML reports with index page: result.html (Screenshots above)
    13. Run the job to find the results.html being published as a html report.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/jenkins/4.png" height="360" width="760"/>   