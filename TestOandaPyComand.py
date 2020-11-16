#! /usr/bin/env python

#---Packages---#
import urllib.parse as pyurllib
import requests as requests
import sys
import os
import datetime
import json
from collections import OrderedDict
import pprint
import numpy as np

#---My Package---#
import OandaPyLib as opl
from ArpCSVList import ArpCSVList

#---Account Info---#
url = os.environ.get('OANDA_API_URL', None)
account_id = os.environ.get('OANDA_API_ACCOUNT_ID', None)
contentType = os.environ.get('OANDA_API_CONTENT_TYPE', None)
authorization = os.environ.get('OANDA_API_AUTHORIZATION', None)
instrument = os.environ.get('OANDA_API_INSTRUMENT', None)

#---Manager---#
dataMng = ArpCSVList()


#---Start Script---#


opl.BuyStop(105.000, 106.010, 1)
opl.BuyLimit(101.500, 108.000, 1)

#opl.SellLimit(110.500, 109.000, 1)
#opl.SellStop(101.000, 100.000, 1)

"""
timeGetPrice, ask, bid = opl.GetPrices()
print(ask)
print(bid)
dataMng.setMarketPrice(ask, bid)
"""

opl.SetStopLoss(213, 100.000)
opl.SetStopLoss(211, 100.000)

#---End---#