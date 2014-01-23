import sys
import json
import requests
import numpy as np
import urllib2
import datetime
import time
from calendar import monthrange

import json
import os.path

from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

#last updated 12022013

# GLOBALS TO HELP DEVELOPMENT 
USE_DUMMY_DATA = False
SLEEP_INTERVAL = 1
WU_SLEEP_INTERVAL = 6
DEBUG = False
#DEBUG = True
USE_LOCAL_CACHE = True

# setup our keys and urls
wu_api_key = '52eb83e5e3dc10e0'
wu_api_site = 'http://api.wunderground.com/api/' + wu_api_key
#geoname_api_username = 'pheno@jonnymoon.com'
geoname_api_username = 'nurul.zaman@gmail.com'

# historical data from world weather online
wo_api_key_primary = 'fet35k348tqsnsh29bkhnwer'
wo_api_key_backup = 'kp6pmd4memtck496jrkrdufn'
wo_api_key = wo_api_key_primary

wo_api_site = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx'
wo_api_site_curr = 'http://api.worldweatheronline.com/premium/v1/weather.ashx'

wu_current = wu_api_site + '/conditions/q/'
wu_forecast3day = wu_api_site + '/forecast/q/'
wu_forecast10day = wu_api_site + '/forecast10day/q/'



#####
# In case of failure we will dynamically different keys
#####
def set_wo_api_key(new_wo_api_key):
    wo_api_key = new_wo_api_key

def get_wo_api_key():
    return wo_api_key



#####
# Returns dummy forecast
#####
def get_dummy_forecast():
    result = [
        {'date': '2013-11-01', 'chance': 43, 'event': 'leaves budding'},
        {'date': '2013-11-02', 'chance': 52, 'event': 'leaves budding'},
        {'date': '2013-11-03', 'chance': 67, 'event': 'leaves budding'},
        {'date': '2013-11-04', 'chance': 73, 'event': 'leaves budding'},
        {'date': '2013-11-05', 'chance': 85, 'event': 'leaves budding'},
        {'date': '2013-11-06', 'chance': 93, 'event': 'leaves budding'},
        {'date': '2013-11-07', 'chance': 95, 'event': 'leaves budding'},
        {'date': '2013-11-08', 'chance': 86, 'event': 'leaves budding'},
        {'date': '2013-11-09', 'chance': 72, 'event': 'leaves budding'},
        {'date': '2013-11-10', 'chance': 61, 'event': 'leaves budding'},
    ]

    return {'days':result}

#####
# Returns dummy forecast and historic test data
#####
def get_dummy_data_for_forecast():
    
    f_dummy_data = [(70,60), (71, 65), (80, 56), (88, 45), (76, 65), \
                (80, 76), (77, 56), (80, 70), (88, 75), (69, 51)] 
    return f_dummy_data

def get_dummy_data_for_history():
    
    h_dummy_data = [(86.0, 56.0), (83.0, 60.0), (83.0, 57.0), (82.0, 56.0), \
                  (83.0, 54.0), (90.0, 53.0), (98.0, 62.0), (94.0, 60.0), \
                  (95.0, 62.0), (88.0, 57.0), (82.0, 57.0), (83.0, 54.0), \
                  (83.0, 56.0), (85.0, 55.0), (82.0, 53.0), (83.0, 55.0), \
                  (76.0, 52.0), (83.0, 53.0), (88.0, 53.0), (79.0, 53.0), \
                  (73.0, 55.0), (74.0, 48.0), (82.0, 53.0), (76.0, 54.0), \
                  (71.0, 50.0), (76.0, 48.0), (79.0, 48.0), (84.0, 50.0), \
                  (79.0, 54.0), (78.0, 53.0)]
    return h_dummy_data


#####
# Reads data from the local cache instead of going out every time
#####
def read_cache_data_if_any(cache_file):
    if USE_LOCAL_CACHE == False:
        return None
    
    cache_file = 'cache/' + cache_file;

    if not os.path.isfile(cache_file):
        return None
    
    json_file_data = open(cache_file)
    json_data = json.load(json_file_data)
    if DEBUG: print "** reading from local cache", cache_file
    return json_data
    

