#! /usr/bin/env python

#---PACKAGES---#
import time
import sys
import threading
from datetime import datetime
import os
from types import resolve_bases
import requests
import json
import configparser

import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.transactions as trans
import oandapyV20.endpoints.trades as trades

#---Account Info---#
url = os.environ.get('OANDA_API_URL', None)
account_id = os.environ.get('OANDA_API_ACCOUNT_ID', None)
contentType = os.environ.get('OANDA_API_CONTENT_TYPE', None)
authorization = os.environ.get('OANDA_API_AUTHORIZATION', None)
instrument = os.environ.get('OANDA_API_INSTRUMENT', None)

#---APIs---#
api = API(access_token=authorization)
oanda = oandapyV20.API(environment="live",access_token=authorization)

#---NAMES---#
OrderTemplatePathname = './Template/OrderTemplate.json'
TransTemplatePathname = './Template/TransTemplate.json'
TradeTemplatePathname = './Template/TradeTemplate.json'
PriceTemplatePathname = './Template/PriceTemplate.json'
OrderRequestsDirName = "./OrderRequests/"
TransRequestsDirName = "./TransRequests/"
TradeRequestsDirName = "./TradeRequests/"
PriceDirName = "./Prices/"

#---Settings---#
MarginLevelLimit = 48

#---Functions---#
def getFileList(dirName):
	ret = None
	try:
		temp = os.listdir(dirName)
		ret = sorted(temp)
	except Exception as e:
		print(e)
	return ret

def GetMarginLevel():
	ret = 0
	try:
		req = accounts.AccountSummary(accountID=account_id)
		res = api.request(req)
		marginAvailable = float(res["account"]["marginAvailable"])
		marginUsed = float(res["account"]["marginUsed"])
		ret = 50 * marginUsed / marginAvailable
	except Exception as e:
		print(e)
	return ret

def GetPrices():
	params = {"instruments" : instrument}
	try:
		req = pricing.PricingInfo(accountID=account_id, params=params)
		res = api.request(req)
		priceTime = res['prices'][0]['time']
		asksPrice = res['prices'][0]['asks'][0]['price']
		bidsPrice = res['prices'][0]['bids'][0]['price']
	except Exception as e:
		print(e)
	return priceTime, asksPrice, bidsPrice

def GetJsonPrices():
	ask = 0
	bid = 0
	try:
		files = getFileList(PriceDirName)
		flag = True
		if not files:
			flag = False
		if flag == True:
			pathname = PriceDirName + "/" + files[0]
			ask, bid = GetJsonPricesPathname(pathname)
	except Exception as e:
		print(e)
	return ask, bid

def GetJsonPricesPathname(pathname):
	ask = 0
	bid = 0
	try:
		params = readParam(pathname)
		ask = float(params["asks"])
		bid = float(params["bids"])
		os.remove(pathname)	
	except Exception as e:
		print(e)
	return ask, bid

def GetJsonPricesList():
	count = 0
	askList = []
	bidList = []
	try:
		files = getFileList(PriceDirName)
		flag = True
		if not files:
			flag = False
		while flag == True:
			count = count + 1
			pathname = PriceDirName + "/" + files[0]
			ask, bid = GetJsonPricesPathname(pathname)
			askList.append(ask)
			bidList.append(bid)
			files = os.listdir(PriceDirName)
			if not files:
				flag = False
			else:
				flag = True
	except Exception as e:
		print(e)
	return askList, bidList, count

def makeOrder(price, takeProfitPrice, orderType, units):
	pathname = OrderTemplatePathname
	try:
		with open(pathname, "r") as fr:
			params = json.load(fr)
			params["order"]["price"] = str(price)
			params["order"]["takeProfitOnFill"]["price"] = str(takeProfitPrice)
			params["order"]["type"] = orderType
			params["order"]["units"] = units
			return params
	except Exception as e:
		print(e)
	return None

