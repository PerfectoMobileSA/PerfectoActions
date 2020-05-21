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

from perfecto.perfectoactions import create_summary
# data = [dict(name='Google', url='http://www.google.com'),
#         dict(name='Stackoverflow', url='http://stackoverflow.com')]


# df = pandas.DataFrame(list(range(5)), columns=['a'])

# df['a'] = df['a'].apply(lambda x: '<a href="http://example.com/{0}">link</a>'.format(x))

# print(df)
# HTML(df.to_html("temp.html",escape=False))

df = pandas.DataFrame()
df = df.append(pandas.read_csv("./final.csv"))
execution_summary = create_summary(df, "Summary Report", "status", "device_summary")
failed = df[(df['status'] == "FAILED")]
passed = df[(df['status'] == "PASSED")]
failed_blocked = df[(df['status'] == "FAILED") | (df['status'] == "BLOCKED")]
totalUnknownCount = df[(df['status'] == "UNKNOWN")].shape[0]
totalTCCount = df.shape[0]
#monthly stats
monthlyStats = df.pivot_table(index = ["month", "platforms/0/deviceType", "platforms/0/os"], 
              columns = "status" , 
              values = "name", 
              aggfunc = "count", margins=True, fill_value=0)\
        .fillna('')
for column in monthlyStats.columns:
  monthlyStats[column] = monthlyStats[column].astype(str).replace('\.0', '', regex=True)
monthlyStats = monthlyStats.to_html( classes="mystyle", table_id="monthlysummary", index=True, render_links=True, escape=False ).replace('<tr>', '<tr align="center">')
failurereasons = pandas.crosstab(df['failureReasonName'],df['status'])
# print (failurereasons)
failurereasons = failurereasons.to_html( classes="mystyle", table_id="failuresummary", index=True, render_links=True, escape=False )
#top failed TCs
topfailedTCNames = failed.groupby(['name']).size().reset_index(name='#Failed').sort_values('#Failed', ascending=False).head(5)
reportURLs = []
for ind in topfailedTCNames.index:
  reportURLs.append(failed.loc[failed['name'] == topfailedTCNames['name'][ind], 'reportURL'].iloc[0])
topfailedTCNames['Result'] = reportURLs
topfailedTCNames['Result'] = topfailedTCNames['Result'].apply(lambda x: '{0}'.format(x))
for ind in topfailedTCNames.index:
  topfailedTCNames.loc[topfailedTCNames['name'].index == ind, 'name']  = '<a target="_blank" href="' + topfailedTCNames['Result'][ind] + '">' + topfailedTCNames['name'][ind] + '</a>'
topfailedTCNames = topfailedTCNames.drop('Result', 1)
topfailedTCNames.columns = ['Top 5 Failed Tests', '#Failed']
# print(str(topfailedTCNames))
topfailedtable = topfailedTCNames.to_html( classes="mystyle", table_id="summary", index=False, render_links=True, escape=False )

#recommendations
orchestrationIssues = ["already in use"]
labIssues = ["HANDSET_ERROR", "ERROR: No device was found"]
regEx_Filter = "Build info:|For documentation on this error|at org.xframium.page|Scenario Steps:| at WebDriverError|\(Session info:|XCTestOutputBarrier\d+|\s\tat [A-Za-z]+.[A-Za-z]+.|View Hierarchy:|Got: |Stack Trace:|Report Link|at dalvik.system|Output:\nUsage|t.*Requesting snapshot of accessibility"
labIssuesCount = 0
scriptingIssuesCount = 0
orchestrationIssuesCount = 0
cleanedFailureList = {}
suggesstionsDict = {}
totalFailCount = failed.shape[0]
totalPassCount = passed.shape[0]
blockedCount = failed_blocked.shape[0]
# failures count
failuresmessage = failed_blocked.groupby(['message']).size().reset_index(name='#Failed').sort_values('#Failed', ascending=False)
print(failuresmessage)
for commonError, commonErrorCount in failuresmessage.itertuples(index=False):
    for labIssue in labIssues:
        if re.search(labIssue, commonError):
            labIssuesCount += commonErrorCount
            break
    for orchestrationIssue in orchestrationIssues:
        if re.search(orchestrationIssue, commonError):
            orchestrationIssuesCount += commonErrorCount
            break
    error = commonError
    regEx_Filter = "Build info:|For documentation on this error|at org.xframium.page|Scenario Steps:| at WebDriverError|\(Session info:|XCTestOutputBarrier\d+|\s\tat [A-Za-z]+.[A-Za-z]+.|View Hierarchy:|Got: |Stack Trace:|Report Link|at dalvik.system|Output:\nUsage|t.*Requesting snapshot of accessibility"
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
    scriptingIssuesCount = (totalFailCount + blockedCount) - (orchestrationIssuesCount + labIssuesCount)
