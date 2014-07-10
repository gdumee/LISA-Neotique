# -*- coding: UTF-8 -*-
#-----------------------------------------------------------------------------
# project     : Lisa server
# module      : Neotique
# file        : NeoTrans.py
# description : Translation usefull fonction
# author      : G.Audet, G.Dumee
#-----------------------------------------------------------------------------
# copyright   : Neotique
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
from random import random 
from subprocess import call
import glob


#-----------------------------------------------------------------------------
# NeoTrans
#-----------------------------------------------------------------------------
class NeoTrans():
    """
    Transalation with many possibilities of text :
    ex : (1, 'message 1'), (10, 'message 2')
    'message 1' has 1 chances on 11 to be selected, 'message 2' has 10 chances on 11
    """
    def __init__(self, trans, path = None):
        """
        # Intialization with a gettext translation function : : translation = gettext.translation(domain='.................
        """
        self.trans = trans

        # Generate translation dictionary
        if path is not None:
            for x in os.listdir(path):
                if os.path.isfile("{0}/{1}".format(path, x)) == True or os.path.isdir("{0}/{1}/LC_MESSAGES".format(path, x)) == False:
                    continue
                
                # Search po files
                wildcard = "{path}/{lang}/LC_MESSAGES/*.po".format(path = path, lang = x)
                for y in glob.glob(wildcard):
                    filename_mo = y[:-2] + "mo"
                    filename_po = y
                    
                    # Check if mo file is older
                    if os.path.isfile(filename_mo) == False or os.path.getmtime(filename_po) > os.path.getmtime(filename_mo):
                        print "Generating {lang} translations".format(lang = x)
                        call(['msgfmt', '-o', filename_mo, filename_po])

    #-----------------------------------------------------------------------------
    def Trans(self, translation_key):
        # Get translation
        msg = self.trans(translation_key)
        
        # Is this an option list for randomized translation ?
        try:
            options = eval(msg)
            if type(options) is tuple:
                # Randomize translation
                return self._do_random(options)
        except:
            pass
        
        # In others cases return translated string
        return msg
        
        
    #-----------------------------------------------------------------------------
    def _do_random(self, options):
        """
        Return a random option from a list
        """
        # Create list and get total percent
        option_list = []
        total_weight = 0
        for weight, msg in options:
            option_list.append({'weight': weight, 'msg': msg}) 
            total_weight += weight
        
        # Get a random string
        val = int(random() * total_weight)
        for option in option_list:
            # If msg weight is good
            if val < option['weight']:
                return option['msg']
                
            # Try next string
            val -= option['weight']
        
        # In case of error, return input
        print 'Translation randomize error'
        return data

# --------------------- End of NeotTrans.py  ---------------------