#####
# Writes data to the local cache
#####
def write_cache_data(json_data, cache_file):
    cache_file = 'cache/' + cache_file;
    try:
        with open(cache_file, 'w') as f:
            json.dump(json_data, f, ensure_ascii=False)
        return True
    except:
        return False


#####
# Returns latitutde and longitude given a zipe code
#####
def get_lat_long_for_zip(zip_code):
    url = "http://api.geonames.org/findNearbyPostalCodesJSON?username=%s&country=US&postalcode=%s" % (geoname_api_username, zip_code)
    r = requests.get(url)
    data = r.json()
    if('status' in data and data['status']['value'] == 17):
        raise RuntimeError('Invalid ZIP code')
    lat = data["postalCodes"][0]['lat']
    lng = data["postalCodes"][0]['lng']
    return (float(lat), float(lng))


#####
# Returns latitude and longitude given a zip code 
#####
def get_zip_for_lat_long(lat, lng):
    url = "http://api.geonames.org/findNearbyPostalCodesJSON?username=%s&country=US&lat=%s&lng=%s" % (geoname_api_username, lat, lng)
    r = requests.get(url)
    data = r.json()
    if('status' in data and data['status']['value'] == 12):
        raise RuntimeError('Invalid coordinates')
    zip_code = data["postalCodes"][0]['postalCode']
    return str(zip_code)





#####
# Weather underground forecast data
#####
def get_weather_forecast_wunder(q_zip):

    forecast_arr = []
    
    q = wu_forecast10day + q_zip + ".json"
    if DEBUG: print "\n", "forecast url: ", q, "\n"
    
    
    forecast_file_name = "wu_forecast10day" +  "_" + q_zip + ".json"
    forecast_data = read_cache_data_if_any(forecast_file_name)
    if forecast_data == None:
        r = requests.get(q)
        forecast_data = r.json()
        write_cache_data(forecast_data, forecast_file_name)
    
    for day in forecast_data['forecast']['simpleforecast']['forecastday']:
        #period = day['period'] - 1
        day_date = str(day['date']['year']) + "-" + str(day['date']['month']) + "-" + str(day['date']['day'])
        high = float(day['high']['fahrenheit'])
        low = float(day['low']['fahrenheit'])
        day_data = (day_date, high, low)
        
        forecast_arr.append(day_data)
        
    return forecast_arr





#####
# World weather online forecast data
#####
def get_weather_forecast_wonline(q_zip):
    
    forecast_arr = []
    q = wo_api_site_curr + "?key=" + get_wo_api_key() + "&q=" + q_zip + "&num_of_days=10&tp=24&format=json"  
    if DEBUG: print "\n", "target url:", q, "\n"
    
    forecast_file_name = "wo_forecast10day" + "_" + q_zip + ".json"
    forecast_data = read_cache_data_if_any(forecast_file_name)
    if forecast_data == None:
        r = requests.get(q)
        forecast_data = r.json()
        write_cache_data(forecast_data, forecast_file_name)
    
    DATE_FMT = '%I:%M %p'  
    forecast_arr = []
    for h_daily in forecast_data['data']['weather']:
        
        h_daily_date = h_daily['date']
        
        
        # hig and low temp
        high = float(h_daily['maxtempF'])
        low = float(h_daily['mintempF'])
        
        daily_data = (h_daily_date, high, low)
        
        forecast_arr.append(daily_data)
    
    return forecast_arr



