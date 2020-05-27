import json 
from easydict import EasyDict as edict
from collections import Counter
import tzlocal
import pandas
import datetime as dt
import time
from IPython.display import HTML
import glob
import os
import re
import numpy as np
import sys

def get_report_details(item, temp, name, criteria):
    if name + "=" in item:
        temp = str(item).split("=")[1]
        criteria += " : " + name + ": " + temp 
    return temp, criteria

# report = "report|jobName=test|jobNumber=1"
report = "report|jobName=test|jobNumber=1|startDate=123|endDate=1223|consolidate=/Users/temp"
try:
  criteria = ""
  jobName = ""
  jobNumber = ""
  startDate = ""
  endDate = ""
  consolidate = ""
  temp = ""
  report_array = report.split("|")
  for item in report_array:
       if "jobName" in item: jobName, criteria =  get_report_details(item, temp, "jobName", criteria)
       if "jobNumber" in item: jobNumber, criteria =  get_report_details(item, temp, "jobNumber", criteria)
       if "startDate" in item: startDate, criteria =  get_report_details(item, temp, "startDate", criteria)
       if "endDate" in item: endDate, criteria =  get_report_details(item, temp, "endDate", criteria)
       if "consolidate" in item: consolidate, criteria =  get_report_details(item, temp, "consolidate", criteria)
      #  print("j" + jobName)
except Exception as e:
  raise Exception( "Verify parameters of report, split them by | seperator" + str(e) )
  sys.exit(-1)
print(criteria)
print(jobName)
print(jobNumber)
print(startDate)
print(endDate)
print(consolidate)



    # if "jobName=" in item:
    #       jobName = str(item).split("=")[1]
    #       criteria = " : job: " + jobName 
    # if "jobNumber=" in item:
    #     jobNumber = str(item).split("=")[1]
    #     criteria += " ; number: " + jobNumber   
    # if "startDate=" in item:
    #     startDate = str(item).split("=")[1]
    #     criteria += " ; startDate: " + startDate
    # if "endDate=" in item:
    #     endDate = str(item).split("=")[1]
    #     criteria += " ; endDate: " + endDate    
    # if "consolidate=" in item:
    #     consolidate = str(item).split("=")[1]
    #     criteria += " ; consolidate: " + consolidate  