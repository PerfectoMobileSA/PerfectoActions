import html
import base64
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
from perfecto.perfectoactions import fig_to_base64

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
reportType = "1email"
duration = "weekly"
filelist = glob.glob(os.path.join("*.html" ))
for f in filelist:
    os.remove(f)
df = pandas.DataFrame()
df = df.append(pandas.read_excel("./sc.xlsx"))
# df = df.append(pandas.read_csv("./final.csv", low_memory=False))
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
monthlyStats = monthlyStats.to_html( classes="mystyle", table_id="report", index=True, render_links=True, escape=False ).replace('<tr>', '<tr align="center">')
failurereasons = pandas.crosstab(df['failureReasonName'],df['status'])
# print (failurereasons)
failurereasons = failurereasons.to_html( classes="mystyle", table_id="report", index=True, render_links=True, escape=False )
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
topfailedtable = topfailedTCNames.to_html( classes="mystyle", table_id="report", index=False, render_links=True, escape=False )

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
        if "An error occurred. Stack Trace:" in error:
            error = error.split("An error occurred. Stack Trace:")[1]
    if re.search("error: \-\[|Fatal error:", error):
        error = str(re.compile("error: \-\[|Fatal error:").split(error)[1])
    if error.strip() in cleanedFailureList:
        cleanedFailureList[error.strip()] += 1
    else:
        cleanedFailureList[error.strip()] = commonErrorCount
    scriptingIssuesCount = (totalFailCount + blockedCount) - (orchestrationIssuesCount + labIssuesCount)

 # Top 5 failure reasons
topFailureDict = {}

failureDict = Counter(cleanedFailureList)
for commonError, commonErrorCount in failureDict.most_common(5):
    topFailureDict[commonError] = int(commonErrorCount)

