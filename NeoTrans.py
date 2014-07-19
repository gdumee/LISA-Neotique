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
# Version   : Date      : Modif
#-----------------------------------------------------------------------------
#           : 19/07/14  : improve error dectection on Trans
#-----------------------------------------------------------------------------
#           :           :
#-----------------------------------------------------------------------------



#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
from random import random 
from subprocess import call
import glob
import gettext


#-----------------------------------------------------------------------------
# NeoTrans
#-----------------------------------------------------------------------------
class NeoTrans():
    """
    Transalation with many possibilities of text :
    ex : (1, 'message 1'), (10, 'message 2')
    'message 1' has 1 chances on 11 to be selected, 'message 2' has 10 chances on 11
    """
    def __init__(self, domain, localedir, fallback, languages, test=""):
        """
        # Intialization with a gettext translation function : : translation = gettext.translation(domain='.................
        """
        if test == "__main__" : print " ---------------------------------------------NeoTrans test mode -------------------------------"
        
        if test == "__main__" : 
            # Generate translation dictionary
            if localedir is not None:
                for x in os.listdir(localedir):
                    if os.path.isfile("{localedir}/{lang}".format(localedir = localedir, lang = x)) == True or os.path.isdir("{localedir}/{lang}/LC_MESSAGES".format(localedir = localedir, lang = x)) == False:
                        continue
                    
                    # Search po files
                    wildcard = "{localedir}/{lang}/LC_MESSAGES/*.po".format(localedir = localedir, lang = x)
                    for y in glob.glob(wildcard):
                        filename_mo = y[:-2] + "mo"
                        filename_po = y
                        
                        # Check if mo file is older
                        if os.path.isfile(filename_mo) == False or os.path.getmtime(filename_po) > os.path.getmtime(filename_mo):
                            # Check if po file has no error
                            self.checkError(filename_po)
                            print "Generating {lang} translations".format(lang = x)
                            call(['msgfmt', '-o', filename_mo, filename_po])
                        


        # Initialize gettext
        self.trans = gettext.translation(domain = domain, localedir = localedir, fallback = fallback, languages = languages).ugettext
    #-----------------------------------------------------------------------------
    #              Publics  Fonctions
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
    def checkError(self,pfile) :
        """
        read po file for syntax errors
        pfile = PO file to check out
        """
        print "Check translation file"
        line = 0
        bMsgstr = False  #are you reading msgstr lines ?
        bError = False #Existing error
        f = open (pfile,"r")
        for line2 in f:
            line +=1
            #delete \t and ' '
            line2 = line2.lstrip()  
            #ignore empty line (after #delete \t and ' ')
            if line2 == '\n' or line2 == '':
                bMsgstr = False
                continue
            #ignore comment file
            if line2[0] == '#' :
                continue
            #no msgid ou msgstr line
            if (line2[:6] <>'msgid ') and (line2[:6] <> 'msgstr') and bMsgstr == False:
                print "    Unknown string on line {0}".format(line)
                continue
            #msgid line
            if line2[:6] == 'msgid ' :
                bMsgstr = False
                if line2.count('"') <> 2 :
                    print "    Error on line {0}".format(line)
                    bError= True
            #msgstr line
            if line2[:6] == 'msgstr' :
                bMsgstr = True
            #check for translations lines
            if bMsgstr == True :
                if line2.count('"') <> 2 : #verif only complexe line
                    if line2.count('"') <> 4 :
                        print '    Missing " on line {0}'.format(line)
                        bError= True
                    if line2.count('(') <> 1 :
                        print '    Missing ( on line {0}'.format(line)
                        bError= True
                    if line2.count(')') <> 1 :
                        print '    Missing ) on line {0}'.format(line)
                        bError= True
                    if line2.count('{') <> line2.count('}') :
                        print '    Missing {1} on line {0}'.format(line,"{ or }")
                        bError= True
                    try :
                        if type(eval(line2[line2.index('"(')+2:line2.index(',')])) <> int :
                            print '    Missing , after number on line {0}'.format(line)
                            bError= True
                    except :
                        print '    Missing de , after number on line {0}'.format(line)
                        bError= True
                    if line2[len(line2)-4:len(line2)-1] <> '),"' :       #len(line2)-1 because \n at EOL
                        print '    Missing )," at the end of line {0}'.format(line)
                        bError= True
        #end for
        
        f.close()
        if bError == True :
            print ('Errors in PO file')
        else :
            print ('No error in PO file')
    
    #-----------------------------------------------------------------------------
    #              Private  Fonctions
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
                return option['msg'].decode('utf-8')
                
            # Try next string
            val -= option['weight']
        
        # In case of error, return input
        print 'Translation randomize error'
        return option

    #----------------------------------------------------------------------------

# --------------------- End of NeotTrans.py  ---------------------
