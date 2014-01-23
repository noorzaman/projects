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

#last updated 12062013



# GLOBALS TO HELP DEVELOPMENT 
USE_DUMMY_DATA = False
SLEEP_INTERVAL = 1
WU_SLEEP_INTERVAL = 6
DEBUG = False
USE_LOCAL_CACHE = True

# geo data
geoname_api_username = 'nurul.zaman@gmail.com'

# world weather online
wo_api_key_primary = 'fet35k348tqsnsh29bkhnwer'
wo_api_key_backup = 'kp6pmd4memtck496jrkrdufn' 
wo_api_key = wo_api_key_primary

wo_api_site = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx'
wo_api_site_curr = 'http://api.worldweatheronline.com/premium/v1/weather.ashx'


# weather underground
wu_api_key = '52eb83e5e3dc10e0'
wu_api_site = 'http://api.wunderground.com/api/' + wu_api_key
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
    
    if DEBUG: print "**EXEC: get_lat_long_for_zip(zip_code):", zip_code
    
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
    
    if DEBUG: print "**EXEC: get_zip_for_lat_long(lat, lng):", lat, lng
    
    url = "http://api.geonames.org/findNearbyPostalCodesJSON?username=%s&country=US&lat=%s&lng=%s" % (geoname_api_username, lat, lng)
    r = requests.get(url)
    data = r.json()
    if('status' in data and data['status']['value'] == 12):
        raise RuntimeError('Invalid coordinates')
    zip_code = data["postalCodes"][0]['postalCode']
    return str(zip_code)



#####
# World weather online forecast data
#####
def get_weather_forecast_wonline(q_zip):

    if DEBUG: print "**EXEC: get_weather_forecast_wonline(q_zip):", q_zip
    
    forecast_arr = []
    q = wo_api_site_curr + "?key=" + get_wo_api_key() + "&q=" + q_zip + "&num_of_days=10&tp=24&format=json"  
    if DEBUG: print "\n", "target url:", q, "\n"
    
    forecast_date = datetime.datetime.now().date()
    forecast_file_name = "wo_forecast10day" + "_" + str(forecast_date)  + "_" + q_zip + ".json"
    if DEBUG: print "\n", "forecast_file_name:", forecast_file_name, "\n"
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
        high = float(h_daily['maxtempC']) # fahrenheit maxtempF
        low = float(h_daily['mintempC']) # fahrn mintempF
        
        daily_data = (h_daily_date, high, low)
        
        forecast_arr.append(daily_data)
    
    return forecast_arr
        





#####
# Calculating calendar dates for each month of the year to be fed to the historic data api (wonline)
#####
def create_monthly_history_dates(start_date, end_date=None):
    
    if DEBUG: print "**EXEC: create_monthly_history_dates(start_date, end_date=None):", start_date, end_date
    
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
# In case we want to forecast in the past (for calibration)
#####
def create_historic_forecast_dates(start_date):
    
    if DEBUG: print "**EXEC: create_historic_forecast_dates(start_date):", start_date

    Date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    forecast_date = Date + datetime.timedelta(days=9) #start day + 9
    forecast_date = forecast_date.strftime("%Y-%m-%d")
    monthly_dates = create_monthly_history_dates(start_date, forecast_date)
    return monthly_dates

 
   

#####
# Get historic data for a zip code using a start date and end date (world online)
#####
def get_weather_historic_wonline(query_zip, start_date, end_date):
    
    if DEBUG: print "**EXEC: get_weather_historic_wonline(query_zip, start_date, end_date)", \
        query_zip, start_date, end_date
    
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
        #high = float(h_daily['maxtempF'])
        #low = float(h_daily['mintempF'])
        high = float(h_daily['maxtempC'])
        low = float(h_daily['mintempC'])
        
        daily_data = (h_daily_date, high, low)
        
        if DEBUG: print "Daily data: ", daily_data
            
        hist_arr.append(daily_data)
    
    return hist_arr


    


#####
# Formula for growing degree day
#####
def get_degree_day(temp_tuple, base_temp=5, chilling=False):
    
    if chilling:
        return get_chilling_day(temp_tuple)

    if DEBUG: print "**EXEC: get_degree_day(temp_tuple, base_temp=5)", temp_tuple, base_temp
    #if DEBUG: print "temp_tuple=", temp_tuple
        
    high_temp = float(temp_tuple[1])
    low_temp = float(temp_tuple[2])
    base_temp = float(base_temp)
    
    
    degree_day = (high_temp + low_temp)/2 - base_temp
    
    if degree_day < 0:
        degree_day = 0 

    if DEBUG: print "high_temp, low_temp, base_temp, degree_day", high_temp, low_temp, base_temp, degree_day
        
    return degree_day


