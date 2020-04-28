from toolBox import basicTool as bt
from toolBox import webTool as wt
import funcMain as fm
import numpy as np
import matplotlib.pyplot as plt

G_Search_Stock_Array = ["1210"]

for _stock_no_in_array in G_Search_Stock_Array:
    G_Translation_Fee = 0.14 / 100
    G_Start_Money = 1000000
    G_Stock_Hold = 0
    G_dict_from_pass_start = {}
    G_Plt_X = []
    G_Plt_Y = []
    _command = "select Date, Daily_Price_Mean from Stock_" + str(_stock_no_in_array)
    print(_command)
    _data = bt.selectTableFromDB("Tw_Stock_Price_Per_Day", "Stock_"+str(_stock_no_in_array), _command)

    #sor date
    for _data_obj in _data:
        _date = int(_data_obj[0])
        G_dict_from_pass_start[_date] = _data_obj

    dict_key = G_dict_from_pass_start.keys()
    _key_array_sort = np.sort(list(dict_key))
    G_Last_Price = 0

    #to dict
    for _t, keys in enumerate(_key_array_sort[30:]):
        print(_t/len(_key_array_sort[30:]))
        _data = G_dict_from_pass_start[keys]
        call_bool = fm.Transaction_Strategy_BBand("Tw_Stock_Price_Per_Day", _stock_no_in_array, _data[0], _data[1])
        stock_price = float(_data[1]) * 1000 + float(_data[1]) * G_Translation_Fee
        G_Last_Price = float(_data[1]) * 1000
        if call_bool == "Buy" and G_Start_Money >= stock_price:
            G_Start_Money -= stock_price
            G_Stock_Hold += 1
        elif call_bool == "Sell" and G_Stock_Hold > 0:
            G_Start_Money += stock_price * G_Stock_Hold
            G_Stock_Hold = 0
        elif call_bool == "Sell_Half" and G_Stock_Hold > 0:
            G_Stock_Sell = int(G_Stock_Hold/2)
            G_Stock_Hold -= G_Stock_Sell
            G_Start_Money += stock_price * G_Stock_Sell
        elif call_bool == "Buy_More" and G_Stock_Hold > 0:
            _count_can_buy = G_Start_Money // stock_price
            _buy_descions = 0
            if _count_can_buy >= 3:
                _buy_descions = 3
            elif _count_can_buy == 2:
                _buy_descions = 2
            elif _count_can_buy == 1:
                _buy_descions = 1
            G_Start_Money -= stock_price*_buy_descions
            G_Stock_Hold += _buy_descions
        G_Plt_X.append(str(_data[0]))
        G_Plt_Y.append(int(G_Start_Money+G_Stock_Hold*G_Last_Price))


    plt.plot(G_Plt_X, G_Plt_Y)
    plt.savefig('./Output/'+_stock_no_in_array+".png", dpi=100)

    _stock_results = str(G_Start_Money)+", "+\
                    str(G_Stock_Hold)+", "+\
                    str(int(G_Start_Money+G_Stock_Hold*G_Last_Price))
    _stock_ratings = "R = "+str(fm.ratings_reckon(1000000, int(G_Start_Money+G_Stock_Hold*G_Last_Price), -1, 1, 17))

    bt.txtCreater(_stock_no_in_array, _stock_results, "./Output/")
    bt.txtCreater(_stock_no_in_array+"_ratings", _stock_ratings, "./Output/")

