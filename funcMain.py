from toolBox import basicTool as bt
from toolBox import webTool as wt
import datetime 
import json
import os
import time
import random
import numpy as np
import math

def pull_stock_data(Stock_No, date, proxy_dict):
    #https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&date=20200401&stockNo=0050
    _stock_url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json'
    _stock_url += "&date=" + str(date)
    _stock_url += "&stockNo=" + str(Stock_No)

    return wt.RequestToWeb(_stock_url, "get", "", "", proxy_dict)

def init_stock_data(Stock_No_Array, proxy_source_dict):
    _db_table_formats = {
        "Date": ["TEXT PRIMARY KEY NOT NULL"],
        "Daily_Price_Mean": ["INTEGER",0]
    }
    #_datetime_now = datetime.datetime.now()
    _datetime_now = datetime.datetime.strptime("2020-04-01", "%Y-%m-%d")
    _stock_in_tw_first_date = datetime.datetime.strptime("1990-01-01", "%Y-%m-%d")
    _proxy_keys = list(proxy_source_dict.keys())

    #create table
    for _stock in Stock_No_Array:
        _processed_date = _datetime_now
        bt.createTable("Tw_Stock_Price_Per_Day", "Stock_"+str(_stock),_db_table_formats)
        _proxy_key = {}
        while _processed_date >= _stock_in_tw_first_date:
            while True:
                try:
                    _raw_data = pull_stock_data(_stock, _processed_date.strftime("%Y%m%d"), _proxy_key)
                    break
                except:
                    _proxy_sample = random.sample(proxy_source_dict.keys(),1)
                    _proxy_key = proxy_source_dict[_proxy_sample[0]]

            time.sleep(0.5)
            #month -1
            try:
                _processed_date = datetime.datetime(_processed_date.year, _processed_date.month-1, 1)
            except:
                _processed_date = datetime.datetime(_processed_date.year-1, 12, 1)
            
            try:
                _data_in_json = json.loads(_raw_data)
            except:
                print("Break in \\n",_raw_data)
                continue
            try:
                for data in _data_in_json["data"]:
                    _price_date = data[0].split("/")
                    _price = data[1]
                    try:
                        _price_date = datetime.datetime(int(_price_date[0])+1911, int(_price_date[1]), int(_price_date[2]))
                    except:
                        continue
                    _price_date_transformed = _price_date.strftime("%Y%m%d")

                    try:
                        bt.insertData("Tw_Stock_Price_Per_Day", "Stock_"+str(_stock),\
                            list(_db_table_formats.keys()), \
                            [_price_date_transformed, _price])
                        print("insert works ", + _price_date_transformed)
                    except:
                        print("Error in sql insert "+ _price_date_transformed + "_" + "Stock_"+str(_stock))
            except:
                print("Error in json loadg, raw_json= ", _data_in_json)
                    
def Transaction_Strategy_BBand(DB, stock_No, yesterday_date, today_price):
    date_range = []
    datetime_yesterday = datetime.datetime.strptime(yesterday_date, "%Y%m%d")

    _command = "select Date, Daily_Price_Mean from Stock_" + str(stock_No)
    _data = bt.selectTableFromDB(DB, "Stock_"+stock_No, _command)
    _data_dict = {}
    _price_array = []

    #to dict
    for data_array in _data:
        if data_array[0] not in _data_dict:
            _data_dict[data_array[0]] = float(data_array[1])
            
    for i in range(20):
        while True:
            datetime_yesterday -= datetime.timedelta(days=1)
            _today = datetime_yesterday.strftime("%Y%m%d")
            if _today in _data_dict:
                _price_array.append(_data_dict[_today])
                break
    _price_std = np.std(_price_array)
    if today_price >= np.mean(_price_array) - 1*_price_std:
        return "Buy"
    elif today_price >= np.mean(_price_array) - 2*_price_std:
        return "Buy_More"

    elif np.mean(_price_array) - float(today_price) >= 0.5:
        return "Sell"
    elif np.mean(_price_array) + 1*_price_std >= today_price:
        return "Sell_Half"
    else:
        return "Hold"

def ratings_reckon(origin_number, last_number, ratings, years):
    #last_number = origin_number * power((1+ ratings/period), period*years)
    if origin_number == -1:
        origin_number = last_number/ math.pow((1+ ratings/1), years)
    if last_number == -1:
        last_number = origin_number * math.pow((1+ ratings/1), years)
    if ratings == -1:
        ratings = ((math.exp(math.log(last_number/origin_number)/(years)))-1) * (1)
            
    return {
        "origin_number": origin_number,
        "last_number" : last_number,
        "ratings" : ratings
    }

def Transaction_Strategy_OverHighestScore(DB, stock_No, yesterday_date, today_price):
    date_range = []
    datetime_yesterday = datetime.datetime.strptime(yesterday_date, "%Y%m%d")

    _command = "select Date, Daily_Price_Mean from Stock_" + str(stock_No)
    _data = bt.selectTableFromDB(DB, "Stock_"+stock_No, _command)
    _data_dict = {}
    _price_array_5weeks = []
    _price_array_24weeks = []


    #to dict
    for data_array in _data:
        if data_array[0] not in _data_dict:
            _data_dict[data_array[0]] = float(data_array[1])
            
    for i in range(7*5):
        datetime_yesterday_tmp = datetime_yesterday
        while True:
            datetime_yesterday_tmp -= datetime.timedelta(days=1)
            _today = datetime_yesterday_tmp.strftime("%Y%m%d")
            if _today in _data_dict:
                _price_array_5weeks.append(_data_dict[_today])
                break

    for i in range(7*24):
        datetime_yesterday_tmp = datetime_yesterday
        while True:
            datetime_yesterday_tmp -= datetime.timedelta(days=1)
            _today = datetime_yesterday_tmp.strftime("%Y%m%d")
            if _today in _data_dict:
                _price_array_24weeks.append(_data_dict[_today])
                break

    _price_std_5weeks = np.std(_price_array_5weeks)

    if today_price >= np.max(_price_array_5weeks):
        return "Buy"
    elif today_price >= np.max(_price_array_24weeks):
        return "Buy_More"

#    elif np.mean(_price_array_24weeks) >= np.max(_price_array_5weeks):
#        return "Sell"

    elif np.mean(_price_array_24weeks) >= np.max(_price_array_5weeks):
        return "Sell_Half"
    else:
        return "Hold"