# Helper method to calculate the degree day
def get_chilling_day(temp_tuple, base_temp=20):

    if DEBUG: print "**EXEC: get_degree_day(temp_tuple, base_temp=20)", temp_tuple, base_temp

    high_temp = float(temp_tuple[1])
    low_temp = float(temp_tuple[2])
    base_temp = float(base_temp)
    
    chilling_day = base_temp - (high_temp + low_temp)/2
    
    #if chilling_day < 0:
    #    chilling_day = 0 

    if DEBUG: print "high_temp, low_temp, base_temp, chilling_day", high_temp, low_temp, base_temp, chilling_day
        
    return chilling_day


#####
# Get degree day sum for the forecast
# - gets the 10 day forecast
# - calculates the months dates leading upto today
# - gets the historic data
# - applies the formula to get the accumulted degree days
#####
def get_degree_day_sum_wonline(zip_code, start_date, base_temp=5, end_date=None, chilling=False):
        
    if DEBUG: print "**EXEC: get_degree_day_sum_wonline(zip_code, start_date, base_temp=5, end_date=None, chilling=False)", \
        zip_code, start_date, base_temp, end_date, chilling
    
    hist_dict = {}
    hist_dates = create_monthly_history_dates(start_date, end_date)

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
    yesterday_historic_temp = None
    for k, v in hist_dict.iteritems():
        for daily_temp_h in v:
            yesterday_historic_temp = daily_temp_h
            degree_day = get_degree_day(daily_temp_h, base_temp, chilling)
            if DEBUG: print "daily_temp=", daily_temp_h, "degree_day=", degree_day
            degree_days.append(degree_day)

    if len(degree_days) > 0:
        degree_days = degree_days[:-1] # remove last day - it is added to the forecast
    
    hist_degree_days_sum = sum(degree_days)
    if DEBUG: print "\n**historical degree days sum:", hist_degree_days_sum, "\n"

    # create array for forecast degree days sum
    forecast_degree_day_sum = []
    
    #append yesterday's data to it
    #forecast_degree_day_sum.append(last_historic_degree_day)
    
    #lookup forecast for next 10 days
    forecast_arr = get_weather_forecast_wonline(zip_code)
    
    #if we are not forecasting for the future (next 10 days)
    #we are probably just trying to look at the forecast for past 
    # i.e. forecast past (fp) - kinda wonky name
    if end_date is not None:
        end_date_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        date_10_days_ago =  datetime.date.today() - datetime.timedelta(days=10)

        if end_date_date <  date_10_days_ago: 
            fp_dates = create_historic_forecast_dates(end_date)
            
            forecast_arr = [] #reinitialize
            for fp in fp_dates:
                fp_start_date = fp[0]
                fp_end_date = fp[1]
                fp_results = get_weather_historic_wonline(zip_code, fp_start_date, fp_end_date)
                for fp_result in fp_results: 
                    forecast_arr.append(fp_result)
                    
    # now tag along yesterdays (the first day before fp_dates)
    # the reason is that it is used to break up cumulative probablitlies into absolutes
    if yesterday_historic_temp is not None:
        forecast_arr.insert(0, yesterday_historic_temp)
 
    if DEBUG: print "\n** forecast:", forecast_arr
    rolling_degree_day_sum = hist_degree_days_sum
    for daily_temp_f in forecast_arr:
        degree_day = get_degree_day(daily_temp_f, base_temp, chilling)
        rolling_degree_day_sum += degree_day
        degree_day_dict = {} #dict
        degree_day_dict[daily_temp_f[0]] = rolling_degree_day_sum #dict
        forecast_degree_day_sum.append(degree_day_dict) #dict
        #forecast_degree_day_sum.append(rolling_degree_day_sum)
        if DEBUG: print "degree day:", degree_day, "rolling degree day sum", rolling_degree_day_sum
    
    if DEBUG: print "forecast_degree_day_sum=", forecast_degree_day_sum
    return forecast_degree_day_sum


 


