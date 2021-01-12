from datetime import datetime, timedelta

import numpy as np
import pandas as pandas
import tzlocal
from datetimerange import DateTimeRange

import perfecto.perfectoactions as actions

# https://stackoverflow.com/questions/60226735/how-to-count-overlapping-datetime-intervals-in-pandas


user = 'user'
deviceId = 'deviceId'
reservationid = 'reservationid'
startTime = 'startTime'
endTime = 'endTime'
status = 'status'


# ori_df = pandas.DataFrame(columns=[user, deviceId, reservationid, status, startTime, endTime], index=range(7), \
#     data=[['gthomas',9182381092,'1','SCHEDULED','2020-12-03 07:00:00','2020-12-03 10:00:00'],
#             ['gthomas',9182381092,'2','SCHEDULED','2020-12-03 09:00:00','2020-12-03 13:00:00'],
#             ['gthomas',9182381092,'3', 'EXPIRED','2020-12-03 08:00:00','2020-12-03 10:59:00'],
#             ['gthomas',9182381092,'4','SCHEDULED','2020-12-03 12:00:00','2020-12-03 16:00:00'],
#             ['gthomas',9182381092,'5','SCHEDULED','2020-12-03 11:00:00','2020-12-03 14:00:00'],
#             ['gthomas',9182381092,'6','STARTED','2020-12-03 12:00:00','2020-12-03 16:00:00'],
#             ['gthomas',9182381092,'7','SCHEDULED','2020-12-03 15:00:00','2020-12-03 18:00:00']
#             ])

# hadas sample
ori_df = pandas.DataFrame(columns=[user, deviceId, reservationid, status, startTime, endTime], index=range(7), \
    data=[['gthomas',9182381092,'1','SCHEDULED','2020-12-03 07:00:00','2020-12-03 10:00:00'],
            ['gthomas',9182381092,'2','SCHEDULED','2020-12-03 09:00:00','2020-12-03 13:00:00'],
            ['gthomas',9182381092,'3', 'SCHEDULED','2020-12-03 08:00:00','2020-12-03 11:00:00'],
            ['gthomas',9182381092,'4','SCHEDULED','2020-12-03 12:00:00','2020-12-03 16:00:00'],
            ['gthomas',9182381092,'5','SCHEDULED','2020-12-03 11:00:00','2020-12-03 14:00:00'],
            ['gthomas',9182381092,'6','SCHEDULED','2020-12-03 12:00:00','2020-12-03 16:00:00'],
            ['gthomas',9182381092,'7','SCHEDULED','2020-12-03 15:00:00','2020-12-03 18:00:00']
            ])

#overlapping
# ori_df = pandas.DataFrame(columns=[user, deviceId, reservationid, status, startTime, endTime], index=range(8), \
#     data=[['gthomas',9182381092,'1','SCHEDULED','2020-12-03 07:00:00','2020-12-03 10:00:00'],
#             ['gthomas',9182381092,'2','SCHEDULED','2020-12-03 07:00:00','2020-12-03 10:00:00'],
#             ['gthomas',9182381092,'3', 'SCHEDULED','2020-12-03 08:00:00','2020-12-03 11:00:00'],
#             ['gthomas',9182381092,'4','SCHEDULED','2020-12-03 08:00:00','2020-12-03 11:00:00'],
#             ['gthomas',9182381092,'5','SCHEDULED','2020-12-03 07:00:00','2020-12-03 10:00:00'],
#             ['gthomas',9182381092,'6','SCHEDULED','2020-12-03 07:00:00','2020-12-03 10:00:00'],
#             ['gthomas',9182381092,'7', 'SCHEDULED','2020-12-03 08:00:00','2020-12-03 11:00:00'],
#             ['gthomas',9182381092,'8','SCHEDULED','2020-12-03 08:00:00','2020-12-03 11:00:00'],
#             ])

#endTime minus 1 second
# ori_df = pandas.DataFrame(columns=[user, deviceId, reservationid, status, startTime, endTime], index=range(3), \
#     data=[['gthomas',9182381092,'1','SCHEDULED','2020-12-03 07:00:00','2020-12-03 10:00:00'],
#             ['gthomas',9182381092,'2','SCHEDULED','2020-12-03 07:00:00','2020-12-03 10:00:00'],
#             ['gthomas',9182381092,'3', 'SCHEDULED','2020-12-03 10:00:00','2020-12-03 11:00:00']
#             ])