#####
# Calculating calendar dates for each month of the year to be fed to the historic data api (wonline)
#####
def create_monthly_history_dates(start_date, end_date=None):
    result = []
    q_start = None
    q_end = None
    num_of_days = 0
    
    # current date will be handled by forecast not history
    if end_date == None:
        end_date = time.strftime("%Y-%m-%d")
    
    # now move the histoic end date back by one day
    if end_date == time.strftime("%Y-%m-%d"):
        corrected_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.timedelta(days=1)
        end_date = corrected_date.strftime("%Y-%m-%d")
        
    sdate_split = start_date.split('-')
    syear, smonth, sday = (int(sdate_split[0]), int(sdate_split[1]), int(sdate_split[2]))
    
    edate_split = end_date.split('-')
    eyear, emonth, eday = (int(edate_split[0]), int(edate_split[1]), int(edate_split[2]))

    if syear != eyear:
        raise ValueError('Start year has to be the same as end year')
    
    # start date and end date are in same month
    if smonth == emonth:
        num_of_days = eday - sday
        query = (start_date, end_date, num_of_days)
        result.append(query)
        return result
    
    q_range = range(smonth, emonth + 1)

    first_month = True

    for idx,r in enumerate(q_range):
        
        q_start = None
        days_in_month = monthrange(syear, r)[1]
        if idx == 0:
            q_start = start_date
        else:
            q_start = str(syear) + "-" + str(r) + "-1"
        
        if idx == len(q_range) - 1:
            q_end = end_date
        else:
            q_end = str(syear) + "-" + str(r) + "-" + str(days_in_month)
        
        #num_of_days = get_num_of_days(q_start, q_end)
    
        sday = int(q_start.split('-')[2])
        eday = int(q_end.split('-')[2])
        num_of_days = eday + 1 - sday
       
        query = (q_start, q_end, num_of_days)
        result.append(query)
        first_month = False
   
    return result
     
   

#####
# Our backup strategy uses weather underground which requires
# historic data to be downloaded for each day.
#####
def create_daily_history_dates(start_date, end_date=None):
    monthly_dates = create_monthly_history_dates(start_date, end_date)
    query_days = []
    for md in monthly_dates:
        sdate = md[0]
        num_of_days = md[2]
        date_split = sdate.split("-")
        for count in range(num_of_days):
            query_days.append(str(date_split[0]) + "-" + str(date_split[1]) + "-" + str(int(date_split[2]) + count))
            
    return query_days



#####
# Get historic data for a zip code using a start date and end date (world online)
#####
def get_weather_historic_wonline(query_zip, start_date, end_date):
    
    #q = create_wonline_query(query_zip, start_date, end_date)
    
    q = wo_api_site + "?q=" + str(query_zip) + "&format=json&date=" \
        + start_date + "&enddate=" + end_date + "&key=" + get_wo_api_key()    
    if DEBUG: print "history url: ", q

    #q = wo_api_site + "?q=" + str(query_zip) + "&format=json&date=" + start_date + "&enddate=" + end_date + "&key=" + wo_api_key
    
    historic_file_name = "wo_historic" +  "_" + start_date + "__" + end_date +  "_" + query_zip + ".json"
    h_data = read_cache_data_if_any(historic_file_name)
    if h_data == None:
        r = requests.get(q)
        h_data = r.json()
        write_cache_data(h_data, historic_file_name)
        if SLEEP_INTERVAL > 0:
            if DEBUG: print "Sleeping for ",  SLEEP_INTERVAL, "seconds"
            time.sleep(SLEEP_INTERVAL)
    
    DATE_FMT = '%I:%M %p'  
    hist_arr = []
    for h_daily in h_data['data']['weather']:
        
        h_daily_date = h_daily['date']
        
        # hig and low temp
        high = float(h_daily['maxtempF'])
        low = float(h_daily['mintempF'])
        
        daily_data = (h_daily_date, high, low)
        
        if DEBUG: print "Daily data: ", daily_data
            
        hist_arr.append(daily_data)
    
    return hist_arr


