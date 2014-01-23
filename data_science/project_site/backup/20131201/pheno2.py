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



# GLOBALS TO HELP DEVELOPMENT 
USE_DUMMY_DATA = False
SLEEP_INTERVAL = 3
DEBUG = False
#DEBUG = True
USE_LOCAL_CACHE = True

# setup our keys and urls
wu_api_key = '52eb83e5e3dc10e0'
wu_api_site = 'http://api.wunderground.com/api/' + wu_api_key
#geoname_api_username = 'pheno@jonnymoon.com'
geoname_api_username = 'nurul.zaman@gmail.com'

# historical data from world weather online
wo_api_key = 'fet35k348tqsnsh29bkhnwer'
#wo_api_key = 'kp6pmd4memtck496jrkrdufn'
wo_api_site = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx'
wo_api_site_curr = 'http://api.worldweatheronline.com/premium/v1/weather.ashx'

wu_current = wu_api_site + '/conditions/q/'
wu_forecast3day = wu_api_site + '/forecast/q/'
wu_forecast10day = wu_api_site + '/forecast10day/q/'


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
def get_weather_forecast(q_zip):
    
    if USE_DUMMY_DATA == True:
        if DEBUG: print "Returning dummy forecast data"
        f_dummy_data = get_dummy_data_for_forecast()
        return f_dummy_data
    
    forecast_arr = []
    
    #q = wu_forecast10day + q_state + "/" + q_zip + ".json"
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
        high = float(day['high']['fahrenheit'])
        low = float(day['low']['fahrenheit'])
        high_low = (high, low)
        
        forecast_arr.append(high_low)
        
    return forecast_arr



#####
# World weather online forecast data
#####
def get_weather_forecast_wonline(q_zip):
    
    if USE_DUMMY_DATA == True:
        if DEBUG: print "Returning dummy forecast data"
        f_dummy_data = get_dummy_data_for_forecast()
        return f_dummy_data
    
    forecast_arr = []
    #q = "http://api.worldweatheronline.com/premium/v1/weather.ashx?key=" + wo_api_key + "&q=" + q_zip + "&num_of_days=10&tp=24&format=json"
    q = wo_api_site_curr + "?key=" + wo_api_key + "&q=" + q_zip + "&num_of_days=10&tp=24&format=json"  
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
        # length of day calculation
        astronomy = h_daily['astronomy'][0]
        sunrise = astronomy['sunrise']
        sunset = astronomy['sunset']

        sunrise = datetime.datetime.strptime(sunrise, DATE_FMT)
        sunset = datetime.datetime.strptime(sunset, DATE_FMT)
        length_of_day = (sunset - sunrise).total_seconds()
        
        # hig and low temp
        high = float(h_daily['maxtempF'])
        low = float(h_daily['mintempF'])
        
        # precipitation and humidity, calculate average
        hourly_precips = []
        hourly_humiditys = []
        for h_hourly in h_daily['hourly']:
            hourly_precips.append(float(h_hourly['precipMM']))
            hourly_humiditys.append(float(h_hourly['humidity']))
        
        precip_avg = np.mean(hourly_precips)
        humidity_avg = np.mean(hourly_humiditys)
        
        daily_data = (high, low, length_of_day, precip_avg, humidity_avg)
        
        forecast_arr.append(daily_data)
    
    return forecast_arr
        



#####
# Calculating calendar dates for each month of the year to be fed to the historic data api
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
# Get historic data for a zip code using a start date and end date
#####
def get_weather_historic(query_zip, start_date, end_date):
    
    if USE_DUMMY_DATA == True:
        if DEBUG: print "Returning dummy historic data"
        h_dummy_data = get_dummy_data_for_history()
        return h_dummy_data
    
    #q = create_wonline_query(query_zip, start_date, end_date)
    
    q = wo_api_site + "?q=" + str(query_zip) + "&format=json&date=" \
        + start_date + "&enddate=" + end_date + "&key=" + wo_api_key    
    if DEBUG: print "history url: ", q
    #q = wo_api_site + "?q=" + str(query_zip) + "&format=json&date=" + start_date + "&enddate=" + end_date + "&key=" + wo_api_key
    
    historic_file_name = "wo_historic" +  "_" + start_date + "__" + end_date +  "_" + query_zip + ".json"
    h_data = read_cache_data_if_any(historic_file_name)
    if h_data == None:
        r = requests.get(q)
        h_data = r.json()
        write_cache_data(h_data, historic_file_name)
        time.sleep(SLEEP_INTERVAL)
    
    DATE_FMT = '%I:%M %p'  
    hist_arr = []
    for h_daily in h_data['data']['weather']:
        
        # length of day calculation
        astronomy = h_daily['astronomy'][0]
        sunrise = astronomy['sunrise']
        sunset = astronomy['sunset']

        sunrise = datetime.datetime.strptime(sunrise, DATE_FMT)
        sunset = datetime.datetime.strptime(sunset, DATE_FMT)
        length_of_day = (sunset - sunrise).total_seconds()
        
        # hig and low temp
        high = float(h_daily['maxtempF'])
        low = float(h_daily['mintempF'])
        
        # precipitation and humidity, calculate average
        hourly_precips = []
        hourly_humiditys = []
        for h_hourly in h_daily['hourly']:
            hourly_precips.append(float(h_hourly['precipMM']))
            hourly_humiditys.append(float(h_hourly['humidity']))
        
        precip_avg = np.mean(hourly_precips)
        humidity_avg = np.mean(hourly_humiditys)
        
        daily_data = (high, low, length_of_day, precip_avg, humidity_avg)
        
        if DEBUG: 
            print "Daily data: ", daily_data
            
        hist_arr.append(daily_data)
    
    return hist_arr





#####
# Formula for growing degree day
#####
def get_degree_day(temp_tuple, base_temp):
    high_temp = float(temp_tuple[0])
    low_temp = float(temp_tuple[1])
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
def get_degree_day_sum(zip_code, start_date, base_temp):
    
#    valid_zipcode = zipcode_supported(zip_code)
#    if not valid_zipcode:
#        return [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    
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
        
        hist_arr = get_weather_historic(zip_code, h_start_date, h_end_date)
        
        if DEBUG: print "\n** historic:", hist_arr
        
        hist_dict[count] = hist_arr
        count += 1
        if DEBUG: 
            if SLEEP_INTERVAL > 0:
                if not USE_DUMMY_DATA: 
                    print "Sleeping for ",  SLEEP_INTERVAL, "seconds"
                    time.sleep(SLEEP_INTERVAL)
    
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
        forecast_degree_day_sum.append(rolling_degree_day_sum)
        if DEBUG: print "degree day:", degree_day, "rolling degree day sum", rolling_degree_day_sum
        
    return forecast_degree_day_sum



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
elif action == 'get_weather_forecast':
    result = get_weather_forecast(action_args[0])
elif action == 'get_weather_forecast_wonline':
    result = get_weather_forecast_wonline(action_args[0])
elif action == 'create_monthly_history_dates':
    result = create_monthly_history_dates(action_args[0])
elif action == 'get_weather_historic':
    result = get_weather_historic(action_args[0], action_args[1], action_args[2])
elif action == 'get_degree_day_sum':
    result = get_degree_day_sum(action_args[0], action_args[1], action_args[2])
else:
    if action_args is not None:
        result = locals()[action](action_args)
    else:
        result = locals()[action]()

print(json.dumps(result))