def makeStopLoss(tradeId, stopLossPrice):
	pathname = TradeTemplatePathname
	try:
		with open(pathname, "r") as fr:
			params = json.load(fr)
			params["tradeID"] = tradeId
			params["trades"]["stopLoss"]["price"] = str(stopLossPrice)
			return params
	except Exception as e:
		print(e)

def dumpParam(params, dirName):
	dt = datetime.now().strftime('%Y%m%d%H%M%S%f')
	pathname = dirName + dt + ".json"
	try:
		with open(pathname, "w") as fw:
			json.dump(params, fw)
	except Exception as e:
		print(e)
		return None
	return pathname

def dumpOrderParam(params):
	dirName = OrderRequestsDirName
	return dumpParam(params, dirName)

def dumpPriceParam(params):
	dirName = PriceDirName
	return dumpParam(params, dirName)

def dumpTradeParam(params):
	dirName = TradeRequestsDirName
	return dumpParam(params, dirName)

def readParam(pathname):
	with open(pathname, "r") as fr:
		params = json.load(fr)
	return params

def BuyLimit(price, takeProfitPrice, units):
	params = makeOrder(price, takeProfitPrice, "LIMIT", units)
	ret = False
	if params is not None:
		dumpOrderParam(params)
		ret = True
	return ret

def BuyStop(price, takeProfitPrice, units):
	params = makeOrder(price, takeProfitPrice, "STOP", units)
	ret = False
	if params is not None:
		dumpOrderParam(params)
		ret = True
	return ret

def SellLimit(price, takeProfitPrice, units):
	params = makeOrder(price, takeProfitPrice, "LIMIT", (-1)*units)
	ret = False
	if params is not None:
		dumpOrderParam(params)
		ret = True
	return ret

def SellStop(price, takeProfitPrice, units):
	params = makeOrder(price, takeProfitPrice, "STOP", (-1)*units)
	ret = False
	if params is not None:
		dumpOrderParam(params)
		ret = True
	return ret

def SetStopLoss(tradeId, stopLossPrice):
	params = makeStopLoss(tradeId, stopLossPrice)
	ret = False
	if params is not None:
		dumpTradeParam(params)
		ret = True
	return ret

def requestOrderPathname(pathname):
	params = readParam(pathname)
	res = None
	try:
		req = orders.OrderCreate(accountID=account_id, data=params)
		if req is not None:
			res=api.request(req)
			os.remove(pathname)
		return res
	except Exception as e:
		print(e)
	return res

def requestTradeCRCDOPathname(pathname):
	rParams = readParam(pathname)
	tradeId = rParams["tradeID"]
	params = rParams["trades"]
	res = None
	try:
		req = trades.TradeCRCDO(accountID=account_id, tradeID=tradeId, data=params)
		if req is not None:
			res=api.request(req)
			os.remove(pathname)
		return res
	except Exception as e:
		print(e)
	return res

def RequestOrder():
	flag = True
	try:
		files = getFileList(OrderRequestsDirName)
		if not files:
			flag = False
		if flag == True:
			pathname = OrderRequestsDirName + "/" + files[0]
			requestOrderPathname(pathname)
		return flag
	except Exception as e:
		print(e)
	return flag

def RequestTradeCRCDO():
	flag = True
	try:
		files = getFileList(TradeRequestsDirName)
		if not files:
			flag = False
		if flag == True:
			pathname = TradeRequestsDirName + "/" + files[0]
			requestTradeCRCDOPathname(pathname)
		return flag
	except Exception as e:
		print(e)
	return flag

def DumpPrice(timeGetPrice, asksPrice, bidsPrice):
	pathname = None
	rParams = readParam(PriceTemplatePathname)
	try:
		rParams["instruments"] = str(instrument)
		rParams["time"] = str(timeGetPrice)
		rParams["asks"] = str(asksPrice)
		rParams["bids"] = str(bidsPrice)
		dumpPriceParam(rParams)
	except Exception as e:
		print(e)
	return pathname

def GetOpenTradeList():
	

#---END---#