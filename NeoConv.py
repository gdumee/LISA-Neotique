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


#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from datetime import datetime


#-----------------------------------------------------------------------------
# NeoConv
#-----------------------------------------------------------------------------
class NeoConv():

    def __init__(self,var):
        self.Verbose = 0 #print for debug
        self._= var   #= translation fonction.................
        
    #-----------------------------------------------------------------------------   
    def WITDate(self, pjson):
        """
        convert WIT date into dic with day, begin time, end time, part of the day (morning, lunch, evening)
        """
        #init
        #exemple  dDate = {'end': '19:00', 'begin': '12:00', 'date': '2014-06-14', 'part': 'afternoon', 'delta': 1}
        dDate = {'date': datetime.now().date(), 
        'delta': 0, 
        'part': 'alltheday', 
        'begin': datetime.now().time().strftime("%H:%M"), 
        'end': datetime.now().time().strftime("%H:%M")}
        
      
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
        
        #part of day
        if depart.time().hour == 04 and fin.time().hour == 12:
            dDate['part']="morning"
        elif depart.time().hour == 12 and fin.time().hour == 13:
            dDate['part']="midday"
        elif depart.time().hour == 12 and fin.time().hour ==19:
            dDate['part']="afternoon"
        elif depart.time().hour == 18 and fin.time().hour == 0:
            dDate['part']="evening"
        elif depart.time().hour == 0 and fin.time().hour == 0:
            dDate['part']="alltheday"
        else :
            dDate['part']="alltheday"
    
        if  self.Verbose == True : print "dDate           =", dDate
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
        if self.Verbose == True : print 'time2str : pTime, type(pTime)       ',pTime, type(pTime)
        
        if type(pTime) == str :
            try :
                pTime = datetime.strptime(pTime, '%H:%M:%S')
            except :
                pTime = datetime.strptime(pTime, '%H:%M') 
            
        h = pTime.strftime("%H")
        if h[0:1]== "0":
            h=h[1:2]
        msg = h + self._('hour')
        m = pTime.strftime("%M")
        if m =="00":
            m=""
        elif m[0:1]== "0":
            m=m[1:2]
        msg += m
        if pMinutes==1 :
            msg += self._('minute')
            if pSecond == 1 :
                s = pTime.strftime("%S")
                msg += self._('and') + s + self._('second')
                
        return msg

#-----------------------------------------------------------------------------
# End of NeoConv
#-----------------------------------------------------------------------------



