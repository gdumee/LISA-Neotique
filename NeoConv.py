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


#TODO list
#prendre en compte le decalage horaire
#add translated day and month in return
#add its own dico translation for day and month


#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from datetime import datetime


#-----------------------------------------------------------------------------
# NeoConv
#-----------------------------------------------------------------------------
class NeoConv():

    def __init__(self,var,test=""):
        self.verbose = 0 #print for debug
        self._= var   #= translation fonction.................
        self.test = test
        if self.test == "__main__" : print " ---------------------------------------------NeoConvtest mode -------------------------------"

    #-----------------------------------------------------------------------------
    def WITDate(self, pjson):
        """
        convert WIT date into dic with date, begin time, end time, part of the day (morning, lunch, evening)
        date, begin time, end time are all datetime objet
        delta is integer
        part is string
        """
        if self.test ==  "__main__" : print 'start WITDate'
        #init
        #exemple  dDate = {'end': datetime.time(20,50), 'begin': datetime.time(12,00), 'date': datetime.date(2014, 7, 18), 'part': 'afternoon', 'delta': 1, 'day' : 'Mon', 'Month':'July'}
        dDate = {'date': datetime.now().date(),
            'delta': 0,
            'part': 'alltheday',
            'begin': datetime.today().time().strftime("%H:%M"),
            'end': datetime.today().time().strftime("%H:%M"),
            'month':datetime.today().strftime("%B"),
            'day' : datetime.today().strftime("%c")[:3],
        }


        if pjson['outcome']['entities'].has_key('datetime') == False:
            return dDate
        #else
        #from
        depart = pjson['outcome']['entities']['datetime']['value']['from']
        depart = depart[:depart.index('+')] #supprssion decalage horaire
        depart = datetime.strptime(depart, '%Y-%m-%dT%H:%M:%S.%f')
        dDate['date'] = depart.date()
        dDate['begin'] = depart.time()
        #to
        fin = pjson['outcome']['entities']['datetime']['value']['to']
        fin = fin[:fin.index('+')] #supprssion decalage horaire
        fin = datetime.strptime(fin, '%Y-%m-%dT%H:%M:%S.%f')
        dDate['end'] = fin.time()
        #delta days
        delta = dDate['date']- datetime.now().date()
        dDate['delta'] = delta.days
        #month
        month = pjson['outcome']['entities']['datetime']['value']['from']
        month = month[:month.index('+')] #supprssion decalage horaire
        month = datetime.strptime(month, '%Y-%m-%dT%H:%M:%S.%f')
        dDate['month'] = month.date().strftime("%B")
        #day
        day = pjson['outcome']['entities']['datetime']['value']['from']
        day = day[:day.index('+')] #supprssion decalage horaire
        day = datetime.strptime(day, '%Y-%m-%dT%H:%M:%S.%f')
        dDate['day'] = day.date().strftime("%c")[:3]

        #part of day
        if depart.time().hour == 18 and fin.time().hour == 00: #speclial case evening for WIT
            dDate['part'] = "evening"
        elif depart.time().hour >= 04 and fin.time().hour <= 12:
            dDate['part'] = "morning"
        elif depart.time().hour >= 12 and fin.time().hour <= 13:
            dDate['part'] = "midday"
        elif depart.time().hour >= 12 and fin.time().hour <=19:
            dDate['part'] = "afternoon"
        elif depart.time().hour >= 18 and fin.time().hour <= 24:
            dDate['part'] = "evening"
        elif depart.time().hour == 0 and fin.time().hour == 0:
            dDate['part'] = "alltheday"
        else :
            dDate['part'] = "alltheday"

        if  self.test == True : print "WITDate           =", dDate
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
        if self.test ==  "__main__": print 'start time2str'
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

    #-----------------------------------------------------------------------------
    def compareSimilar(self, str1, str2):
        # TODO comparaison plus précise : pas d'accents, pluriels, pas d'articles...
        return str1.lower() == str2.lower()

# --------------------- End of NeoConv.py  ---------------------
