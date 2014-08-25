# -*- coding: UTF-8 -*-
import unittest
import logging
import time
import subprocess

# Le code à tester doit être importable
from NeoConv import NeoConv

#requiered
from lisa.Neotique.NeoTrans import NeoTrans
import inspect
import os, sys
from datetime import datetime, timedelta,time


class TestNeoConv(unittest.TestCase):


    # Cette méthode sera appelée avant chaque test.
    def setUp(self):
        pass

    # Cette méthode sera appelée après chaque test.
    def tearDown(self):
        print('Nettoyage !')

    # Chaque méthode dont le nom commence par 'test_' est un test.
    def test_NoArg(self):
        ret = NeoConv.WITDate()
        date = {'begin': datetime.today().time().strftime("%H:%M"),'end':  datetime.today().time().strftime("%H:%M"),
            'date': datetime.now().date(),'part': 'alltheday', 'delta': 0,
            'day': datetime.today().strftime("%c")[:3],'month': datetime.today().strftime("%B")}
        try :
            assert (ret == date)
        except AssertionError :
            print 'ret :',ret
            print 'date :',date
            raise AssertionError

    def test_jsonNoDatetime(self):
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
        u'msg_body': u'quelle est la m\xe9t\xe9o \xe0 Marseille demain ?',
        u'outcome': {
            u'entities': {
                u'location': {u'body': u'Marseille', u'start': 22, u'end': 31, u'suggested': True, u'value': u'Petaouchnoc'},
            u'confidence': 0.999,
            u'intent': u'meteo_getweather'},
        'type': u'chat'}}
        ret = NeoConv.WITDate(jsonInput)
        date = {'begin': datetime.today().time().strftime("%H:%M"),'end':  datetime.today().time().strftime("%H:%M"),
            'date': datetime.now().date(),'part': 'alltheday', 'delta': 0,
            'day': datetime.today().strftime("%c")[:3],'month': datetime.today().strftime("%B")}
        try :
            assert (ret == date)
        except AssertionError :
            print 'ret :',ret
            print 'date :',date
            raise AssertionError

    def test_Tomorrow(self):
        dfrom = (datetime.today()+timedelta(1)).strftime("%Y-%m-%dT%H:%M:00.00+00")
        dto = (datetime.today()+timedelta(2)).strftime("%Y-%m-%dT%H:%M:00.00+00")
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
        u'msg_body': u'quelle est la m\xe9t\xe9o \xe0 Marseille demain ?',
        u'outcome': {
            u'entities': {
                u'datetime': {u'body': u'xxxxx', u'start': 32, u'end': 38, u'value': {u'to': dto, u'from': dfrom}}},
            u'confidence': 0.999,
            u'intent': u'meteo_getweather'},
        'type': u'chat'}
        ret = NeoConv.WITDate(jsonInput)
        dbegin = time(datetime.now().hour, datetime.now().minute)
        date = {'begin':dbegin,'end':  dbegin,
            'date': datetime.now().date()+timedelta(1),'part': 'alltheday', 'delta': 1,
            'day': (datetime.today()+timedelta(1)).strftime("%c")[:3],'month':(datetime.today()+timedelta(1)).strftime("%B")}
        #cant test
        date['part']=ret['part']
        date['tpart']=ret['tpart']
        date['tday']=ret['tday']
        date['tmonth']=ret['tmonth']

        try :
            assert (ret == date)
        except AssertionError :
            print 'ret :',ret
            print 'date :',date
            raise AssertionError




# Ceci lance le test si on exécute le script
# directement.
if __name__ == '__main__':
    debug = 0
    if debug == 0 :
        unittest.main(verbosity=2)
    else :
    #debug
        pass
