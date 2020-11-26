##!/usr/bin/env python
# -*- coding: utf-8 -*-

#---Packages---#
import socket
import threading
import time
from datetime import datetime
from enum import Enum
import signal

#---Library---#
import OandaPyLib as opl
import ArpCSVList as dataMng
import MovingAverage as ma

#---Data Manager---#


class ThreadGrabber():
	def __init__(self, interval, startDelay):
		self.startDelay = startDelay
		self.interval = interval
	
	def taskGetPrice(self):
		timeGetPrice, ask, bid = opl.GetPrices()
		dataMng.setMarketPrice(ask, bid)
		logger = "ThreadTimerGrabber---{}".format(datetime.now().strftime("%Y/%m/%d %H:%M.%S"))
		logger = logger + ',' + str(timeGetPrice) + ',' + str(ask) + ',' + str(bid)
		print(logger)
	
	def taskGetMovingAverage(self):
		

	def task(self, arg, args):
		self.taskGetPrice()
	
	def start(self):
		signal.signal(signal.SIGALRM, self.task)
		signal.setitimer(signal.ITIMER_REAL, self.startDelay, self.interval)

#---END---#