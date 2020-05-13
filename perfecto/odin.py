import numpy as np
from pandas.io.json import json_normalize
import pandas
import requests
import json
import urllib.request, urllib.parse, urllib.error
from collections import Counter
from urllib.error import HTTPError
from datetime import datetime, timedelta
import re
from easydict import EasyDict as edict
import time
import webbrowser
import os
from dateutil.parser import parse
import sys
import configparser

"""
    This is the payload based on only start and end date
"""


def payloadNoJob(oldmilliSecs, current_time_millis, page):
    payload = {
        "startExecutionTime[0]": oldmilliSecs,
        "endExecutionTime[0]": current_time_millis,
        "_page": page,
    }
    return payload


"""
    This is the payload based on only start and end date
"""


def payloadJob(jobName, jobNumber, page):
    payload = {
        "jobName[0]": jobName,
        "jobNumber[0]": jobNumber,
        "_page": page,
    }
    return payload


"""
    Retrieve a list of test executions within the last month
    :return: JSON object contains the executions
"""


def retrieve_tests_executions(daysOlder, page):
    endTime = datetime.strptime(str(endDate) + " 23:59:59,999", "%d/%m/%Y %H:%M:%S,%f")
    print("endExecutionTime:" + str(endTime))
    millisec = endTime.timestamp() * 1000
    current_time_millis = round(int(millisec))
    oldmilliSecs = pastDateToMS(startDate, daysOlder)
    if not jobName:
        payload = payloadNoJob(oldmilliSecs, current_time_millis, page)
    else:
        payload = payloadJob(jobName, jobNumber, page)
    # creates http geat request with the url, given parameters (payload) and header (for authentication)
    r = requests.get(
        api_url, params=payload, headers={"PERFECTO_AUTHORIZATION": OFFLINE_TOKEN}
    )
    # print entire response
    # #print(str(r.content))
    print(str(r.url))
    return r.content


"""
    sends API request
"""


def send_request(url):
    try:
        response = urllib.request.urlopen(url)
    except HTTPError as e:
        content = e.read()
        response = content
    return response


"""
    sends API request and gets a json response
"""


def send_request_with_json_response(url):
    response = send_request(url)
    text = response.read().decode("utf-8")
    map = json.loads(text)
    return map


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
   gets the top failed device pass count, handset errors and device/ desktop details
