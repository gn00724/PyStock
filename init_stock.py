from toolBox import basicTool as bt
from toolBox import webTool as wt
import funcMain as fm
import numpy as np
import matplotlib.pyplot as plt

Proxy_List = bt.csvtoArray("./Source/ProxyList.csv")
Proxy_in_dict = {}
for ip in Proxy_List:
    if ip[0] not in Proxy_in_dict:
        Proxy_in_dict[ip[0]] = {"https":ip[0]}

#init
#fm.init_stock_data(["0050"],Proxy_in_dict)
fm.init_stock_data(["2382"],Proxy_in_dict)