print(orchestrationIssuesCount)
print(labIssuesCount)
print(scriptingIssuesCount)
# print(cleanedFailureList)

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
eDict = edict(
        {
           
            "Pass%": int(percentageCalculator(totalPassCount, totalTCCount)),
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
    if (topfailedTCNames.shape[0]) > 1:
        for tcName, status in topfailedTCNames.itertuples(index=False):
            suggesstionsDict[
                "# Fix the top failing test: "
                + tcName
                + " as the failures count is: "
                + str(int((str(status).split(",")[0]).replace("[", "").strip()))
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
        print(str(int(percentageCalculator(totalPassCount, totalTCCount))))
        suggesstionsDict["# Great automation progress. Keep it up!"] = 0

    int(percentageCalculator(totalFailCount, totalTCCount)) > 15
print("**************#Top 5 failure reasons ")
topSuggesstionsDict = Counter(suggesstionsDict)
print(topSuggesstionsDict)
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
print(jsonObj)
html_string = (
        """
    <html lang="en">
       <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    		     <head><title> Cloud Status</title>
          <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
            <script>
              $(document).ready(function(){{
                document.getElementById("tabbed-device").click();
            }});
            $(document).ready(function(){{
                // Add smooth scrolling to all links
                $("a").on('click', function(event) {{

                    // Make sure this.hash has a value before overriding default behavior
                    if (this.hash !== "") {{
                    // Prevent default anchor click behavior
                    event.preventDefault();

                    // Store hash
                    var hash = this.hash;

                    // Using jQuery's animate() method to add smooth page scroll
                    // The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
                    $('html, body').animate({{
                        scrollTop: $(hash).offset().top
                    }}, 800, function(){{
                
                        // Add hash (#) to URL when done scrolling (default click behavior)
                        window.location.hash = hash;
                    }});
                    }} // End if
                }});
            }});
            $(document).ready(function(){{
              $("#myInput").on("keyup", function() {{
                var value = $(this).val().toLowerCase();
                $("#devicetable tbody tr").filter(function() {{
                  $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
                }});
              }});
            }});
                      $(document).ready(function(){{
              $("#myInput2").on("keyup", function() {{
                var value = $(this).val().toLowerCase();
                $("#usertable tbody tr").filter(function() {{
                  $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
                }});
              }});
            }});
            $(document).ready(function(){{
              $("#myInput3").on("keyup", function() {{
                var value = $(this).val().toLowerCase();
                $("#repotable tbody tr").filter(function() {{
                  $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
                }});
              }});
            }});
            </script>
    		<script type="text/javascript">
    	           $(document).ready(function(){{
                   $("#slideshow > div:gt(0)").show();
    				$("tbody tr:contains('Disconnected')").css('background-color','#fcc');
    				$("tbody tr:contains('ERROR')").css('background-color','#fcc');
    				$("tbody tr:contains('Un-available')").css('background-color','#fcc');
    				$("tbody tr:contains('Busy')").css('background-color','#fcc');
                    var table = document.getElementById("devicetable");
    				var rowCount = table.rows.length;
    				for (var i = 0; i < rowCount; i++) {{
    					if ( i >=1){{
                        available_column_number = 0;
                        device_id_column_number = 1;
    						if (table.rows[i].cells[available_column_number].innerHTML == "Available") {{
                                for(j = 0; j < table.rows[0].cells.length; j++) {{
    								table.rows[i].cells[j].style.backgroundColor = '#e6fff0';
                                        if(j=table.rows[0].cells.length){{
                                                if (table.rows[i].cells[(table.rows[0].cells.length - 1)].innerHTML.indexOf("failed") > -1) {{
                                                        table.rows[i].cells[j].style.color = '#660001';
                                                        table.rows[i].cells[j].style.backgroundColor = '#FFC2B5';
                                                }}
    							}}
                                 }}
    							var txt = table.rows[i].cells[device_id_column_number].innerHTML;
    							var url = 'http';
    							var row = $('<tr></tr>')
    							var link = document.createElement("a");
    							link.href = url;
    							link.innerHTML = txt;
    							link.target = "_blank";
    							table.rows[i].cells[device_id_column_number].innerHTML = "";
    							table.rows[i].cells[device_id_column_number].appendChild(link);
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
                function zoom(element) {{
				         var data = element.getAttribute("src");
						 let w = window.open('about:blank');
						 let image = new Image();
						 image.src = data;
						 setTimeout(function(){{
						   w.document.write(image.outerHTML);
						 }}, 0);
				     }}
                function autoselect(element) {{
                     var data = element.getAttribute("id");
                     document.getElementById(data + "-1").checked = true;
                }}     
    		</script>

    		<meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
             <style>

            html {{
              height:100%;
            }}
            
            .tabbed {{
               display:  flex;
               text-align: left;
               flex-wrap: wrap;
               box-shadow: 0 0 20px rgba(186, 99, 228, 0.4);
               font-size: 12px;
               font-family: "Trebuchet MS", Helvetica, sans-serif;
             }}
             .tabbed > input {{
               display: none;
             }}
             .tabbed > input:checked + label {{
               font-size: 14px;
               text-align: center;
               color: white;
               background-image: linear-gradient(to left, #bfee90, #333333, black,  #333333, #bfee90);
             }}
             .tabbed > input:checked + label + div {{
               color:darkslateblue;
               display: block;
             }}
             .tabbed > label {{
               background-image: linear-gradient(to left, #fffeea,  #333333, #333333 ,#333333 ,#333333 , #333333, #fffeea);
               color: white;
               text-align: center;
               display: block;
               order: 1;
               flex-grow: 1;
               padding: .3%;
             }}
             .tabbed > div {{
               order: 2;
               flex-basis: 100%;
               display: none;
               padding: 10px;
             }}

             /* For presentation only */
             .container {{
               width: 100%;
               margin: 0 auto;
               background-color: black;
               box-shadow: 0 0 20px rgba(400, 99, 228, 0.4);
             }}

             .tabbed {{
               border: 1px solid;
             }}

             hr {{
               background-color: white;
               height: 5px;
               border: 0;
               margin: 10px 0 0;
             }}
             
             hr + * {{
               margin-top: 10px;
             }}
             
             hr + hr {{
               margin: 0 0;
             }}

            .mystyle {{
                font-size: 12pt;
                font-family: "Trebuchet MS", Helvetica, sans-serif;
                border-collapse: collapse;
                border: 2px solid black;
                margin:auto;
                width: 95%;
                box-shadow: 0 0 80px rgba(2, 112, 0, 0.4);
                table-layout: fixed;
                word-wrap: break-word; 
                background-color: white;
            }}

            .mystyle body {{
              font-family: "Trebuchet MS", Helvetica, sans-serif;
                table-layout: auto;
                position:relative;
            }}

            #slide{{
              width:100%;
              height:auto;
            }}

            #myInput, #myInput2, #myInput3 {{
              background-image: url('http://www.free-icons-download.net/images/mobile-search-icon-94430.png');
              background-position: 2px 4px;
              background-repeat: no-repeat;
              background-size: 25px 30px;
              width: 40%;
              height:auto;
              font-weight: bold;
              font-size: 12px;
              padding: 11px 20px 12px 40px;
              box-shadow: 0 0 80px rgba(2, 112, 0, 0.4);
            }}

            body {{
              background-color: black;
              height: 100%;
              background-repeat:  repeat-y;
              background-position: right;
              background-size:  contain;
              background-attachment: initial;
              opacity:.93;
            }}

            h4 {{
              font-family:monospace;
            }}

            @keyframes slide {{
              0% {{
                transform:translateX(-25%);
              }}
              100% {{
                transform:translateX(25%);
              }}
            }}

            .mystyle table {{
                table-layout: auto;
                width: 100%;
                height: 100%;
                position:relative;
                border-collapse: collapse;
            }}

            tr:hover {{background-color:grey;}}

            .mystyle td {{
                font-size: 12px;
                position:relative;
                padding: 5px;
                width:10%;
                color: black;
              border-left: 1px solid #333;
              border-right: 1px solid #333;
              background: #fffffa;
              text-align: center;
            }}

            table.mystyle td:first-child {{ text-align: left; }}   

            table.mystyle thead {{
              background: #333333;
              font-size: 14px;
              position:relative;
              border-bottom: 1px solid #DBDB40;
              border-left: 1px solid #D8DB40;
              border-right: 1px solid #D8DB40;
              border-top: 1px solid black;
            }}

            table.mystyle thead th {{
              line-height: 200%;
              font-size: 13px;
              color: #fff1bf;
              text-align: center;
              transition:transform 0.25s ease;
            }}

            table.mystyle thead th:hover {{
                -webkit-transform:scale(1.01);
                transform:scale(1.01);
            }}

            table.mystyle thead th:first-child {{
              border-left: none;
            }}

            .topnav {{
              overflow: hidden;
              background-color: black;
              opacity: 0.9;
            }}

            .topnav a {{
              float: right;
              display: block;
              color: #333333;
              text-align: center;
              padding: 12px 15px;
              text-decoration: none;
              font-size: 12px;
              position: relative;
              border: 1px solid #6c3;
              font-family: "Trebuchet MS", Helvetica, sans-serif;
            }}

            #summary{{
             box-shadow: 0 0 80px rgba(200, 112, 1120, 0.4);
             position: relative;
             width:50%;
             cursor: pointer;
             padding: .1%;
             border-style: outset;
             border-radius: 1px;
             border-width: 1px;
            }}
            
            #logo{{
             box-shadow: 0 0 80px rgba(200, 112, 1120, 0.4);
             position: relative;
             cursor: pointer;
             border-style: outset;
             border-radius: 1px;
             border-width: 1px;
            }}

            .topnav a.active {{
              background-color: #333333;
              color: white;
              font-weight: lighter;
            }}

            .topnav .icon {{
              display: none;
            }}

            @media screen and (max-width: 600px) {{
              .topnav a:not(:first-child) {{display: none;}}
              .topnav a.icon {{
                color: #DBDB40;
                float: right;
                display: block;
              }}
            }}

            @media screen and (max-width: 600px) {{
              .topnav.responsive {{position: relative;}}
              .topnav.responsive .icon {{
                position: absolute;
                right: 0;
                top: 0;
              }}
              .topnav.responsive a {{
                float: none;
                display: block;
                text-align: left;
              }}
            }}

            * {{
              box-sizing: border-box;
            }}

            img {{
              vertical-align: middle;
            }}

            .containers {{
              position: relative;
            }}

            .mySlides {{
              display:none;
              width:90%;
            }}

            #slideshow {{
              cursor: pointer;
              margin:.01% auto;
              position: relative;
              width: 70%;
              height: 55%;
            }}

            #ps{{
              height: 10%;
              margin-top: 0%;
              margin-bottom: 90%;
              background-position: center;
              background-repeat: no-repeat;
              background-blend-mode: saturation;
            }}

            #slideshow > div {{
              position: relative;
              width: 90%;
            }}

       		#download {{
			  background-color: #333333;
			  border: none;
			  color: white;
              font-size: 12px;
              padding: 13px 20px 15px 20px;
			  cursor: pointer;
			}}

			#download:hover {{
			  background-color: RoyalBlue;
			}}
            </style>
          <body bgcolor="#FFFFED">
        <body> <div align="center">""" + execution_summary  + """ alt='user_summary' id='summary' onClick='zoom(this)'></img></br></div></p>  <div style="overflow-x:auto;">""" + monthlyStats + failurereasons +  topfailedtable  + """ </div> </body>"""
)
# with open(os.path.join(TEMP_DIR, "output", "temp.html"), "w") as f:
with open("temp.html", "w") as f:
    f.write(html_string.format(table=df.to_html( classes="mystyle", table_id="summary", index=False , render_links=True, escape=False)))

  # f.write(html_string.format(table=df.to_html( classes="mystyle", table_id="summary", index=False , render_links=True, escape=False)))