"""


def getDeviceDetails(device, deviceFailCount):
    devicePassCount = 0
    errorsCount = 0
    i = 0
    df = pandas.DataFrame(resources)
    df = pandas.DataFrame([flatten_json(x) for x in resources])

    import tzlocal

    df["startTime"] = pandas.to_datetime(df["startTime"].astype(int), unit="ms")
    df["startTime"] = (
        df["startTime"].dt.tz_localize("utc").dt.tz_convert(tzlocal.get_localzone())
    )
    df["startTime"] = df["startTime"].dt.strftime("%d/%m/%Y %H:%M:%S")

    df["endTime"] = pandas.to_datetime(df["endTime"].astype(int), unit="ms")
    df["endTime"] = (
        df["endTime"].dt.tz_localize("utc").dt.tz_convert(tzlocal.get_localzone())
    )
    df["endTime"] = df["endTime"].dt.strftime("%d/%m/%Y %H:%M:%S")

    df["Duration"] = pandas.to_datetime(df["endTime"]) - pandas.to_datetime(
        df["startTime"]
    )
    df = df[df['Duration']> pandas.Timedelta(0)]

    custom_columns = [
        "name",
        "owner",
        "startTime",
        "endTime",
        "Duration",
        "status",
        "job/name",
        "job/number",
        "job/branch",
        "reportURL",
        "failureReasonName",
        "platforms/0/os",
        "platforms/0/deviceId",
        "platforms/0/deviceType",
        "platforms/0/mobileInfo/manufacturer",
        "platforms/0/mobileInfo/model",
        "platforms/0/osVersion",
        "platforms/0/browserInfo/browserType",
        "platforms/0/browserInfo/browserVersion",
        "id",
        "externalId",
        "uxDuration",
        "platforms/0/screenResolution",
        "platforms/0/location",
        "platforms/0/mobileInfo/imei",
        "platforms/0/mobileInfo/phoneNumber",
        "platforms/0/mobileInfo/distributor",
        "platforms/0/mobileInfo/firmware",
        "platforms/0/selectionCriteriaV2/0/name",
        "platforms/0/selectionCriteriaV2/1/name",
        "platforms/0/selectionCriteriaV2/2/name",
        "platforms/0/selectionCriteriaV2/2/value",
        "platforms/0/customFields/0/name",
        "platforms/0/customFields/0/value",
        "videos/0/startTime",
        "videos/0/endTime",
        "videos/0/format",
        "videos/0/streamingUrl",
        "videos/0/downloadUrl",
        "videos/0/screen/width",
        "videos/0/screen/height",
        "tags/0",
        "tags/1",
        "tags/2",
        "tags/3",
        "tags/4",
        "tags/5",
        "tags/6",
        "executionEngine/version",
        "project/name",
        "project/version",
        "automationFramework",
        "parameters/0/name",
        "parameters/0/value",
        "parameters/1/name",
        "parameters/1/value",
        "parameters/2/name",
        "parameters/2/value",
        "parameters/3/name",
        "parameters/3/value",
        "parameters/4/name",
        "parameters/4/value",
        "parameters/5/name",
        "parameters/5/value",
        "parameters/6/name",
        "parameters/6/value",
        "parameters/7/name",
        "parameters/7/value",
        "parameters/8/name",
        "parameters/9/name",
        "parameters/9/value",
        "parameters/10/name",
        "parameters/10/value",
        "parameters/11/name",
        "parameters/11/value",
        "parameters/12/name",
        "parameters/12/value",
        "platforms/0/mobileInfo/operator",
        "platforms/0/mobileInfo/operatorCountry",
        "tags/7",
        "parameters/8/value",
        "platforms/0/selectionCriteriaV2/3/name",
        "platforms/0/selectionCriteriaV2/3/value",
        "platforms/0/selectionCriteriaV2/4/name",
        "platforms/0/selectionCriteriaV2/4/value",
        "platforms/0/selectionCriteriaV2/5/name",
        "platforms/0/selectionCriteriaV2/5/value",
        "platforms/0/selectionCriteriaV2/6/name",
        "platforms/0/selectionCriteriaV2/6/value",
        "platforms/0/selectionCriteriaV2/7/name",
        "platforms/0/selectionCriteriaV2/7/value",
        "customFields/0/name",
        "customFields/0/value",
        "customFields/1/name",
        "customFields/1/value",
        "parameters/13/name",
        "parameters/13/value",
        "artifacts/0/type",
        "artifacts/0/path",
        "artifacts/0/zipped",
        "artifacts/1/type",
        "artifacts/1/path",
        "artifacts/1/contentType",
        "artifacts/1/zipped",
        "artifacts/2/type",
        "artifacts/2/path",
        "artifacts/2/zipped",
        "message",
        "tags/8",
        "tags/9",
        "artifacts/0/contentType",
        "tags/10",
        "tags/11",
        "artifacts/2/contentType",
        "platforms/1/deviceId",
        "platforms/1/deviceType",
        "platforms/1/os",
        "platforms/1/osVersion",
        "platforms/1/screenResolution",
        "platforms/1/location",
        "platforms/1/mobileInfo/imei",
        "platforms/1/mobileInfo/manufacturer",
        "platforms/1/mobileInfo/model",
        "platforms/1/mobileInfo/distributor",
        "platforms/1/mobileInfo/firmware",
        "platforms/1/selectionCriteriaV2/0/name",
        "platforms/1/selectionCriteriaV2/0/value",
        "platforms/1/customFields/0/name",
        "platforms/1/customFields/0/value",
        "videos/1/startTime",
        "videos/1/endTime",
        "videos/1/format",
        "videos/1/streamingUrl",
        "videos/1/downloadUrl",
        "videos/1/screen/width",
        "videos/1/screen/height",
        "tags/12",
        "tags/13",
        "tags/14",
        "tags/15",
        "tags/16",
        "platforms/1/mobileInfo/phoneNumber",
    ]
    df = df[df.columns.intersection(custom_columns)]
    df = df.reindex(columns=custom_columns)
    df = df.dropna(axis=1, how="all")
    df.to_csv("temp.csv", index=False)
    with open("temp.html", "a") as _file:
        _file.write(df.head().to_html() + "\n\n")
    for resource in resources:
        try:
            test_execution = resource  # retrieve a test execution
            # get devices which fails
            platforms = test_execution["platforms"]  # retrieve the platforms
            platform = platforms[0]
            actual_deviceID = platform["deviceId"]
            if actual_deviceID in device:
                status = test_execution["status"]
                if status in "PASSED":
                    devicePassCount += 1
                elif status in "FAILED":
                    message = test_execution["message"]
                    if "HANDSET_ERROR" in message:
                        errorsCount += 1
                deviceType = platform["deviceType"]
                if "DESKTOP" in deviceType:
                    browserInfo = platform["browserInfo"]
                    topDeviceFailureDict[device] = [
                        platform["os"] + "_" + platform["osVersion"],
                        browserInfo["browserType"]
                        + "_"
                        + browserInfo["browserVersion"],
                        devicePassCount,
                        deviceFailCount,
                        errorsCount,
                    ]
                else:
                    mobileInfo = platform["mobileInfo"]
                    topDeviceFailureDict[device] = [
                        mobileInfo["manufacturer"],
                        mobileInfo["model"],
                        devicePassCount,
                        deviceFailCount,
                        errorsCount,
                    ]
        except IndexError:
            continue
        except KeyError:
            continue

        printProgressBar(
            i + 1,
            len(resources),
            prefix="Fetching Device details in Progress:",
            suffix="Complete",
            length=50,
        )
        i += 1


"""
   gets the total pass count of each failed case