#####
# Get historic data for a zip code using a start date and end date (world online)
#####
def get_weather_historic_wunder(query_zip, historic_date):
    
    formatted_date = ""
    for ch in historic_date:
        if ch != '-':
            formatted_date += ch
    
    #"http://api.wunderground.com/api/52eb83e5e3dc10e0/history_20060405/q/94538.json"
    q = wu_api_site + "/history_" + formatted_date + "/q/" + query_zip + ".json"
    if DEBUG: print "history url: ", q

    historic_file_name = "wu_historic" +  "_" + formatted_date +  "_" + query_zip + ".json"
    
    h_data = read_cache_data_if_any(historic_file_name)
    if h_data == None:
        r = requests.get(q)
        h_data = r.json()
        write_cache_data(h_data, historic_file_name)
        if WU_SLEEP_INTERVAL >0:
            if DEBUG: print "Sleeping for ",  WU_SLEEP_INTERVAL, "seconds"
            time.sleep(WU_SLEEP_INTERVAL)
    
    
    hist_arr = []
    h_daily_data = h_data['history']['dailysummary'][0]
    
    h_daily_date_str = h_daily_data['date'] 
    h_daily_date = str(h_daily_date_str['year']) + "-" + str(h_daily_date_str['mon']) + "-" + str(h_daily_date_str['mday'])
    
    high = float(h_daily_data['maxtempi'])
    low = float(h_daily_data['mintempi'])
    
    daily_data = (h_daily_date, high, low)
    if DEBUG: print "Daily data: ", daily_data
            
    hist_arr.append(daily_data)
    return hist_arr










#####
# Formula for growing degree day
#####
def get_degree_day(temp_tuple, base_temp):
    if DEBUG: print "temp_tuple=", temp_tuple
    high_temp = float(temp_tuple[1])
    low_temp = float(temp_tuple[2])
    base_temp = float(base_temp) 

    degree_day = (high_temp + low_temp)/2 - base_temp
    
    if degree_day < 0:
        degree_day = 0      
    return degree_day



#####
# Get degree day sum for the forecast
# - gets the 10 day forecast
# - calculates the months dates leading upto today
# - gets the historic data
# - applies the formula to get the accumulted degree days
#####
def get_degree_day_sum_wunder(zip_code, start_date, base_temp):

    if DEBUG: print "\n** EXECUTING:get_degree_day_sum_wunder:" , zip_code, start_date, base_temp
    
    forecast_degree_day_sum = []
    
    #lookup forecast for next 10 days
    forecast_arr = get_weather_forecast_wunder(zip_code)
    
    if DEBUG: print "\n** forecast:", forecast_arr
        
    hist_dict = {}
    if DEBUG: print start_date
    hist_dates = create_daily_history_dates(start_date)

    if DEBUG: print "history query dates:", hist_dates
    
    # degree days for history
    degree_days = []
    for hist_date in hist_dates:
        daily_temp_h = get_weather_historic_wunder(zip_code, hist_date)
        degree_day = get_degree_day(daily_temp_h[0], base_temp)
        degree_days.append(degree_day)
        
    hist_degree_days_sum = sum(degree_days)
    if DEBUG: print "\n**historical degree days sum:", hist_degree_days_sum, "\n"
        
    # create array for forecast degree days sum
    rolling_degree_day_sum = hist_degree_days_sum
    for daily_temp_f in forecast_arr:
        degree_day = get_degree_day(daily_temp_f, base_temp)
        rolling_degree_day_sum += degree_day
        #forecast_degree_day_sum.append(rolling_degree_day_sum)        
        degree_day_dict = {} #dict
        degree_day_dict[daily_temp_f[0]] = rolling_degree_day_sum #dict
        forecast_degree_day_sum.append(degree_day_dict) #dict
        forecast_degree_day_sum.append(rolling_degree_day_sum) #dict
 
        if DEBUG: print "degree day:", degree_day, "rolling degree day sum", rolling_degree_day_sum       
    return forecast_degree_day_sum



    