#####
# On error tries to use some trouble shooting measures
# - tries again in case random http err
# - switches key in case primary ran over quota
# - switches the source for last ditch effort
#####
# takes care of all errors or selecting different sources
def get_degree_day_sum(zip_code, start_date, base_temp, end_date=None, chilling=False):
    
    if DEBUG: print "**EXEC: get_degree_day_sum(zip_code, start_date, base_temp, end_date=None):", \
        zip_code, start_date, base_temp, end_date, chilling
    
    #valid_zipcode = zipcode_supported(zip_code)
    #if not valid_zipcode:
    #    return [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    
    try:
        return get_degree_day_sum_wonline(zip_code, start_date, base_temp, end_date, chilling)
    except:
        pass
    
    #try one more time - cached date will automatically be skipped
    try:
        return get_degree_day_sum_wonline(zip_code, start_date, base_temp, end_date, chilling)
    except:
        pass
    
    #switch to backup key if primary key is not working
    try:
        set_wo_api_key(wo_api_key_backup)
        return get_degree_day_sum_wonline(zip_code, start_date, base_temp, end_date, chilling)
    except:
        return [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    
    #is it truly time to use the paid account ?
    try:
        set_wo_api_key(wo_api_key_leaftime_paid)
        return get_degree_day_sum_wonline(zip_code, start_date, base_temp, end_date, chilling)
    except:
        return [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]


    


#####
# Finally we get our prediictions
#####
def convert_from_cumulative_to_discrete(event_predictions):
    discrete_predictions = []
    for idx, p in enumerate(event_predictions):
        if idx == len(event_predictions) - 1:
            break
        discrete_p = event_predictions[idx + 1] - event_predictions[idx]
        discrete_p = "%.2f" % discrete_p
        discrete_predictions.append(discrete_p)
        
    if DEBUG: print "discrete_predictions", discrete_predictions


        
def is_end_date_greater(start_date, end_date):
    start_date_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()    
    return end_date_date > start_date_date
        

    
def get_zero_probabilities(probs_in_array):
    zero_probs_arr = []
    for i in range(probs_in_array):
        zero_probs_arr.append(0.0)
    return zero_probs_arr



def get_event_type_predictions(event_type, gdd_arr):
    
    event_predictions = None
    model_file_name = None
    
    if event_type == "start_of_spring": #Bud Break
        model_file_name = "start_of_spring_model2007.pkl"
    elif  event_type == "end_of_spring": #Leaf Maturity (Greenest)
        model_file_name = "end_of_spring_model2007.pkl"
    elif  event_type == "start_of_fall": #Beginning of fall colors
        model_file_name = "start_of_fall_model2007.pkl"    
    elif  event_type == "middle_of_fall": #Most Intense Fall Colors
        model_file_name = "middle_of_fall_model2007.pkl"
    elif  event_type == "end_of_fall": #End of leaf drop
        model_file_name = "end_of_fall_model2007.pkl"
    
    #feed the values to the model
    model_clone = joblib.load(model_file_name)

    #Get right number of dimesions and shape for non-dim and 1-dim
    gdd_arr = np.ma.atleast_2d(gdd_arr)
    gdd_arr = np.transpose(gdd_arr)
    event_predictions = model_clone.predict_proba(gdd_arr)[:,1]
    
    if DEBUG: print "event_predictions", event_predictions
    discrete_predicitons = convert_from_cumulative_to_discrete(event_predictions)
    if DEBUG: print "discrete_predicitons", discrete_predicitons
        
    return event_predictions



def get_predictions_by_zip(zip_code, end_date=None):
    
    if DEBUG: print "**EXEC: get_predictions_by_zip(zip_code, end_date=None):", \
        zip_code, end_date
        
    lat, lng = get_lat_long_for_zip(zip_code)
    return get_predictions(lat, lng, end_date)


#####        
# Degree day calculations are from the start of the year
# So if someone looks at March 1, 2009 - we start accumulating from Jan. 1, 2009
#####
# Degree day calculations are from the start of the year
# So if someone looks at March 1, 2009 - we start accumulating from Jan. 1, 2009
def get_gdd_start_date(end_date=None):

    OLDEST_YEAR_SUPPORTED = 2009

    DEF_START_MONTH = "1"
    DEF_START_DAY = "1"
    DEF_START_YEAR = "2013"
    DEF_START_DATE = DEF_START_YEAR + "-" + DEF_START_MONTH + "-" + DEF_START_DAY
    
    if end_date is None:
        return DEF_START_DATE
    
    start_date = None
    try:
        start_year = end_date.split("-")[0]
        
        if int(start_year) < OLDEST_YEAR_SUPPORTED: 
            return DEF_START_DATE
        
        start_date = start_year + "-" + DEF_START_MONTH + "-" + DEF_START_DAY
        # check if this is a real date and end date > start date
        start_date_check = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_check = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date_check > end_date_check:
            return DEF_START_DATE
    except:
        return DEF_START_DATE
    
    return start_date



def get_chilling_start_date(end_date=None):

    OLDEST_YEAR_SUPPORTED = 2009

    DEF_START_MONTH = "8"
    DEF_START_DAY = "15"
    DEF_START_YEAR = "2013"
    DEF_START_DATE = DEF_START_YEAR + "-" + DEF_START_MONTH + "-" + DEF_START_DAY
    
    if end_date is None:
        return DEF_START_DATE
    
    start_date = None
    try:
        start_year = end_date.split("-")[0]
        
        if int(start_year) < OLDEST_YEAR_SUPPORTED: 
            return DEF_START_DATE
        
        start_date = start_year + "-" + DEF_START_MONTH + "-" + DEF_START_DAY
        # check if this is a real date and end date > start date
        start_date_check = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_check = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date_check > end_date_check:
            return DEF_START_DATE
    except:
        return DEF_START_DATE
    
    return start_date
    


def get_predictions (lat, lng, end_date=None): 
    
    if DEBUG: print "**EXEC: get_predictions (lat, lng, end_date=None):", \
        lat, lng, end_date
    
    event1_predictions, event2_predictions, event3_predictions, event4_predictions, event5_predictions = \
        None, None, None, None, None

    GROWING_BASE_TEMP = 4
    GDD_START_DATE = get_gdd_start_date(end_date)
    if DEBUG: print "GDD_START_DATE", GDD_START_DATE
        
    CDD_START_DATE = get_chilling_start_date(end_date)
    if DEBUG: print "CDD_START_DATE", CDD_START_DATE
    
    json_resp_dict = {}
    json_resp_dict['lat'] = lat
    json_resp_dict['lng'] = lng
    
    zip_code = get_zip_for_lat_long(lat, lng)    
    
    #get growth degree days
    gdds = get_degree_day_sum(zip_code, GDD_START_DATE, GROWING_BASE_TEMP, end_date)
    
    #extract gdds out of the dictionary
    gdd_arr = [gdd.values()[0] for gdd in gdds]
    if is_end_date_greater(CDD_START_DATE, end_date):
        event1_predictions, event2_predictions = get_zero_probabilities(11), get_zero_probabilities(11)
    else:
        event1_predictions = get_event_type_predictions("start_of_spring", gdd_arr)
        event2_predictions = get_event_type_predictions("end_of_spring", gdd_arr)
    

    #get chilling degree days
    CHILLING_BASE_TEMP = 20
    if not is_end_date_greater(CDD_START_DATE, end_date):
        event3_predictions, event4_predictions, event5_predictions = \
            get_zero_probabilities(11),get_zero_probabilities(11),get_zero_probabilities(11)
    else:
        cdds = get_degree_day_sum(zip_code, CDD_START_DATE, CHILLING_BASE_TEMP, end_date, True) #chilling
        cdd_arr = [cdd.values()[0] for cdd in cdds]
        event3_predictions = get_event_type_predictions("start_of_fall", cdd_arr)
        event4_predictions = get_event_type_predictions("middle_of_fall", cdd_arr)
        event5_predictions = get_event_type_predictions("end_of_fall", cdd_arr)

        
    predictions_arr = []
    for gdd, event_1, event_2, event_3, event_4, event_5 in \
    zip(gdds, event1_predictions,event2_predictions, event3_predictions, event4_predictions, event5_predictions):

        events_container = {}
        events_dict = {}
        events_dict['event_1'] = event_1
        events_dict['event_2'] = event_2
        events_dict['event_3'] = event_3
        events_dict['event_4'] = event_4
        events_dict['event_5'] = event_5
        
        events_container['date'] = gdd.keys()[0]
        events_container['events'] = events_dict
        
        predictions_arr.append(events_container)
        
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
elif action == 'get_weather_forecast_wonline':
    result = get_weather_forecast_wonline(action_args[0])
elif action == 'create_monthly_history_dates':
    result = create_monthly_history_dates(action_args[0])
elif action == 'get_weather_historic_wonline':
    result = get_weather_historic_wonline(action_args[0], action_args[1], action_args[2])
elif action == 'get_degree_day_sum_wonline':
    result = get_degree_day_sum_wonline(action_args[0], action_args[1], action_args[2])
elif action == 'get_degree_day_sum':
    result = get_degree_day_sum(action_args[0], action_args[1], action_args[2])
elif action == 'get_predictions':
    result = get_predictions (action_args[0], action_args[1],action_args[2])
elif action == 'get_predictions_by_zip':
    result = get_predictions_by_zip (action_args[0], action_args[1])
else:
    if action_args is not None:
        result = locals()[action](action_args)
    else:
        result = locals()[action]()

print(json.dumps(result))
