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
from random import seed
from subprocess import call
import glob
import gettext
from twisted.python import log


#-----------------------------------------------------------------------------
# NeoTrans
#-----------------------------------------------------------------------------
class NeoTrans():
    """
    Transalation with many possibilities of text :
    ex : (1, 'message 1'), (10, 'message 2')
    'message 1' has 1 chances on 11 to be selected, 'message 2' has 10 chances on 11
    """
    def __init__(self, domain, localedir, languages, fallback = True, test = False):
        """
        # Intialization with a gettext translation function : translation = gettext.translation(domain='.................
        """
        # TODO
        test = True

        # Initialize random
        seed()

        # Generate translation dictionary
        if localedir is not None:
            if localedir[-1] == '/':
                localedir = localedir[:-1]

            # Test mode
            key_dict = {}
            if test == True:
                # Create pot, and get translation IDs
                key_dict = self.CreatePot(localedir, domain)

            for x in os.listdir(localedir):
                if os.path.isfile("{localedir}/{lang}".format(localedir = localedir, lang = x)) == True or os.path.isdir("{localedir}/{lang}/LC_MESSAGES".format(localedir = localedir, lang = x)) == False:
                    continue

                # Search po files
                wildcard = "{localedir}/{lang}/LC_MESSAGES/*.po".format(localedir = localedir, lang = x)
                for y in glob.glob(wildcard):
                    filename_mo = y[:-2] + "mo"
                    filename_po = y

                    # Test mode
                    if test == True:
                        # Check if po file has no error
                        if self.checkError(filename_po, key_dict) == True:
                            continue

                    # Check if mo file is older
                    if os.path.isfile(filename_mo) == False or os.path.getmtime(filename_po) > os.path.getmtime(filename_mo):
                        log.msg("Generating {lang} translations".format(lang = x))
                        call(['msgfmt', '-o', filename_mo, filename_po])

        # Initialize gettext
        self.trans = gettext.translation(domain = domain, localedir = localedir, fallback = fallback, languages = languages).ugettext

    #-----------------------------------------------------------------------------
    #              Publics  Fonctions
    #-----------------------------------------------------------------------------
    def Trans(self, translation_key):
        # If empty key
        if translation_key == "":
            return ""

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
    def checkError(self, po_file, key_dict = {}):
        """
        Read po file for syntax errors
        po_file : PO file to check out
        key_dict : Keys to search missing translations
        """
        log.msg("Checking PO file : {}".format(po_file))

        line = 0
        bMsgstr = False
        bError = False

        # open file
        f = open(po_file, "r+")

        # Read lines in file
        for l in f:
            line += 1

            # Delete \t and ' '
            l = l.strip()

            # Empty line and comment
            if l == '\n' or l == '' or l[0] == '#':
                bMsgstr = False
                continue

            # msgid line
            if l.startswith('msgid '):
                bMsgstr = False
                if l.count('"') != 2:
                    log.err("    Error on line {0} : missing \" for msgid".format(line))
                    bError= True

                # Remove key from pot dictionnary
                key = eval(l[len('msgid '):].strip())
                if key_dict.has_key(key):
                    key_dict.pop(key)
            # msgstr line
            elif l.startswith('msgstr '):
                bMsgstr = True
                l = l[len('msgstr '):].strip()
            # No msgid ou msgstr line
            elif bMsgstr == False:
                log.err("    Unknown string on line {0}".format(line))
                continue

            # Check for translations lines
            if bMsgstr == True:
                # Get simple string
                s = ""
                try:
                    s = eval(l)
                    if s == "" and key != "":
                        log.err("    No translation on line {0} for {1}".format(line, key))

                except:
                    log.err("    Invalid string on line {0}".format(line))
                    bError= True
                    continue

                # Try to get translation options
                o = None
                if len(s) > 0 and s[0] == '(':
                    try:
                        o = eval(s)
                    except:
                        log.err("    Invalid string on line {0}".format(line))
                        bError= True
                        continue

                # Check types
                if o is not None:
                    try:
                        if type(o[0][0]) != int:
                            log.err('    Invalid option weight on line {0}'.format(line))
                            bError= True
                        if type(o[0][1]) != str:
                            log.err('    Invalid option string on line {0}'.format(line))
                            bError= True
                    except:
                        log.err('    Invalid translation option on line {0}'.format(line))
                        bError= True

        # Check missing keys
        for k in key_dict:
            f.write("\n")
            f.write("msgid \"{0}\"\n".format(k))
            f.write("msgstr  \"\"\n")
            line += 3
            log.err("    No translation on line {0} for {1}".format(line, k))

        # Close file
        f.close()

        # Result message
        if bError == False:
            log.msg("    No error in PO file")

        return bError

    #-----------------------------------------------------------------------------
    def _get_py_files(self, path):
        py_list = []
        for x in os.listdir(path):
            y = "{path}/{sub}".format(path = path, sub = x)
            if os.path.isdir(y) == True:
                py_list += self._get_py_files(y)
            elif x == "__init__.py":
                continue
            elif x[-3:] == ".py":
                py_list.append(y)
        return py_list

    #-----------------------------------------------------------------------------
    def CreatePot(self, path, domain):
        # Init xgettext params
        pot_file = "{path}/{domain}.pot".format(path = path, domain = domain.lower())
        params = ['xgettext', '-i', '--no-location', '--package-name', domain, '--package-version', '1.0', '--default-domain', domain, '--output', pot_file, '--copyright-holder=Neotique', '--foreign-user']

        # Add py files to parse
        params += self._get_py_files(path[:-5])

        # Create pot file
        call(params)

        # Get IDs dictionnary
        try:
            key_dict = {}
            with open(pot_file, "r") as f:
                for l in f:
                    l = l.strip()
                    if l.startswith("msgid "):
                        key = eval(l[len("msgid "):])
                        if key != "":
                            key_dict[key] = 0
        except:
            pass

        return key_dict

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
        log.err('Translation randomize error')
        return options

# --------------------- End of NeoTrans.py  ---------------------