"""


def getPassCount(testName):
    testNamePassCount = 0
    i = 0
    for resource in resources:
        try:
            test_execution = resource  # retrieve a test execution
            name = test_execution["name"]

            if testName in name:
                status = test_execution["status"]
                if status in "PASSED":
                    testNamePassCount += 1
        except IndexError:
            continue
        except KeyError:
            continue
        printProgressBar(
            i + 1,
            len(resources),
            prefix="Pass % calculation API in Progress:",
            suffix="Complete",
            length=50,
        )
        i += 1
    return testNamePassCount


"""
   gets fail and pass count of each test case and assigns it to a dict
"""


def getTCDetails(tcName, failureCount):
    topTCFailureDict[tcName] = [failureCount, getPassCount(tcName)]


"""
   calculates the percetage of a part and whole number
"""


def percentageCalculator(part, whole):
    if int(whole) > 0:
        calc = (100 * float(part) / float(whole), 0)
        calc = round(float((calc[0])), 2)
    else:
        calc = 0
    return calc


"""
   gets start date to milliseconds
"""


def pastDateToMS(startDate, daysOlder):
    dt_obj = datetime.strptime(
        startDate + " 00:00:00,00", "%d/%m/%Y %H:%M:%S,%f"
    ) - timedelta(days=daysOlder)
    print("startExecutionTime:" + str(dt_obj))
    millisec = dt_obj.timestamp() * 1000
    oldmilliSecs = round(int(millisec))
    return oldmilliSecs


"""
   gets past pass percentage of tests
"""


def pastPassPercentageCalculator(daysOlder):
    totalPassCount = 0
    totalTCCount = 0
    i = 0
    for resource in resources:
        try:
            totalTCCount += 1
            test_execution = resource  # retrieve a test execution
            status = test_execution["status"]
            if status in "PASSED":
                totalPassCount += 1
        except IndexError:
            continue
        except KeyError:
            continue
        printProgressBar(
            i + 1,
            len(resources),
            prefix="TC Pass % based on older days API in Progress:",
            suffix="Complete",
            length=50,
        )
        i += 1
    return str(percentageCalculator(totalPassCount, totalTCCount))


"""
   gets' Perfecto reporting API responses, creates dict for top device failures, auto suggestions and top tests failures and prepared json
