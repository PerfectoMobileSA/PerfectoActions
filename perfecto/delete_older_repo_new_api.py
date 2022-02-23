#!/usr/bin/env python
import sys
import os
import json
from requests import get, delete
from pandas import DataFrame
import pandas as pd
import datetime
from datetime import datetime, timedelta
from re import MULTILINE
from colorama import init
from json2html import *


"""
    Dictionary
"""


class my_dictionary(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value


def getPastDate(days):
    # Logic for fetching past days based on user preference
    today = datetime.today()
    pastDate = timedelta(days=int(float(days)))
    return today - pastDate


"""
    flattens the json
"""


def flatten_json(nested_json, exclude=[""]):
    """Flatten json object with nested keys into a single level.
        Args:
            nested_json: A nested json object.
            exclude: Keys to exclude from output.
        Returns:
            The flattened json object if successful, None otherwise.
    """
    out = {}

    def flatten(x, name="", exclude=exclude):
        if type(x) is dict:
            for a in x:
                if a not in exclude:
                    flatten(x[a], name + a + "/")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "/")
                i += 1
        else:
            out[name[:-1]] = x
    flatten(nested_json)
    return out


"""
    Retrieve a list of repository items
"""


def retrieve_repository_items(page, artifactType):
    payload = payLoad(page, artifactType)
    url = "https://" + os.environ["cloudName"] + \
        ".app.perfectomobile.com"
    api_url = url + "/repository/api/v1/artifacts?"
    # creates http get request with the url, given parameters (payload) and header (for authentication)
    r = get(
        api_url, params=payload, headers={
            "PERFECTO_AUTHORIZATION": os.environ["securityToken"]}
    )
    print(str(api_url))
    print(str(payload))
    return r.content


"""
    delete repository items
"""


def delete_repository_items(artifactType):
    url = "https://" + os.environ["cloudName"] + \
        ".app.perfectomobile.com"
    api_url = url + "/repository/api/v1/artifacts?artifactLocator=" + artifactType
    # creates http delete request with the url and header (for authentication)
    r = delete(
        api_url, headers={
            "PERFECTO_AUTHORIZATION": os.environ["securityToken"]}
    )
    print(str(api_url))
    return r.content


"""
    Creates payload for reporting API
"""


def payLoad(page, artifactType):
    payload = my_dictionary()
    payload.add("pageSize", 2000)
    payload.add("skip", page * 2000)
    if artifactType is not None:
        payload.add("artifactType", artifactType)
    return payload


"""
   gets start date to milliseconds
"""


def pastDateToMS(startDate, daysOlder):
    dt_obj = datetime.strptime(
        startDate + " 00:00:00,00", "%Y-%m-%d %H:%M:%S,%f"
    ) - timedelta(days=daysOlder)
    millisec = dt_obj.timestamp() * 1000
    oldmilliSecs = round(int(millisec))
    return oldmilliSecs


"""
   manage perfecto repository
"""


def manageRepo(value, DAYS, delete, artifactType=None):
    page = 0
    df = DataFrame()
    truncated = True
    resources = []
    while truncated == True:
        print(
            "Current page: "
            + str(page)
        )
        executions = retrieve_repository_items(page, artifactType)
        print("Output:\n" + str(executions))
        # Loads JSON string into JSON object
        executions = json.loads(executions)
        if "{'userMessage': 'Failed decoding the offline token:" in str(executions):
            raise Exception("please change the security token for your cloud")
        try:
            executionList = executions["artifacts"]
            keys_to_remove = ["username", "artifactMetadata",
                              "groupKey"]
            executionList = [
                {k: v for k, v in d.items() if k not in keys_to_remove} for d in executionList]
        except TypeError:
            import traceback
            traceback.print_exc()
            raise Exception(
                "Unable to find matching records")
        if len(executionList) == 0:
            print("0 test executions")
            break
        else:
            truncated = executions["truncated"]
            if page >= 1:
                resources.extend(tuple(executionList))
            else:
                resources.extend(tuple(executionList))
            page += 1
    if len(resources) > 0:
        jsonDump = json.dumps(resources)
        resources = json.loads(jsonDump)

        print("Total executions: " + str(len(resources)))
        lists = [flatten_json(x) for x in resources]
        df = DataFrame(lists)
        cols_to_drop = ['usageMetadata/lastUpdateTime',
                        'usageMetadata/lastDownloadTime']
        df.drop(cols_to_drop, axis=1, errors='ignore', inplace=True)
        df['date'] = pd.to_datetime(
            df['usageMetadata/creationTime'], unit='ms')
        expectedDate = getPastDate(DAYS)
        # filter items before expected date
        df = df[(df['date'] < expectedDate)]
        # filter items starting with expected value
        df = df[df['artifactLocator'].astype(str).str.startswith(value)]

        print(len(df))
        print(df.head(1000))

        for row in df.itertuples(index=True, name='Pandas'):
            if(row.artifactLocator.startswith(value)):
                if(str(delete).lower() == "true"):
                    print("deleting " + row.artifactLocator)
                    delete_repository_items(row.artifactLocator)
                else:
                    print("not deleting " + row.artifactLocator)

    return df


def main():
    """
    Runs the perfecto actions and reports
    """
    try:
        start_time = datetime.now().replace(microsecond=0)
        init()
        os.environ["cloudName"] = ""
        os.environ["securityToken"] = ""
        value = 'GROUP:Group/APAC/iOS/'
        DAYS = 90
        artifactType = "IOS"
        delete = "true"
        df = manageRepo(value, DAYS, delete, artifactType)
        end = datetime.now().replace(microsecond=0)
        print("".join(["Total Time taken:", str(end - start_time)]))
    except Exception as e:
        raise Exception("Oops!", e)


if __name__ == "__main__":
    main()
    sys.exit()
