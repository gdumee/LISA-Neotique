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
import string
from fuzzywuzzy import fuzz
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

    #-----------------------------------------------------------------------------
    @classmethod
    def compareSimilar(cls, str1, str2):
        # Compare strings
        if str1 == str2:
            return True

        # Replace special chars
        str1 = str1.lower()
        str2 = str2.lower()
        for p in string.punctuation:
            str1 = str1.replace(p, ' ')
            str2 = str2.replace(p, ' ')

        # Compare strings
        if str1 == str2:
            return True

        # Remove accents
        accents = {"à": "a", "â": "a", "ä": "a", "é": "e", "è": "e", "ê": "e", "ë": "e", "ï": "i", "ô": "o", "ö": "o", "ü": "u", "ü": "u", "ù": "u"}
        for a, b in accents.iteritems():
            str1 = str1.replace(a.decode('utf-8'), b.decode('utf-8'))
            str2 = str2.replace(a.decode('utf-8'), b.decode('utf-8'))

        # Compare strings
        if str1 == str2:
            return True

        # Split strings into words
        list1 = str1.split()
        list2 = str2.split()

        # Remove articles, pronouns...
        articles = ["le", "la", "les", "de", "du", "des", "ce", "ces", "se", "ses", "sa", "son", "cet", "cette"]
        for a in articles:
            while a in list1:
                list1.remove(a)
            while a in list2:
                list2.remove(a)

        # Compare recombined strings
        str1 = " ".join(list1)
        str2 = " ".join(list2)
        if str1 == str2:
            return True

        # Fuzzy comparaisons
        if fuzz.ratio(str1, str2) > 95:
            return True
        if fuzz.partial_ratio(str1, str2) > 95:
            return True
        if fuzz.token_set_ratio(str1, str2) > 95:
            return True
        if fuzz.token_sort_ratio(str1, str2) > 95:
            return True

        return False

# --------------------- End of NeoConv.py  ---------------------