def get_degree_day_sum_wonline(zip_code, start_date, base_temp):
    
    if DEBUG: print "\n** EXECUTING:get_degree_day_sum_wonline:" , zip_code, start_date, base_temp
            
    forecast_degree_day_sum = []
    
    #lookup forecast for next 10 days
    forecast_arr = get_weather_forecast_wonline(zip_code)
    
    if DEBUG: print "\n** forecast:", forecast_arr
        
    hist_dict = {}
    if DEBUG: print start_date
    hist_dates = create_monthly_history_dates(start_date)

    if DEBUG: print "history query dates:", hist_dates
    
    count = 0
    for hist_date in hist_dates:
        h_start_date = hist_date[0]
        h_end_date = hist_date[1]
        
        if DEBUG: print "** getting data for", h_start_date, "-", h_end_date
        
        hist_arr = get_weather_historic_wonline(zip_code, h_start_date, h_end_date)
        
        if DEBUG: print "\n** historic:", hist_arr
        
        hist_dict[count] = hist_arr
        count += 1
    
    #get historical degree day sum 
    degree_days = []
    for k, v in hist_dict.iteritems():
        for daily_temp_h in v:
            degree_day = get_degree_day(daily_temp_h, base_temp)
            if DEBUG: print "daily_temp=", daily_temp_h, "degree_day=", degree_day
            degree_days.append(degree_day)

    hist_degree_days_sum = sum(degree_days)
    if DEBUG: print "\n**historical degree days sum:", hist_degree_days_sum, "\n"
    
    # create array for forecast degree days sum
    rolling_degree_day_sum = hist_degree_days_sum
    for daily_temp_f in forecast_arr:
        degree_day = get_degree_day(daily_temp_f, base_temp)
        rolling_degree_day_sum += degree_day
        degree_day_dict = {} #dict
        degree_day_dict[daily_temp_f[0]] = rolling_degree_day_sum #dict
        forecast_degree_day_sum.append(degree_day_dict) #dict
        #forecast_degree_day_sum.append(rolling_degree_day_sum)
        if DEBUG: print "degree day:", degree_day, "rolling degree day sum", rolling_degree_day_sum
        
    return forecast_degree_day_sum   






 


#####
# On error tries to use some trouble shooting measures
# - tries again in case random http err
# - switches key in case primary ran over quota
# - switches the source for last ditch effort
#####
def get_degree_day_sum(zip_code, start_date, base_temp):
    
    try:
        return get_degree_day_sum_wonline(zip_code, start_date, base_temp)
    except:
        pass
    
    #try one more time - cached date will automatically be skipped
    try:
        return get_degree_day_sum_wonline(zip_code, start_date, base_temp)
    except:
        pass
    
    #switch to backup key if primary key is not working
    try:
        set_wo_api_key(wo_api_key_backup)
        return get_degree_day_sum_wonline(zip_code, start_date, base_temp)
    except:
        pass
           
    # last ditch effort - try weather underground
    try:
        return get_degree_day_sum_wunder(zip_code, start_date, base_temp)
    except:
        return [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]



#####
# Finally we get our prediictions
#####
#def get_predictions (model_file_name, gdds):
#    
#    model_clone = joblib.load(model_file_name)
#    
#    #Get right number of dimesions and shape
#    #If it's non dimensional, do this
#    gdds = np.ma.atleast_2d(gdds)
#    
#    #If then it's (1, n), do this
#    gdds = np.transpose(gdds)
#    
#    #Predict
#    predictions = model_clone.predict_proba(gdds)[:,1]
#    nArr = [] # json-izable list
#    for prediction in predictions:
#        nArr.append(prediction)
#    return nArr 


def get_json_resp():
    
    pred_lat = "40.123"
    pred_lng ="40.123"
    pred_date = "2013-11-01"
    
    json_resp = []

    
    json_resp_dict = {}
    json_resp_dict['lat']=pred_lat
    json_resp_dict['lng']=pred_lng
    json_resp_dict['date']=pred_date
    
    for i in range(3):
        predictions = dict(leaf_budding='0.2345', leaf_greening='0.4565', leaf_peak='0.2344')
        json_resp.append(predictions)    
        
    json_resp_dict['predictions'] = json_resp 
    return json_resp_dict



def get_event_type_predictions(event_type, gdd_arr):
    
    if event_type == "start_of_spring":
        model_file_name = "start_of_spring_model2007.pkl"
    
        #feed the values to the model
        model_clone = joblib.load(model_file_name)
        
        #Get right number of dimesions and shape for non-dim and 1-dim
        gdd_arr = np.ma.atleast_2d(gdd_arr)
        gdd_arr = np.transpose(gdd_arr)
        event_predictions = model_clone.predict_proba(gdd_arr)[:,1]
        
        return event_predictions


