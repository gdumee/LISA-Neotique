# -*- coding: UTF-8 -*-
#-----------------------------------------------------------------------------
# project     : Lisa plugins
# module      : NeoConv
# file        : NeoConv.py
# description : usefull conversion fonctions
# author      : Neotique team
#-----------------------------------------------------------------------------
# copyright   : Neotique
#-----------------------------------------------------------------------------


#TODO
#prendre en compte le decalge hoarire
#add transaled day,and translated month pour return
#add its own dico translation pour day and month


#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from datetime import datetime


#-----------------------------------------------------------------------------
# NeoConv
#-----------------------------------------------------------------------------
class NeoConv():

    def __init__(self,var):
        self.verbose = 0 #print for debug
        self._= var   #= translation fonction.................

    #-----------------------------------------------------------------------------   
    def WITDate(self, pjson=""):
        """
        convert WITdate into dic 
        -with date, begin time, end time, part of the day (morning, lunch, evening), day, month, translate day, translate month, translate part of the day, delta days between current day and WIT day
        -date, begin, end are all datetime objet
        -delta is integer
        -(t)part,(t)day,(t)month are string
        
        jsonINPUT = json from WIT
        if no entities datetime inside ou no jsonINPUT return actual date 
        
        exemple :
        return = {'end': datetime.time(20,50), 
            'begin': datetime.time(12,00), 
            'date': datetime.date(2014, 7, 18), 
            'part': 'afternoon', 
            'tpart': 'après midi', 
            'delta': 1, 
            'day' : 'Mon', 
            'tday' : 'Lundi', 
            'month':'July',
            'tmonth':'Juillet'}
        """
        #init
        dDate = {'date': datetime.now().date(), 
            'delta': 0, 
            'part': 'alltheday', 
            'begin': datetime.today().time().strftime("%H:%M"), 
            'end': datetime.today().time().strftime("%H:%M"),
            'month':datetime.today().strftime("%B"),
            'day' : datetime.today().strftime("%c")[:3],
        }
        
        if ('outcome' not in pjson)  or ('datetime' not in pjson['outcome']['entities']) : #in case of no json or in case of json whitout datetime
            return dDate
        #else
        dfrom = pjson['outcome']['entities']['datetime']['value']['from']
        dfrom = dfrom[:dfrom.index('+')] #supprssion decalage horaire
        dfrom = datetime.strptime(dfrom, '%Y-%m-%dT%H:%M:%S.%f')
        dDate['begin'] = dfrom.time()
        dDate['date'] = dfrom.date()
        delta = dDate['date']- datetime.now().date()
        dDate['delta'] = delta.days
        dDate['month'] = dfrom.date().strftime("%B")
        dDate['tmonth'] =self._(dDate['month'])
        dDate['day'] = dfrom.date().strftime("%c")[:3]
        dDate['tday'] =self._(dDate['day'])
        
        dto = pjson['outcome']['entities']['datetime']['value']['to']
        dto = dto[:dto.index('+')] #supprssion decalage horaire
        dto = datetime.strptime(dto, '%Y-%m-%dT%H:%M:%S.%f')   
        dDate['end'] = dto.time()

        
        #part of day
        if dfrom.time().hour == 18 and dto.time().hour == 00: #speclial case evening for WIT
            dDate['part'] = "evening"
        elif dfrom.time().hour >= 04 and dto.time().hour <= 12:
            dDate['part'] = "morning"
        elif dfrom.time().hour >= 12 and dto.time().hour <= 13:
            dDate['part'] = "midday"
        elif dfrom.time().hour >= 12 and dto.time().hour <=19:
            dDate['part'] = "afternoon"
        elif dfrom.time().hour >= 18 and dto.time().hour <= 24:
            dDate['part'] = "evening"
        elif dfrom.time().hour == 0 and dto.time().hour == 0:
            dDate['part'] = "alltheday"
        else :
            dDate['part'] = "alltheday"
        dDate['tpart'] =self._(dDate['part'])
        
        return dDate

    #-----------------------------------------------------------------------------
    def time2str(self,pTime,pMinutes=1,pSecondes=0):
        """
        Convert a time to string "[x hours] [y minutes] [z seconds]"
        pTime 20:30:17, should be a string or time obj
        pTime mini requierment hour:minute    seconds are optionnal
        pMinutes = optionnal, if 1 returns '20 heures 30 minutes' else returns '20 heures 30'
        pSecondes = optionnal, if 1 (and pMinutes=1) returns '20 heures 30 minutes and 17 secondes ' else returns '20 heures 30 minutes'
        """
        if self.verbose  == 1 : print  'input     :',pTime, type(pTime)
        
        if type(pTime) == str:  #convert str to datetime objet
            try:
                pTime = datetime.strptime(pTime, '%H:%M:%S')
                pTime= pTime.time()
            except:
                pTime = datetime.strptime(pTime, '%H:%M') 
                pTime = pTime.time()
        
        h = pTime.strftime("%H")
        if h[0:1] == "0":
            h=h[1:2]
        msg = h + self._('hour') + ' '
        m = pTime.strftime("%M")
        if m == "00":
            m = ""
        elif m[0:1] == "0":
            m = m[1:2]
        msg += str(m)
        if pMinutes == 1:
            msg += self._('minute')
            if pSecond == 1:
                s = pTime.strftime("%S")
                msg += self._('and') + s + self._('second')

        if self.verbose  == 1 : print 'time2str output    :',msg
        return msg

# --------------------- End of NeoConv.py  ---------------------
