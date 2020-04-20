from toolBox import basicTool as bt
from toolBox import webTool as wt
import datetime 
import json
import os
import time
import random

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
    _datetime_now = datetime.datetime.now()
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
                except:
                    print("Error in sql insert "+ _price_date_transformed)
                    
def Transaction_Strategy_BBand(DB, stock_No, yesterday_date):
    date_range = []
    datetime_yesterday = datetime.datetime.strptime(yesterday_date, "%Y%m%d")

    for i in range(20):
        datetime_yesterday -= datetime.timedelta(days=1)
        date_range.append(datetime_yesterday.strftime("%Y%m%d"))

    _command = "select Date, Daily_Price_Mean from Stock_" + str(stock_No)
    return bt.selectTableFromDB(DB, "Stock_"+stock_No, _command)