# reach top errors and clean them
i = 0
for commonError, commonErrorCount in topFailureDict.items():
    if "ERROR: No device was found" in commonError:
        error = (
            "Raise a support case as the error: *|*"
            + commonError.strip()
            + "*|* occurs in *|*"
            + str(commonErrorCount)
            + "*|* occurrences"
        )
    elif "Cannot open device" in commonError:
        error = (
            "Reserve the device/ use perfecto lab auto selection feature to avoid the error:  *|*"
            + commonError.strip()
            + "*|* occurs in *|*"
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
            "status": [
                {
                "#Total": "Count ->",
                "#Execution": totalTCCount,
                "#Pass" : totalPassCount,
                "#Failed" : totalFailCount,
                "#Blocked" : blockedCount,
                "#Unknowns": totalUnknownCount,
                "Overall Pass %": str(int(percentageCalculator(totalPassCount, totalTCCount))) + "%",
                },
            ],
            "issues": [
              {
                "#Issues": "Count ->",
                "#Scripting": scriptingIssuesCount,
                "#Lab": labIssuesCount,
                "#Orchestration": orchestrationIssuesCount,
                },
            ],
            "recommendation": [
                {
                   "Recommendations": "-",
                   "Rank": 1,
                    "impact": "0",
                },
                {
                   "Recommendations": "-",
                     "Rank": 2,
                    "impact": "0",
                },
                {
                    "Recommendations": "-",
                    "Rank": 3,
                    "impact": "0",
                },
                {
                    "Recommendations": "-",
                    "Rank": 4,
                     "impact": "0",
                },
                {
                    "Recommendations": "-",
                    "Rank": 5,
                    "impact": "0",
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
        suggesstionsDict["# Great automation progress. Keep it up!"] = 0

    int(percentageCalculator(totalFailCount, totalTCCount)) > 15
topSuggesstionsDict = Counter(suggesstionsDict)
counter = 0
totalImpact = 0
for sugg, commonErrorCount in topSuggesstionsDict.most_common(5):
    impact = 1
    if sugg.startswith("# "):
        sugg = sugg.replace("# ", "")
        impact = commonErrorCount
    else:
        impact = percentageCalculator(
            totalPassCount + commonErrorCount, totalTCCount
        ) - percentageCalculator(totalPassCount, totalTCCount)
    jsonObj.recommendation[counter].impact = str(("%.2f" % round(impact, 2))) + "%"
    jsonObj.recommendation[counter].Recommendations = (
        html.escape(sugg.replace("*|*", "'").replace("{","{{").replace("}","}}").strip())
    )
    totalImpact += round(impact, 2)
    counter += 1
execution_status = pandas.DataFrame.from_dict(jsonObj.status)
execution_status = execution_status.to_html( classes="mystyle", table_id="report", index=False, render_links=True, escape=False )
issues = pandas.DataFrame.from_dict(jsonObj.issues)
issues = issues.to_html( classes="mystyle", table_id="report", index=False, render_links=True, escape=False )
recommendations = pandas.DataFrame.from_dict(jsonObj.recommendation)
recommendations.columns = ['Recommendations', 'Rank', 'Impact to Pass % [Total - ' + str(totalImpact) + '%]']
recommendations = recommendations.to_html( classes="mystyle", table_id="report", index=False, render_links=True, escape=False )
print("Total impact% :" + str(totalImpact))


import plotly.express as px
import plotly
#ggplot2 #plotly_dark #simple_white
#weekly
report_filename = "temp.html"
df['startDate'] = pandas.to_datetime(pandas.to_datetime(df['startTime']).dt.strftime("%d/%m/%Y"))
df['week'] = df['startDate'] - df['startDate'].dt.weekday.astype('timedelta64[D]')
monthly_summary = []
for job in df['job/name'].dropna().unique(): 
    fig = px.histogram(df.loc[df['job/name'] == job], x="week", color="Test Status",
                            hover_data=df.columns, color_discrete_map= {"PASSED":"limegreen","FAILED":"crimson","UNKNOWN":"#9da7f2","BLOCKED":"#e79a00"}, template="seaborn", opacity=0.5)
    fig.update_layout(
        title={
          'text': job,
          'y':0.94,
          'x':0.5,
          'xanchor': 'center',
          'yanchor': 'top'},
        xaxis_title="Week",
        yaxis_title="Status",
        font=dict(
            family="Trebuchet MS, Helvetica, sans-serif",
            size=12,
            color = 'black'
        ),
        autosize=True,
       
        hovermode="x unified",
        yaxis={'tickformat': ',d'},
        xaxis = dict(tickmode = 'array'),
        xaxis_tickformat = '%d<br>%B<br>%Y',
    ) 
    if reportType == "email":
          fig.update_layout(
            width=700,
            height=500,
          )
    fig.update_yaxes(automargin=True)
    if reportType == "email":
        encoded = base64.b64encode(plotly.io.to_image(fig))
        """ + monthly_summary +  """ 
        monthly_summary.append('<img src="data:image/png;base64, {}"'.format(encoded.decode("ascii")) + "alt='monthly summary' id='reportDiv' onClick='zoom(this)'></img>")
    else:   
        # fig.show()
        with open(report_filename, 'a') as f:
           f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
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
                box-shadow: 0 0 80px rgba(2, 112, 0, 0.4);
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

            p {{
              text-align:center;
              color:white;
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
                width: auto;
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
              font-size: 14px;
              font-weight: normal;
              color: #fffffa;
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
      .glow {{
        font-size: 15px;
        color: white;
        text-align: center;
        -webkit-animation: glow 1s ease-in-out infinite alternate;
        -moz-animation: glow 1s ease-in-out infinite alternate;
        animation: glow 1s ease-in-out infinite alternate;
      }}

      @-webkit-keyframes glow {{
        from {{
          text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #e60073, 0 0 40px #e60073, 0 0 50px #e60073, 0 0 60px #e60073, 0 0 70px #e60073;
        }}
        
        to {{
          text-shadow: 0 0 20px #fff, 0 0 30px #ff4da6, 0 0 40px #ff4da6, 0 0 50px #ff4da6, 0 0 60px #ff4da6, 0 0 70px #ff4da6, 0 0 80px #ff4da6;
        }}
      }}
      .reportHeadingDiv {{
        background-color: #44118b; 
        text-align: center;
      }}
      .reportDiv {{
        overflow-x: scroll;
        align:center;
        text-align: center;
      }}
      #report{{
        box-shadow: 0 0 80px rgba(200, 112, 1120, 0.4);
        overflow-x: scroll;
        min-width:100%;
      }}
            </style>
          <body bgcolor="#FFFFED">
        <body> <div class="reportDiv">""" + "".join(monthly_summary) + """</div></p><div class="reportDiv"> """ + execution_summary  + """ alt='execution summary' id='reportDiv' onClick='zoom(this)'></img></br></div></p>  <div style="overflow-x:auto;">""" + \
          """ <p> <div class="reportHeadingDiv" ><h1 class="glow">Summary</h1></div><p><div class="reportDiv">""" + execution_status + \
          """ </div><p> <div class="reportHeadingDiv" ><h1 class="glow">OS Summary</h1></div> <p><div class="reportDiv">""" + monthlyStats + \
          """ </div><p><div class="reportHeadingDiv" ><h1 class="glow">Issues</h1> </div> <p><div class="reportDiv">""" +issues + \
          """ </div><p> <div class="reportHeadingDiv" ><h1 class="glow">Custom Failure Reasons</h1> </div> <p><div class="reportDiv">""" + failurereasons + \
          """ </div><p> <div class="reportHeadingDiv" ><h1 class="glow">Top Failed Tests </h1> </div> <p><div class="reportDiv">""" +topfailedtable + \
          """ </div><p> <div class="reportHeadingDiv" ><h1 class="glow">Top Recommendations </h1> </div> <p><div class="reportDiv">""" + recommendations + """ </div></div> </body>"""
)


with open(report_filename, "a") as f:
    f.write(html_string.format(table=df.to_html( classes="mystyle", table_id="report", index=False , render_links=True, escape=False)))