"""


def prepareReport():
    page = 1
    i = 0
    truncated = True
    failureList = {}
    cleanedFailureList = {}
    device_Dictionary = {}
    totalFailCount = 0
    totalPassCount = 0
    totalUnknownCount = 0
    totalTCCount = 0
    labIssuesCount = 0
    scriptingIssuesCount = 0
    orchestrationIssuesCount = 0
    testNameFailureList = {}
    suggesstionsDict = {}
    global topDeviceFailureDict
    global topTCFailureDict
    global resources
    failureList.clear()
    cleanedFailureList.clear()
    testNameFailureList.clear()
    device_Dictionary.clear()
    resources.clear()
    suggesstionsDict.clear()
    while truncated == True:
        print(
            "Retrieving all the test executions in your lab. Current page: "
            + str(page)
            + ". Hold On!!"
        )
        executions = retrieve_tests_executions(0, page)
        # Loads JSON string into JSON object
        executions = json.loads(executions)
        if "{'userMessage': 'Failed decoding the offline token:" in str(executions):
            raise Exception("please change the offline token for your cloud")
        if "userMessage': 'Missing Perfecto-TenantId header" in str(executions):
            raise Exception("Check the cloud name and security tokens")
        executionList = executions["resources"]
        if len(executionList) == 0:
            print("there are no test executions for that period of time")
            break
        else:
            # print(str(executions))
            metadata = executions["metadata"]
            truncated = metadata["truncated"]
            if page >= 1:
                resources.extend(executionList)
            else:
                resources.append(executionList)
            page += 1

    jsonDump = json.dumps(resources)
    resources = json.loads(jsonDump)
    totalTCCount = len(resources)
    print("Total executions: " + str(len(resources)))
    for resource in resources:
        try:
            #            totalTCCount += 1
            test_execution = resource  # retrieve a test execution
            status = test_execution["status"]
            if status in "FAILED":
                totalFailCount += 1
                # get failed test names
                name = test_execution["name"]
                if name in testNameFailureList:
                    testNameFailureList[name] += 1
                else:
                    testNameFailureList[name] = 1
                # get devices which fails
                platforms = test_execution["platforms"]  # retrieve the platforms
                platform = platforms[0]
                actual_deviceID = platform["deviceId"]
                if actual_deviceID in device_Dictionary:
                    device_Dictionary[actual_deviceID] += 1
                else:
                    device_Dictionary[actual_deviceID] = 1
                # get error messages
                message = test_execution["message"]
                if message in failureList:
                    failureList[message] += 1
                else:
                    failureList[message] = 1
            elif status in "PASSED":
                totalPassCount += 1
            elif status in "UNKNOWN":
                totalUnknownCount += 1
        except IndexError:
            continue
        except KeyError:
            continue

    # Top 5 device which failed
    topDeviceFailureDict.clear()
    deviceFailureDict = Counter(device_Dictionary)
    for device, deviceFailCount in deviceFailureDict.most_common(5):
        getDeviceDetails(device, deviceFailCount)

    # Top 5 failure tests along with pass count
    topTCFailureDict.clear()
    testNameFailureListDict = Counter(testNameFailureList)
    for failedTestName, failedTestNamesCount in testNameFailureListDict.most_common(5):
        getTCDetails(str(failedTestName), failedTestNamesCount)

    # last 7/14 days pass % calculator
    # print("14D" + str(pastPassPercentageCalculator(14)))
    print("total unique fail count:" + str(len(failureList)))
    i = 0
    failureListFileName = CQL_NAME + "_failures" + ".txt"
    print(
        "transfering all failure reasons to: %s"
        % (os.path.join(os.path.abspath(os.curdir), failureListFileName))
    )
    open(failureListFileName, "w").close
    for commonError, commonErrorCount in failureList.items():
        for labIssue in labIssues:
            if re.search(labIssue, commonError):
                labIssuesCount += commonErrorCount
                break
        for orchestrationIssue in orchestrationIssues:
            if re.search(orchestrationIssue, commonError):
                orchestrationIssuesCount += commonErrorCount
                break
        error = commonError
        regEx_Filter = "Build info:|For documentation on this error|at org.xframium.page|Scenario Steps:| at WebDriverError|\(Session info:|XCTestOutputBarrier\d+|\s\tat [A-Za-z]+.[A-Za-z]+.|View Hierarchy:|Got: |Stack Trace:|Report Link|at dalvik.system"
        if re.search(regEx_Filter, error):
            error = str(re.compile(regEx_Filter).split(error)[0])
            if "An error occurred." in error:
                error = error.split("An error occurred. Stack Trace:")[1]
        if re.search("error: \-\[|Fatal error:", error):
            error = str(re.compile("error: \-\[|Fatal error:").split(error)[1])
        if error.strip() in cleanedFailureList:
            cleanedFailureList[error.strip()] += 1
        else:
            cleanedFailureList[error.strip()] = commonErrorCount
        scriptingIssuesCount = totalFailCount - (
            orchestrationIssuesCount + labIssuesCount
        )
        with open(failureListFileName, "a", encoding="utf-8") as myfile:
            myfile.write(
                error.strip() + "\n*******************************************\n"
            )
        printProgressBar(
            i + 1,
            len(failureList),
            prefix="chart preparation in Progress:",
            suffix="Complete",
            length=50,
        )
        i += 1

    # Top 5 failure reasons
    topFailureDict = {}

    failureDict = Counter(cleanedFailureList)
    for commonError, commonErrorCount in failureDict.most_common(5):
        topFailureDict[commonError] = int(commonErrorCount)

    # reach top errors and clean them
    i = 0
    for commonError, commonErrorCount in topFailureDict.items():
        if "Device not found" in error:
            error = (
                "Raise a support case as *|*"
                + commonError.strip()
                + "*|* as it occurs in *|*"
                + str(commonErrorCount)
                + "*|* occurrences"
            )
        elif "Cannot open device" in error:
            error = (
                "Reserve the device/ use perfecto lab auto selection feature to avoid:  *|*"
                + commonError.strip()
                + "*|* as it occurs in *|*"
                + str(commonErrorCount)
                + "*|* occurrences"
            )
        else:
            error = (
                "Fix the error: *|*"
                + commonError.strip()
                + "*|* as it occurs in *|*"
                + str(commonErrorCount)
                + "*|* occurrences"
            )
        suggesstionsDict[error] = commonErrorCount
        printProgressBar(
            i + 1,
            len(topFailureDict),
            prefix="Generation of suggestions in Progress:",
            suffix="Complete",
            length=50,
        )
        i += 1
    eDict = edict(
        {
            "snapshotDate": str(finalDate),
            "last24h": int(percentageCalculator(totalPassCount, totalTCCount)),
            "lab": labIssuesCount,
            "orchestration": orchestrationIssuesCount,
            "scripting": scriptingIssuesCount,
            "unknowns": totalUnknownCount,
            "executions": totalTCCount,
            "recommendations": [
                {
                    "rank": 1,
                    "recommendation": "-",
                    "impact": 0,
                    "impactMessage": "null",
                },
                {
                    "rank": 2,
                    "recommendation": "-",
                    "impact": 0,
                    "impactMessage": "null",
                },
                {
                    "rank": 3,
                    "recommendation": "-",
                    "impact": 0,
                    "impactMessage": "null",
                },
                {
                    "rank": 4,
                    "recommendation": "-",
                    "impact": 0,
                    "impactMessage": "null",
                },
                {
                    "rank": 5,
                    "recommendation": "-",
                    "impact": 0,
                    "impactMessage": "null",
                },
            ],
            "topProblematicDevices": [
                {
                    "rank": 1,
                    "model": "",
                    "os": "",
                    "id": "",
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                },
                {
                    "rank": 2,
                    "model": "",
                    "os": "",
                    "id": "",
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                },
                {
                    "rank": 3,
                    "model": "",
                    "os": "",
                    "id": "",
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                },
                {
                    "rank": 4,
                    "model": "",
                    "os": "",
                    "id": "",
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                },
                {
                    "rank": 5,
                    "model": "",
                    "os": "",
                    "id": "",
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                },
            ],
            "topFailingTests": [
                {"rank": 1, "test": "", "failures": 0, "passes": 0},
                {"rank": 2, "test": "", "failures": 0, "passes": 0},
                {"rank": 3, "test": "", "failures": 0, "passes": 0},
                {"rank": 4, "test": "", "failures": 0, "passes": 0},
                {"rank": 5, "test": "", "failures": 0, "passes": 0},
            ],
        }
    )
    jsonObj = edict(eDict)

    if float(percentageCalculator(totalUnknownCount, totalTCCount)) >= 30:
        suggesstionsDict[
            "# Fix the unknowns. The unknown script ratio is too high (%) : "
            + str(percentageCalculator(totalUnknownCount, totalTCCount))
            + "%"
        ] = percentageCalculator(
            totalPassCount + totalUnknownCount, totalTCCount
        ) - percentageCalculator(
            totalPassCount, totalTCCount
        )
    if len(suggesstionsDict) < 5:
        if (len(topTCFailureDict)) > 1:
            for tcName, status in topTCFailureDict.items():
                suggesstionsDict[
                    "# Fix the top failing test: "
                    + tcName
                    + " as the failures count is: "
                    + str(int((str(status).split(",")[0]).replace("[", "").strip()))
                ] = 1
                break
    if len(suggesstionsDict) < 5:
        if (len(topDeviceFailureDict)) > 1:
            for device, status in topDeviceFailureDict.items():
                if "_" in str(status):
                    suggesstionsDict[
                        "# Fix the issues with top failing desktop: "
                        + (str(status).split(",")[0])
                        .replace("[", "")
                        .replace("'", "")
                        .strip()
                        + " "
                        + (str(status).split(",")[1]).replace("'", "").strip()
                        + " as the failures count is: "
                        + str(int((str(status).split(",")[3]).strip()))
                    ] = 1
                else:
                    suggesstionsDict[
                        "# Fix the top failing device: "
                        + device
                        + " as the failures count is: "
                        + str(int((str(status).split(",")[3]).strip()))
                    ] = 1
                break
    if len(suggesstionsDict) < 5:
        if int(percentageCalculator(totalFailCount, totalTCCount)) > 15:
            if totalTCCount > 0:
                suggesstionsDict[
                    "# Fix the failures. The total failures % is too high (%) : "
                    + str(percentageCalculator(totalFailCount, totalTCCount))
                    + "%"
                ] = totalFailCount
    if len(suggesstionsDict) < 5:
        if float(percentageCalculator(totalPassCount, totalTCCount)) < 80 and (
            totalTCCount > 0
        ):
            suggesstionsDict[
                "# Fix the failures. The total pass %  is too less (%) : "
                + str(int(percentageCalculator(totalPassCount, totalTCCount)))
                + "%"
            ] = (
                100
                - (
                    percentageCalculator(
                        totalPassCount + totalUnknownCount, totalTCCount
                    )
                    - percentageCalculator(totalPassCount, totalTCCount)
                )
            ) - int(
                percentageCalculator(totalPassCount, totalTCCount)
            )
    if len(suggesstionsDict) < 5:
        if totalTCCount == 0:
            suggesstionsDict[
                "# There are no executions for today. Try Continuous Integration with any tools like Jenkins and schedule your jobs today. Please reach out to Professional Services team of Perfecto for any assistance :) !"
            ] = 100
        elif int(percentageCalculator(totalPassCount, totalTCCount)) > 80:
            print(str(totalTCCount))
            print(str(int(percentageCalculator(totalPassCount, totalTCCount))))
            suggesstionsDict["# Great automation progress. Keep it up!"] = 0

        int(percentageCalculator(totalFailCount, totalTCCount)) > 15
    print("**************#Top 5 failure reasons ")
    topSuggesstionsDict = Counter(suggesstionsDict)
    counter = 0
    for sugg, commonErrorCount in topSuggesstionsDict.most_common(5):
        impact = 1
        if sugg.startswith("# "):
            sugg = sugg.replace("# ", "")
            impact = commonErrorCount
        else:
            impact = percentageCalculator(
                totalPassCount + commonErrorCount, totalTCCount
            ) - percentageCalculator(totalPassCount, totalTCCount)
        jsonObj.recommendations[counter].impact = int(impact)
        if int(impact) < 1:
            jsonObj.recommendations[counter].recommendation = (
                sugg.replace('"', "*|*").replace("'", "*|*").strip()
                + ". Impact: "
                + str(("%.2f" % round(impact, 2)))
                + "%"
            )
        else:
            jsonObj.recommendations[counter].recommendation = (
                sugg.replace('"', "*|*").replace("'", "*|*").strip()
            )
        print(str(counter + 1) + "." + str(sugg))
        printProgressBar(
            counter + 1,
            5,
            prefix="Top suggesstions in Progress:",
            suffix="Complete",
            length=5,
        )
        counter += 1
    counter = 0
    print("**************#Top 5 device which failed")
    for device, status in topDeviceFailureDict.items():
        print(str(counter + 1) + "." + device, status)
        jsonObj.topProblematicDevices[counter].id = device.strip()
        jsonObj.topProblematicDevices[counter].os = (
            (str(status).split(",")[0]).replace("[", "").replace("'", "").strip()
        )
        jsonObj.topProblematicDevices[counter].model = (
            (str(status).split(",")[1]).replace("'", "").strip()
        )
        jsonObj.topProblematicDevices[counter].passed = int(
            (str(status).split(",")[2]).strip()
        )
        jsonObj.topProblematicDevices[counter].failed = int(
            (str(status).split(",")[3]).strip()
        )
        jsonObj.topProblematicDevices[counter].errors = int(
            (str(status).split(",")[4]).replace("]", "").strip()
        )
        printProgressBar(
            counter + 1,
            5,
            prefix="Top device suggesstions in Progress:",
            suffix="Complete",
            length=5,
        )
        counter += 1
    df = pandas.DataFrame(jsonObj.topProblematicDevices)
    df["model"].replace("", np.nan, inplace=True)
    df.dropna(subset=["model"], inplace=True)
    counter = 0
    print("**************#Top 5 failure tests along with pass count")
    for tcName, status in topTCFailureDict.items():
        print(str(counter + 1) + "." + tcName, status)
        jsonObj.topFailingTests[counter].test = tcName.strip()
        jsonObj.topFailingTests[counter].failures = int(
            (str(status).split(",")[0]).replace("[", "").strip()
        )
        jsonObj.topFailingTests[counter].passes = int(
            (str(status).split(",")[1]).replace("]", "").strip()
        )
        printProgressBar(
            counter + 1,
            5,
            prefix="Top TC failures in Progress:",
            suffix="Complete",
            length=5,
        )
        counter += 1
    df2 = pandas.DataFrame(jsonObj.topFailingTests)
    df2["test"].replace("", np.nan, inplace=True)
    df2.dropna(subset=["test"], inplace=True)
    with open("temp.html", "a") as _file:
        _file.write(df.head().to_html() + "\n\n" + df2.head().to_html())
    jsonObj = (
        str(jsonObj).replace("'", '"').replace('"null"', "null").replace("*|*", "'")
    )

    print("############################ Generated JSON:")
    print("jsonObj" + jsonObj)
    print("############################")


"""
   shows the progress bar