def get_predictions_for_zip (zip_code, start_date, end_date=None):
    coords = get_lat_long_for_zip(zip_code)
    return get_predictions (coords[0], coords[1], start_date, end_date)
        
def get_predictions (lat, lng, start_date, end_date=None): 
    
    json_resp_dict = {}
    json_resp_dict['lat'] = lat
    json_resp_dict['lng'] = lng
    
    zip_code = get_zip_for_lat_long(lat, lng)    
    weather_forecast = get_weather_forecast_wonline(zip_code)

    gdds = get_degree_day_sum(zip_code, start_date, 50)

    if DEBUG: print "gdds=", gdds
 
    #extract gdds out of the dictionary
    gdd_arr = []
    for gdd in gdds:
        gdd_arr.append(gdd.values()[0])
        
    
    event1_predictions = get_event_type_predictions("start_of_spring", gdd_arr)
    
    predictions_arr = []
    for gdd, event_1, event_2, event_3 in zip(gdds, event1_predictions,event1_predictions,event1_predictions):
     
        date_dict = {}
        date_dict['date'] = gdd.keys()[0]
        
        events_dict = {}
        events_dict['event_1'] = event_1
        events_dict['event_2'] = event_2
        events_dict['event_3'] = event_3
        date_dict['events'] = events_dict
        predictions_arr.append(date_dict)
        
        
    json_resp_dict['predictions'] = predictions_arr
    return json_resp_dict


##########################################################
# Keep this bottom section at the bottom of the file
##########################################################

#sys.argv[0] # this is the file name
#sys.argv[1] # this is the variable passed from php

params = json.loads(sys.argv[1])

action = 'getForecast'; #default to getForecast if nothing is set

if('debug' in params):
	DEBUG = params['debug']

if('action' in params):
    action = params['action']
    action = action.strip()

action_args = None
if ('action_args' in params):
    action_args = params['action_args']

if DEBUG:
    print "action=", action
    if(action_args is not None): print "action_args=", ','.join(action_args)

result = None

if action == 'get_lat_long_for_zip':
    result = get_lat_long_for_zip(action_args[0])
elif action == 'get_zip_for_lat_long':
    result = get_zip_for_lat_long(action_args[0], action_args[1])
elif action == 'get_weather_forecast_wunder':
    result = get_weather_forecast_wunder(action_args[0])
elif action == 'get_weather_forecast_wonline':
    result = get_weather_forecast_wonline(action_args[0])
elif action == 'create_monthly_history_dates':
    result = create_monthly_history_dates(action_args[0])
elif action == 'create_daily_history_dates':
    result = create_daily_history_dates(action_args[0])
elif action == 'get_weather_historic_wonline':
    result = get_weather_historic_wonline(action_args[0], action_args[1], action_args[2])
elif action == 'get_weather_historic_wunder':
    result = get_weather_historic_wunder(action_args[0], action_args[1])
elif action == 'get_degree_day_sum_wunder':
    result = get_degree_day_sum_wunder(action_args[0], action_args[1], action_args[2])
elif action == 'get_degree_day_sum_wonline':
    result = get_degree_day_sum_wonline(action_args[0], action_args[1], action_args[2])
elif action == 'get_degree_day_sum':
    result = get_degree_day_sum(action_args[0], action_args[1], action_args[2])
elif action == 'get_predictions':
    #gdds = [96.5, 112.0, 116.0, 117.0, 117.0, 117.0, 117.5, 117.5, 117.5, 117.5]
    #result = get_predictions (action_args[0], gdds)
    result = get_predictions (action_args[0], action_args[1],action_args[2])
elif action == 'get_predictions_for_zip':
    result = get_predictions_for_zip (action_args[0], action_args[1])
elif action == 'get_json_resp':
    result = get_json_resp()
else:
    if action_args is not None:
        result = locals()[action](action_args)
    else:
        result = locals()[action]()

print(json.dumps(result))