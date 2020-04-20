import urllib.request, urllib.parse, urllib.error
import json
import datetime
from datetime import timedelta
import perfectoactions
import pandas
from multiprocessing import Pool, Process
import os
import traceback
import sys
import multiprocessing
import uuid


def send_request(url, content):
    try:
        response = urllib.request.urlopen(url.replace(" ", "%20"))
    except Exception as e:
        return e
    sys.stdout.flush()
    return response

def send_request_for_repository(url, content, key):
    response = send_request(url, content)

    if("500" in str(response)):
        print(url)
        raise RuntimeError("Failed to list repository items - Repository item: " + key + "  was not found in media repository, url:" + str(url))

    text = response.read().decode("utf-8")
    map = json.loads(text)
    return map

def getActualDate(map):
   #date is fetched here
   try:
       date = map['item']['creationTime']['formatted']
   except KeyError:
       return "";
   dateOnly = date.split("T")
   return datetime.datetime.strptime(dateOnly[0], "%Y-%m-%d")

def getPastDate(days):
   #Logic for fetching past days based on user preference
   today = datetime.datetime.today()
   pastDate = timedelta(days=int(days))
   return today - pastDate

def sendAPI(resource_type, resource_key, operation):
    url = perfectoactions.get_url(str(resource_type), resource_key, operation)
    admin = os.environ['repo_admin']
    if "true" in admin.lower():
        url += "&admin=" + "true"
    return send_request_for_repository(url, "", resource_key)

def fetch_details(i, exp_number, result, exp_list):
    """ fetches details"""
    if i == exp_number:
         if ":" in result:
             exp_list = exp_list.append(result.split(":", 1)[1].replace("'","").strip())
         else:
             exp_list = exp_list.append('-')
    return exp_list

def run_commands(value):
    # Get date of repository items
    FINAL_LIST = []
    DAYS = os.environ['repo_days']
    DELETE = os.environ['repo_delete']
    map = sendAPI(os.environ['repo_resource_type'], value, "info")
    actualDate = getActualDate(map)
    if not (str(actualDate) == ""):
             expectedDate = getPastDate(DAYS)
             expDate = str.split(str(expectedDate), " ")
             actDate = str(str.split(str(actualDate), " ")[0])
             #DELETES the item if older than expected date
             if(actualDate < expectedDate) :
                 print(perfectoactions.colored("File: " + value + " with actual creation date: " + actDate + " was created before " + str(DAYS) + " days.", "red"))
                  # DELETE item from the repository
                 if(DELETE.lower() == "true") :
                     map = sendAPI(os.environ['repo_resource_type'], value, "delete")
                     status = map['status']
                     if (status != "Success") :
                          FINAL_LIST.append('File:' + value + ';Created on:' + actDate + ';Comparison:is older than;Days:' + DAYS + ';Deleted?:Unable to delete!;')
                          raise RuntimeError("Repository item " + value + " was not deleted")
                     else:
                          FINAL_LIST.append('File:' + value + ';Created on:' + actDate + ';Comparison:is older than;Days:' + DAYS + ';Deleted?:Yes;')
                 else:
                      FINAL_LIST.append('File:' + value + ';Created on:' + actDate + ';Comparison:is older than;Days:' + DAYS + ';Deleted?:No;')
             else:
                  print(perfectoactions.colored("File: " + value + " with actual creation date: " + actDate + " was created within the last " + str(DAYS) + " days.", "green"))
#                   FINAL_LIST.append('File:' + value + ';Created on:' + actDate + ';Comparison:is younger than;Days:' + DAYS + ';Deleted?:No;')
    fileName = uuid.uuid4().hex + '.txt'
    file = os.path.join(perfectoactions.TEMP_DIR, 'repo_results', fileName)
    f= open(file,"w+")
    f.write(str(FINAL_LIST))
    f.close()

def manage_repo(resource_key):
    # Get list of repository items
    map = sendAPI(os.environ['repo_resource_type'], resource_key, "list")
    try:
        itemList = map['items']
        sys.stdout.flush()
    except:
        raise RuntimeError("There are no List of repository items inside the folder: " + resource_key)
    #debug
#     for value in itemList:
#         run_commands(value)
    pool_size = multiprocessing.cpu_count() * 2
    repo_folder_pool = multiprocessing.Pool(processes=pool_size, maxtasksperchild=2)
    try:
         FINAL_LIST = repo_folder_pool.map(run_commands, itemList)
         repo_folder_pool.close()
    except Exception:
        repo_folder_pool.close()
        repo_folder_pool.terminate()
        print(traceback.format_exc())  
        sys.exit(-1)
    
def deleteOlderFiles(resource_type, delete, admin, repo_paths, days ):
    os.environ['repo_delete'] = delete
    os.environ['repo_days'] = days
    os.environ['repo_resource_type'] = resource_type
    os.environ['repo_admin'] = admin
    perfectoactions.create_dir(os.path.join(perfectoactions.TEMP_DIR , 'repo_results'), True)
    I=0
    REPO_LIST = repo_paths.split(",")
    #debug:
#     for repo in REPO_LIST:
#         manage_repo(repo)
    procs = []
    for li in REPO_LIST:
           proc = Process(target=manage_repo, args=(str(li),))
           procs.append(proc)
           proc.start()
    try:
       for proc in procs:
           proc.join()
       for proc in procs:
           proc.terminate()
    except Exception:
       proc.terminate()
       print(traceback.format_exc())
       sys.exit(-1)

    for r, d, f in os.walk(os.path.join(perfectoactions.TEMP_DIR , 'repo_results')):
        for file in f:
            if ".txt" in file:
                with open(os.path.join(r, file)) as f:
                    with open(os.path.join(r, "Final_Repo.txt"), "a") as f1:
                        for line in f:
                            f1.write(line)
                            f1.write("\n")
    file = os.path.join(perfectoactions.TEMP_DIR, 'repo_results', 'Final_Repo.txt')
    try:
        f= open(file,"r")
    except FileNotFoundError:
        raise Exception( 'No repository items found')
        sys.exit(-1)
    result = f.read()
    f.close()
    FINAL_LIST = result.split("\n")
    
    file = []
    created = []
    comparison = []
    days = []
    deleted = []
    final_dict = {}
    for lists in FINAL_LIST:
        if lists is not None:
            if len(lists) > 0:
                new_result = str(lists).split(";")
                i = 0
                for result in new_result:
                    if "Deleted?:" in result:
                        fetch_details(i, new_result.index(result, i), str(result).replace("]",''), deleted)
                    if "File:" in result:
                        fetch_details(i, new_result.index(result, i), result, file)
                    if "Created on:" in result:
                        fetch_details(i, new_result.index(result, i), result, created)
                    if "Comparison:" in result:
                        fetch_details(i, new_result.index(result, i), result, comparison)
                    if "Days:" in result:
                        fetch_details(i, new_result.index(result, i), result, days)
                    i = i + 1
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.max_colwidth', 100)
    pandas.set_option('colheader_justify', 'center')
    final_dict =  {'File': file, 'Created On': created, 'Comparison': comparison, 'Days': days, 'Deleted?': deleted}
    df = pandas.DataFrame(final_dict)
    df = df.sort_values(by ='File')
    df.style.set_properties(**{'text-align': 'left'})
    sys.stdout.flush()
    return df