"""


def printProgressBar(
    iteration, total, prefix="", suffix="", decimals=1, length=10, fill="#"
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    # percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    # filledLength = int(length * iteration // total)
    # bar = fill * filledLength + '-' * (length - filledLength)
    # print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete


#    if iteration == total:
#        print()

"""
   returns a boolean if the provided string is a date or nots
"""


def is_date(string):
    try:
        parse(string)
        return True
    except ValueError:
        return False


def main():
    start = datetime.now().replace(microsecond=0)
    # #Auto- Retry
    prepareReport()
    # if not prepareReport():
    #     print("############################ Retry in progress as unable to generate report!############################")
    #     if not prepareReport():
    #         print("############################ Not retrying further. Unable to generate Report############################")
    #         exit
    #     else:
    #         print("############################ Success! ############################")
    # else:
    print("############################ Success! ############################")
    end = datetime.now().replace(microsecond=0)
    print("Total Time taken:" + str(end - start))


if __name__ == "__main__":
    global finalDate
    print("Number of arguments:", len(sys.argv))
    print("Argument List:", str(sys.argv))
    try:
        CQL_NAME = str(sys.argv[1])
        OFFLINE_TOKEN = str(sys.argv[2])
    except Exception:
        raise Exception(
            "Pass the mandatory parameters like cloud name and offline token"
        )
    orchestrationIssues = ["already in use"]
    labIssues = ["HANDSET_ERROR"]
    REPORTING_SERVER_URL = "https://" + CQL_NAME + ".reporting.perfectomobile.com"
    api_url = REPORTING_SERVER_URL + "/export/api/v1/test-executions"
    resources = []
    topTCFailureDict = {}
    topDeviceFailureDict = {}

    # job
    jobName = ""
    try:
        jobName = str(sys.argv[5])
        jobNumber = str(sys.argv[6])
    except Exception:
        jobName = ""
    # End date
    try:
        if is_date(sys.argv[4]):
            finalDate = sys.argv[4]
            endDate = str(
                datetime.strptime(
                    str(
                        (
                            datetime.strptime(
                                str(
                                    datetime.strptime(sys.argv[4], "%Y-%m-%d").strftime(
                                        "%d/%m/%Y"
                                    )
                                ),
                                "%d/%m/%Y",
                            ).date()
                            - timedelta(days=0)
                        )
                    ),
                    "%Y-%m-%d",
                ).strftime("%d/%m/%Y")
            )
        elif "d" in sys.argv[4]:
            dateRange = int(sys.argv[4].split("d")[0])
            for value in range(int(dateRange)):
                finalDate = str(datetime.now().date() + timedelta(-value))
                endDate = str(
                    datetime.strptime(
                        str(
                            (
                                datetime.strptime(
                                    str(
                                        datetime.strptime(
                                            finalDate, "%Y-%m-%d"
                                        ).strftime("%d/%m/%Y")
                                    ),
                                    "%d/%m/%Y",
                                ).date()
                                - timedelta(days=0)
                            )
                        ),
                        "%Y-%m-%d",
                    ).strftime("%d/%m/%Y")
                )
                startDate = endDate
                main()
            finalDate = str(datetime.now().date())
            endDate = str(
                datetime.strptime(
                    str(
                        (
                            datetime.strptime(
                                str(
                                    datetime.strptime(finalDate, "%Y-%m-%d").strftime(
                                        "%d/%m/%Y"
                                    )
                                ),
                                "%d/%m/%Y",
                            ).date()
                            - timedelta(days=0)
                        )
                    ),
                    "%Y-%m-%d",
                ).strftime("%d/%m/%Y")
            )
        else:
            finalDate = str(datetime.today().strftime("%Y-%m-%d"))
            endDate = str(
                datetime.strptime(
                    str(
                        (
                            datetime.strptime(
                                str(
                                    datetime.strptime(finalDate, "%Y-%m-%d").strftime(
                                        "%d/%m/%Y"
                                    )
                                ),
                                "%d/%m/%Y",
                            ).date()
                            - timedelta(days=0)
                        )
                    ),
                    "%Y-%m-%d",
                ).strftime("%d/%m/%Y")
            )
    except Exception:
        finalDate = str(datetime.today().strftime("%Y-%m-%d"))
        endDate = str(
            datetime.strptime(
                str(
                    (
                        datetime.strptime(
                            str(
                                datetime.strptime(finalDate, "%Y-%m-%d").strftime(
                                    "%d/%m/%Y"
                                )
                            ),
                            "%d/%m/%Y",
                        ).date()
                        - timedelta(days=0)
                    )
                ),
                "%Y-%m-%d",
            ).strftime("%d/%m/%Y")
        )
    # Start date
    try:
        startDate = str(
            datetime.strptime(
                str(
                    (
                        datetime.strptime(
                            str(
                                datetime.strptime(sys.argv[3], "%Y-%m-%d").strftime(
                                    "%d/%m/%Y"
                                )
                            ),
                            "%d/%m/%Y",
                        ).date()
                        - timedelta(days=0)
                    )
                ),
                "%Y-%m-%d",
            ).strftime("%d/%m/%Y")
        )
    except Exception:
        startDate = endDate

    main()
