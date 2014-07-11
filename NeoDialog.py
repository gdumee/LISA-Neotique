# -*- coding: UTF-8 -*-
#-----------------------------------------------------------------------------
# project     : Lisa server
# module      : Neotique
# file        : NeoDialog.py
# description : Manage dialog with clients in a plugin
# author      : G.Dumee, G.Audet
#-----------------------------------------------------------------------------
# copyright   : Neotique
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import json
from NeoTimer import NeoTimer
import uuid


#-----------------------------------------------------------------------------
# NeoDialog
#-----------------------------------------------------------------------------
class NeoDialog:
    """
    Dialog manager
    """
    # Dialogs
    _Dialogs = {}    
    
    #-----------------------------------------------------------------------------
    def __init__(self, configuration_lisa):
        self.configuration_lisa = configuration_lisa

    #-----------------------------------------------------------------------------
    def SimpleAnswer(self, plugin, method, message, protocol):
        """
        Answer the client with a message
        """
        # Send question to the client
        print "Notify ", message
        self.SimpleNotify(plugin = plugin, method = method, message = message, protocol = protocol)
        
        # No rule answer after plugin end
        args = {}
        args['plugin'] = plugin
        args['method'] = method
        args['body'] = ""
        args['answer_rule'] = False
        return args

    #-----------------------------------------------------------------------------
    def AnswerWithQuestion(self, plugin, method, message, protocol, caller, caller_cbk, caller_param):
        """
        Answer to client with a new question, and wait for an answer from the client
        """
        # Send question to the client
        self.NotifyWithQuestion(plugin = plugin, method = method, message = message, protocol = protocol, caller = caller, caller_cbk = caller_cbk, caller_param = caller_param)
        
        # No rule answer after plugin end
        args = {}
        args['plugin'] = plugin
        args['method'] = method
        args['body'] = ""
        args['answer_rule'] = False
        return args

    #-----------------------------------------------------------------------------
    def SimpleNotify(self, plugin, method, message, protocol):
        """
        Notify user in a zone with a TTS message
        pMessage = message text to send
        pClients_zone = Target zone : "cuisine", "chambre", "all"... 
        """
        # Send data to calling client
        args = {}
        args['plugin'] = plugin
        args['method'] = method
        args['body'] = message
        args['clients_zone'] = ["sender"]
        args['from'] = "server"
        protocol.answerToClient(json.dumps(args))

    #-----------------------------------------------------------------------------
    def NotifyWithQuestion(self, plugin, method, message, protocol, caller, caller_cbk, caller_param):
        """
        Notify user in a zone with a TTS message
        pMessage = message text to send
        pClients_zone = Target zone : "cuisine", "chambre", "all"... 
        """
        # Create a unique dialog
        uid = str(uuid.uuid1())
        self._Dialogs[uid] = {'caller': caller, 'caller_cbk': caller_cbk, 'caller_param': caller_param}

        # Create timeout timer
        self._Dialogs[uid]['timer'] = NeoTimer(duration_s = 10, user_cbk = self._timer_cbk, user_param = uid)

        # Send data to calling client
        args = {}
        args['type'] = "command"
        args['command'] = "ASK"
        args['plugin'] = plugin
        args['method'] = method
        args['body'] = message
        args['clients_zone'] = ["all"]  # TODO
        args['from'] = "server"
        args['need_answer'] = True
        args['answer_arg'] = uid
        protocol.answerToClient(json.dumps(args))
        
    #-----------------------------------------------------------------------------
    def _timer_cbk(self, uid):
        """
        Internal timer callback
        """
        # Search dialog
        if self._Dialogs.has_key(uid) == False:
            return

        # Callback caller without answer
        self._Dialogs[uid]['caller_cbk'](self._Dialogs[uid]['caller_param'], None)
        
        # Remove dialog
        self._Dialogs.pop(uid, None)
        
    #-----------------------------------------------------------------------------
    def process_answer(self, jsondata):
        # Search dialog
        if jsondata.has_key('outcome') == False or jsondata['outcome'].has_key('answer_arg') == False:
            return
        uid = jsondata['outcome']['answer_arg']
        if self._Dialogs.has_key(uid) == False:
            return
        
        # Callback caller without answer
        caller_cbk = self._Dialogs[uid]['caller_cbk']
        caller_param = self._Dialogs[uid]['caller_param']

        # Remove dialog
        self._Dialogs.pop(uid, None)

        # Callback caller without answer
        caller_cbk(caller_param, jsondata)
    process_answer = classmethod(process_answer)

# --------------------- End of NeoDialog.py  ---------------------
