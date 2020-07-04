from toolBox import basicTool as bt
from toolBox import webTool as wt
import funcMain as fm
import numpy as np
import matplotlib.pyplot as plt
from toolBox import basicTool as bt




wt.Scrapy_Proxy_List("./Source/","ProxyList")

Proxy_List = bt.csvtoArray("./Source/ProxyList.csv")
Proxy_in_dict = {}
for _t,ip in enumerate(Proxy_List):
    if ip[0] not in Proxy_in_dict and _t >0:
        Proxy_in_dict[ip[0]] = {"https":ip[0]}

#init
#fm.init_stock_data(["0050"],Proxy_in_dict)
#fm.init_stock_data(["2382"],Proxy_in_dict)
#fm.init_stock_data(["2317"],Proxy_in_dict)
#fm.init_stock_data(["0056"],Proxy_in_dict)
#fm.init_stock_data(["1210"],Proxy_in_dict)
#fm.init_stock_data(["2330"],Proxy_in_dict)
#fm.init_stock_data(["3008"],Proxy_in_dict)
#fm.init_stock_data(["3231"],Proxy_in_dict)
#fm.init_stock_data(["2356"],Proxy_in_dict)
fm.init_stock_data(["1210"],Proxy_in_dict)