# ori_df = pandas.DataFrame(columns=[user, deviceId, reservationid, status, startTime, endTime], index=range(14), \
#     data=[['gthomas',9182381092,'1','SCHEDULED','2020-12-03 07:00:00','2020-12-03 10:00:00'],
#             ['gthomas',9182381092,'2','SCHEDULED','2020-12-03 09:00:00','2020-12-03 13:00:00'],
#             ['gthomas',9182381092,'3', 'SCHEDULED','2020-12-03 08:00:00','2020-12-03 10:59:00'],
#             ['gthomas',9182381092,'4','SCHEDULED','2020-12-03 12:00:00','2020-12-03 16:00:00'],
#             ['gthomas',9182381092,'5','SCHEDULED','2020-12-03 11:00:00','2020-12-03 14:00:00'],
#             ['gthomas',9182381092,'6','STARTED','2020-12-03 12:00:00','2020-12-03 16:00:00'],
#             ['gthomas',9182381092,'7','SCHEDULED','2020-12-03 15:00:00','2020-12-03 18:00:00'],
#             ['sthomas',9182381092,'1','SCHEDULED','2020-12-03 07:00:00','2020-12-03 10:00:00'],
#             ['sthomas',9182381092,'2','SCHEDULED','2020-12-03 09:00:00','2020-12-03 13:00:00'],
#             ['sthomas',9182381092,'3', 'SCHEDULED','2020-12-03 08:00:00','2020-12-03 10:59:00'],
#             ['sthomas',9182381092,'4','SCHEDULED','2020-12-03 12:00:00','2020-12-03 16:00:00'],
#             ['sthomas',9182381092,'5','SCHEDULED','2020-12-03 11:00:00','2020-12-03 14:00:00'],
#             ['sthomas',9182381092,'6','STARTED','2020-12-03 12:00:00','2020-12-03 16:00:00'],
#             ['sthomas',9182381092,'7','SCHEDULED','2020-12-03 15:00:00','2020-12-03 18:00:00']
#             ])

