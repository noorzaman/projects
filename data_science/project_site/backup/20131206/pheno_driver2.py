## location finders ##
echo -e  "\n** get_lat_long_for_zip\n"
#python pheno2.py '{"action":"get_lat_long_for_zip","action_args":["94538"]}'

echo -e "\n** get_zip_for_lat_longi\n"
#python pheno2.py '{"action":"get_zip_for_lat_long","action_args":["37.530815","-121.971215"]}'



## some utility methods ##
echo -e "\n** get_dummy_data_for_forecasti\n"
#python pheno2.py '{"action":"get_dummy_data_for_forecast"}'

echo -e "\n** get_dummy_data_for_history\n"
#python pheno2.py '{"action":"get_dummy_data_for_history"}'



## weather forecast and history (weather underground) ##
echo -e "\n** get_weather_forecast_wunder (for weather underground) \n"
#python pheno2.py '{"action":"get_weather_forecast_wunder","action_args":["94538"]}'



## weather forecast (world weather online) ##
echo -e "\n** get_weather_forecast (for world weather online) \n"
#python pheno2.py '{"action":"get_weather_forecast_wonline","action_args":["94538"]}'



## date calculation ##
echo -e "\n** create_monthly_history_dates \n"
#python pheno2.py '{"action":"create_monthly_history_dates","action_args":["2013-01-1"]}'

echo -e "\n** create_daily_history_dates \n"
#python pheno2.py '{"action":"create_daily_history_dates","action_args":["2013-01-1"]}'



## get historic weather (from world weather online) ##
echo -e "\n** get_weather_historic_wonline \n" 
#python pheno2.py '{"action":"get_weather_historic_wonline","action_args":["02238", "2013-10-01", "2013-10-30"]}'

echo -e "\n** get_weather_historic_wunder \n" 
#python pheno2.py '{"action":"get_weather_historic_wunder","action_args":["02238", "2013-11-25"]}'



## get degree day sum for the forecasts - wonline ##
echo -e "\n** get_degree_day_sum_wonline \n" 
#python pheno2.py '{"action":"get_degree_day_sum_wonline","action_args":["94538", "2013-9-1", "50"]}'

## get degree day sum for the forecasts - wunderground ##
echo -e "\n** get_degree_day_sum_wunder \n" 
#python pheno2.py '{"action":"get_degree_day_sum_wunder","action_args":["94538", "2013-11-25", "50"]}'


## get degree day sum - try mutliple source if first one down
echo -e "\n** get_degree_day_sum \n" 
python pheno2.py '{"action":"get_degree_day_sum","action_args":["90001", "2013-9-1", "50"]}'


## get predictions
echo -e "\n** get_predictions \n" 
#model_file_name = "start_of_spring_model2007.pkl"
#gdds = [1935.5, 1950.0, 1954.5, 1957.0, 1960.0, 1960.0, 1960.0, 1960.0, 1960.0, 1960.5]
python pheno2.py '{"action":"get_predictions","action_args":["start_of_spring_model2007.pkl", "dummy_array"]}'
