### PerfectoActions
<br /> 
PerfectoActions can execute device operations like clean up, reboot and get network settings in parallel across/ specific perfecto devices and showcase their results in a final report.

## Prerequisites:
    
    1. Install [Python](https://www.python.org/downloads/) version 3 and above.
    
    2. Install [pip](https://pip.pypa.io/en/stable/installing/)
    
    3. Run the following command:
            `pip install perfectoactions`
    
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
    
5.  get network settings like airplane mode, wifi and data for only available galaxy devices in parallel: <br /> 
    `perfectoactions -c "<<CLOUD NAME>>" -s "<<SECURITY TOKEN>>"  -a "get_network_settings:true" -d "model:Galaxy.*"`

6. Re-runs the same execution with a specified sleep time: <br /> 
    `perfectoactions -c "<<CLOUD NAME>>" -s "<<SECURITY TOKEN>>" -r 1`
    
7. Skip's output in html format: ( for faster results in terminal/cmd ) <br /> 
    `perfectoactions -c "<<CLOUD NAME>>" -s "<<SECURITY TOKEN>>" -o false`
    
    
## Scheduling in Windows:
    
    1. Open Task Scheduler.
    2. Create a new task.
    3. Name it as preferred.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/win/1.png" height="360" width="760"/>

    4. Click on trigger and then click on New
    5. Set the trigger as preferred. E.g. Select daily to run daily.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/win/2.png" height="360" width="760"/>

    6. Click on Actions and then click on New
    7. Browse the actions.bat file, a sample file is found it samples folder.
    8. Make sure to edit the actions.bat file and supply your preferred arguments to perfectoactions [ line:2 ]
    9. perfectoactions will be triggered.
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/win/3.png" height="360" width="760"/>

    10. Results will be displayed
<img src="https://github.com/PerfectoMobileSA/Device_actions_reporter/blob/master/docs/win/4.png" height="360" width="760"/>

## Scheduling in Mac:

## Scheduling from Jenkins:
    
## Python package dev ( only for advanced users who wants to edit the python package ):

Increase the version in setup.py and run the following to upload to test pypi: <br /> 

    python3 -m pip install --user --upgrade setuptools wheel twine
    rm -rf build dist
    python3 setup.py clean --all
    python3 setup.py sdist bdist_wheel
    python3 -m twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/* -r testpypi
    

Using Python’s Virtual for testing:<br /> 

    python3 -m pip install --user --upgrade virtualenv
    virtualenv env
    source env/bin/activate

Install test package in local:<br /> 

    pip3 uninstall perfectoactions
    pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple perfectoactions
    

Python code performance check:<br /> 

    Navigate to perfecto folder in terminal/cmd. 
    pip install snakeviz
    python -m cProfile -o temp.dat perfectoactions.py
    snakeviz temp.dat