def reserve(ori_df, limit, skip_list, include_list, delete):
    user = 'user'
    deviceId = 'deviceId'
    reservationid = 'reservationid'
    startTime = 'startTime'
    endTime = 'endTime'
    status = 'status'
    cols = [user, deviceId, reservationid, status, startTime, endTime]  
    # ori_df[startTime] = pandas.to_datetime(ori_df[startTime], unit="ms")
    # ori_df[startTime] = (
    #     ori_df[startTime].dt.tz_localize("utc").dt.tz_convert(tzlocal.get_localzone())
    # )
    # ori_df[startTime] = ori_df[startTime].dt.strftime("%d/%m/%Y %H:%M:%S")
    # ori_df[endTime] = pandas.to_datetime(ori_df[endTime], unit="ms")
    # ori_df[endTime] = (
    #     ori_df[endTime].dt.tz_localize("utc").dt.tz_convert(tzlocal.get_localzone())
    # )
    # ori_df[endTime] = ori_df[endTime].dt.strftime("%d/%m/%Y %H:%M:%S")
    print(ori_df)
    pandas.set_option("display.max_columns", None)
    pandas.set_option("display.max_colwidth", 100)
    pandas.set_option("colheader_justify", "center")
    deleted_df = pandas.DataFrame(columns=cols)
    i = 0
    for user_name in ori_df[user].unique():
        if(user_name in include_list.split(",") or include_list == ""):
            pandas.options.mode.chained_assignment = None
            df = ori_df[ori_df[user] == user_name] 
            df = df[df[status].isin(['SCHEDULED', 'STARTED'])] 
            df=df.sort_values([startTime,endTime])
            df[startTime] = pandas.to_datetime(df[startTime])
            df[endTime] = pandas.to_datetime(df[endTime])
            df[endTime] = df[endTime] - timedelta(seconds=1)
            temp_df = df[[startTime,endTime]]
            print("\n full table of user: " + str(user_name))
            print(temp_df)
            
            
            temp_df = temp_df.melt(var_name = 'status',value_name = 'time').sort_values('time')
            # if there are more than expected violations, delete the reservation.
            while(temp_df['time'].shape[0] > 0):
                if(temp_df['time'].shape[0] > 1):
                    temp_df['counter'] = np.where(temp_df['status'].eq(startTime),1,-1).cumsum()
                    # temp_df['counter'] = temp_df['status'].map({startTime:1,endTime:-1}).cumsum()
                    temp_df = temp_df[temp_df['counter'] > int(str(limit))]  
                    # temp_df = temp_df.groupby(['status','time'],as_index=False).agg({'counter': 'sum'})
                temp_df = temp_df[temp_df['status'] == startTime].sort_values(['time'], ascending=[False]).sort_values(['counter'], ascending=[False])
                print((temp_df))
                if(temp_df['time'].shape[0] > 0):
                    new_startTime = temp_df['time'].iloc[0]
                    new_df = df[df[startTime] == new_startTime]
                    new_df = new_df.sort_values([endTime], ascending=[False])
                    print("\n violation for user: " + str(user_name) +  "\n")
                    print(new_df)
                    if(temp_df['counter'].iloc[0] > (int(str(limit)) )):       
                        bool = False              
                        while(new_df.shape[0] > 0) :
                            time_range = DateTimeRange( new_df[startTime].iloc[0],  new_df[endTime].iloc[0])
                            count = 0
                            if(new_df.shape[0] > 0):
                                df = df.reset_index(drop=True)
                                for index, row in df.iterrows():
                                    x = DateTimeRange(df[startTime].iloc[index], df[endTime].iloc[index])
                                    if(time_range.is_intersection(x)):
                                        count+=1
                            else:
                                break;
                            if(count > (int(str(limit)))):
                                reservation_id = str(new_df[reservationid].iloc[0])
                                if(new_df[user].iloc[0] not in skip_list.split(",")):
                                    if(str(delete).lower() == "true"):
                                    # delete each reservation
                                        print("id: " + reservation_id + " will be deleted now.")
                                        # map = deleteReserveAPI(RESOURCE_TYPE_RESERVATIONS, reservation_id, "delete", "true")
                                        print("Delete API output of id: " + reservation_id + "\n " + str(map))
                                        try:
                                            delete_status = map["status"]
                                            if("Success" in delete_status):  
                                                pass
                                            else:
                                                raise Exception("Unable to delete reservation: " + reservation_id + " Response: " + map.items())    
                                        except Exception as e:
                                            raise Exception("Unable to delete reservation: " + reservation_id + " Response: " + map['errorMessage'])  
                                    deleted_df.loc[i] = new_df.iloc[0] 
                                    i=i+1
                                    ori_df.drop(ori_df[ori_df[reservationid] == reservation_id].head(1).index, inplace = True) 
                                df.drop(df[df[reservationid] == reservation_id].head(1).index, inplace = True) 
                                new_df.drop(new_df[new_df[reservationid] == reservation_id].head(1).index, inplace=True)
                            else:
                                break
                        temp_df.drop(temp_df[temp_df['time'] == new_startTime].head(1).index, inplace = True) 
                            
    
    print("\n remaining  reservations:\n")
    ori_df[endTime] = pandas.to_datetime(ori_df[endTime], format="%Y-%m-%d %H:%M:%S")
    ori_df[endTime] = ori_df[endTime] + timedelta(seconds=1)
    print(ori_df.to_string(index=False))
    if(deleted_df.shape[0] > 0):
        deleted_df = deleted_df.drop('status', axis=1)
        deleted_df[endTime] = deleted_df[endTime] + timedelta(seconds=1)
        print("\n Deleted reservations:")
        print(deleted_df.to_string(index=False))
        deleted_df = deleted_df.sort_values(by=user)
        deleted_df.style.set_properties(**{"text-align": "left"})

skip_list = "bthomas,tthomas"
include_list = "gthomas"
delete="false"
reserve(ori_df, "2",skip_list, include_list, delete)
