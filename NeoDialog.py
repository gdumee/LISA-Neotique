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


#-----------------------------------------------------------------------------
# NeoDialog
#-----------------------------------------------------------------------------
class NeoDialog:
    """
    Dialog manager
    """
    def __init__(self, configuration_lisa):
        self.configuration_lisa = configuration_lisa

    #-----------------------------------------------------------------------------
    def SimpleAnswer(self, plugin, method, message):
        """
        Answer the client with a message
        """
        # Nothing to do, default answer rule will respond
        args = {}
        args['plugin'] = plugin
        args['method'] = method
        args['body'] = message
        args['answer_rule'] = True
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
        args['answer_arg'] = self
        protocol.answerToClient(json.dumps(args))
        
        # Create a Timer for response
        try:
            len(caller.dialog)
        except:
            caller.dialogs = []
            
        # Create timeout timer
        caller.dialogs.append({'caller': caller, 'caller_cbk': caller_cbk, 'caller_param': caller_param})
        caller.dialogs[-1]['timer'] = NeoTimer(duration_s = 10, user_cbk = self._timer_cbk, user_param = caller.dialogs[-1])
        
    #-----------------------------------------------------------------------------
    def _timer_cbk(self, dialog):
        """
        Internal timer callback
        """
        # Callback caller without answer
        dialog['caller_cbk'](dialog['caller_param'], None)
        
        # Remove timer from caller
        dialog['caller'].dialogs.remove(dialog)
        
    def process_answer(self, jsondata):
        print "recéption réponse"

# --------------------- End of NeoDialog.py  ---------------------
