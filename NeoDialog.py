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
import json, uuid, threading, os, inspect
from datetime import datetime
from pymongo import MongoClient
from twisted.python.reflect import namedAny
from twisted.python import log
from wit import Wit
from lisa.Neotique.NeoTimer import NeoTimer
from lisa.Neotique.NeoTrans import NeoTrans
from lisa.server.ConfigManager import ConfigManagerSingleton

from sys import getrefcount
# Initialize translation
path = os.path.dirname(os.path.abspath(__file__)) + "/lang"
_ = NeoTrans(domain = 'neotique', localedir = path, fallback = True, languages = [ConfigManagerSingleton.get().getConfiguration()['lang']]).Trans


#-----------------------------------------------------------------------------
# NeoContext
#-----------------------------------------------------------------------------
class NeoContext():
    __lock = threading.RLock()
    __global_ctx = {}
    __history = {}
    __steps = {'count': 0, 'first': None, 'last': None}
    __plugins = {}
    configuration_server = ConfigManagerSingleton.get().getConfiguration()

    #-----------------------------------------------------------------------------
    def __init__(self, factory, client_uid):
        self.factory = factory
        self.wait_step = None
        self.client = factory.clients[client_uid]
        self._client_steps = {'count': 0, 'first': None, 'last': None}

    #-----------------------------------------------------------------------------
    def clean(self):
        # Lock access
        NeoContext.__lock.acquire()

        # Clean client vars
        self._client_steps = None
        self.client = None
        self.factory = None
        if hasattr(self, 'Vars') == True:
            for v in self.Vars:
                self.Vars[v] = None

        # Clean global vars
        NeoContext.__steps = None
        for v in NeoContext.__plugins:
            NeoContext.__plugins[v] = None
        for v in NeoContext.__history:
            NeoContext.__history[v] = None
        if NeoContext.__global_ctx.has_key('Vars') == True:
            for v in NeoContext.__global_ctx['Vars']:
                for t in NeoContext.__global_ctx['Vars'][v]:
                    #NeoContext.__global_ctx['Vars'][v][t]['timer'].stop()
                    # TODO cancel timers
                    print "Count : {}".format(getrefcount(NeoContext.__global_ctx['Vars'][v][t]['timer']))
                    NeoContext.__global_ctx['Vars'][v][t]['timer'] = None

                del NeoContext.__global_ctx['Vars']
                NeoContext.__global_ctx['Vars'] = None
        for v in NeoContext.__global_ctx:
            NeoContext.__global_ctx[v] = None

        # Release access
        NeoContext.__lock.release()

    #-----------------------------------------------------------------------------
    def parse(self, jsonInput, module_name = None, function_name = None):
        # If waiting an answer
        if self._process_answer(jsonInput) == True:
            # The answer was processed
            return

        # In no plugin is associated to the intent
        if module_name is None or function_name is None:
            # Add an error step
            step = self._create_step()
            step['type'] = "Error no plugin"
            step['in_json'] = jsonInput

            # Return an error to client
            jsonData = {'type': 'Error', 'message': _("no_plugin")}
            self.factory.sendToClients(client_uids = [self.client['uid']], jsonData = jsonData)
            return

        # Check Wit confidence
        if jsonInput['outcome'].has_key('confidence') == False or jsonInput['outcome']['confidence'] < NeoContext.configuration_server['wit_confidence']:
            # Add an error step
            step = self._create_step()
            step['type'] = "error confidence"
            step['in_json'] = jsonInput

            # Return an error to client
            jsonData = {'type': 'Error', 'message': _("Confidence too low")}
            self.factory.sendToClients(client_uids = [self.client['uid']], jsonData = jsonData)
            return

        # Get initialized plugin
        plugin = None
        plugin_uid = None
        for p in NeoContext.__plugins:
            if NeoContext.__plugins[p]['module_name'] == module_name:
                # Get plugin
                plugin = NeoContext.__plugins[p]
                plugin_uid = p
                break

        # if not found
        if plugin is None:
            # Create the plugin
            try:
                # Initialize plugin
                plugin_uid = str(uuid.uuid1())
                plugin = {'uid': plugin_uid}
                plugin['module_name'] = module_name
                plugin['instance'] = namedAny(module_name)()
                if hasattr(plugin['instance'], 'uid') == True:
                    plugin['instance'].uid = plugin_uid
                plugin['steps'] = {'count': 0, 'first': None, 'last': None}
                NeoContext.__plugins[plugin_uid] = plugin

            except:
                # Add an error step
                step = self._create_step()
                step['type'] = "error create plugin"
                step['module_name'] = module_name
                step['in_json'] = jsonInput

                # Return an error to client
                jsonData = {'type': 'Error', 'message': _("Error initializing plugin")}
                self.factory.sendToClients(client_uids = [self.client['uid']], jsonData = jsonData)

                return

        # Get method to call
        methodToCall = None
        try:
            methodToCall = getattr(plugin['instance'], function_name)
        except:
            # Add an error step
            step = self._create_step()
            step['type'] = "error plugin method"
            step['module_name'] = module_name
            step['function_name'] = function_name
            step['in_json'] = jsonInput

            # Return an error to client
            jsonData = {'type': 'Error', 'message': _("Error plugin doesn't have this function")}
            self.factory.sendToClients(client_uids = [self.client['uid']], jsonData = jsonData)

            return

        # Save step in context
        step = self._create_step(plugin_uid = plugin_uid)
        step['type'] = "Plugin call"
        step['in_json'] = jsonInput.copy()

        # Call plugin method
        jsonInput['context'] = self
        jsonOutput = methodToCall(jsonInput)

        # Old Lisa plugin output
        if jsonOutput is not None:
            self.speakToClient(plugin_uid = plugin_uid, text = jsonOutput['body'])

    #-----------------------------------------------------------------------------
    def speakToClient(self, plugin_uid, text, client_uids = None, zone_uids = None):
        """
        Speak to the client

        plugin_uid : uid of the plugin calling the API
        text : speech for user
        context : current dialog context, can be None for global notification to user (associated with no context)
        client_uids : optional list of destination clients, use clients uids
        zone_uids : optional list of destination zones, use zone uids

        To answer a client, do net set client_uids and zone_uids
        To send to everyone : client_uids = ['all'] or zone_uids = ['all']
        """
        # Check params
        if client_uids is None:
            client_uids = []
        if zone_uids is None:
            zone_uids = []

        # If no destination
        if len(client_uids) == 0 and len(zone_uids) == 0:
            client_uids.append(self.client['uid'])

        # Add a step
        step = self._create_step(plugin_uid = plugin_uid)
        step['type'] = "Plugin speech"
        step['message'] = text

        # Send to client
        jsonData = {}
        jsonData['type'] = 'chat'
        jsonData['message'] = text
        self.factory.sendToClients(client_uids = client_uids, zone_uids = zone_uids, jsonData = jsonData)

    #-----------------------------------------------------------------------------
    def askClient(self, plugin_uid, text, answer_cbk, wit_context = None, client_uids = None, zone_uids = None):
        """
        Ask a question, and wait for an answer

        plugin_uid : uid of the plugin calling the API
        text : question for user
        client_uids : optional list of destination clients, use clients uids
        zone_uids : optional list of destination zones, use zone uids
        answer_cbk : function called on answer

        To answer a client, do net set client_uids and zone_uids
        To send to everyone : client_uids = ['all'] or zone_uids = ['all']

        The callback prototype is : def answer_cbk(self, context, jsonAnswer)
            context : identical to context given here
            jsonAnswer : json received from the client (!!may have no intent!!), None when no answer is received after a timeout
        """
        # Check params
        if client_uids is None:
            client_uids = []
        if zone_uids is None:
            zone_uids = []

        # Lock access
        NeoContext.__lock.acquire()

        # If there is a current wait, end it without answer
        self._process_answer()

        # If no destination
        if len(client_uids) == 0 and len(zone_uids) == 0:
            client_uids.append(self.client['uid'])

        # Add a step
        step = self._create_step(plugin_uid = plugin_uid)
        step['type'] = "Plugin question"
        step['message'] = text
        step['clients'] = client_uids
        step['zones'] = zone_uids
        if wit_context is not None:
            step['wit_context'] = wit_context

        # Set waiting state
        step['answer_cbk'] = answer_cbk
        step['wait_timer'] = NeoTimer(duration_s = 20, user_cbk = self._timer_cbk, user_param = 0)
        self.wait_step = step

        # Release access
        NeoContext.__lock.release()

        # Send to client
        jsonData = {}
        jsonData['type'] = 'command'
        jsonData['command'] = 'ask'
        jsonData['message'] = text
        if wit_context is not None:
            jsonData['wit_context'] = wit_context
        self.factory.sendToClients(client_uids = client_uids, zone_uids = zone_uids, jsonData = jsonData)

    #-----------------------------------------------------------------------------
    def globalSpeakToClient(self, text, client_uids = None, zone_uids = None):
        """

        """
        TODO

    #-----------------------------------------------------------------------------
    def globalAskToClient(self, text, answer_cbk, client_uids = None, zone_uids = None):
        """

        """
        TODO

    #-----------------------------------------------------------------------------
    def _timer_cbk(self, param):
        """
        Internal timer callback
        """
        # No answer timeout
        self._process_answer()

    #-----------------------------------------------------------------------------
    def _process_answer(self, jsonAnswer = None):
        # Lock access
        NeoContext.__lock.acquire()

        # Answer may arrive simultaneously
        if self.wait_step is None:
            # Release access
            NeoContext.__lock.release()
            return False

        # Keep step locally
        step = self.wait_step
        self.wait_step = None

        # Stop timer
        step['wait_timer'].stop()
        step.pop('wait_timer')

        # Add a step
        new_step = self._create_step(plugin_uid = step['plugin_uid'])
        new_step['type'] = "Answer"
        new_step['question_step'] = step['uid']
        step['answer_step'] = new_step

        # Release access
        NeoContext.__lock.release()

        # If there is an answer
        if jsonAnswer is not None:
            new_step['json'] = jsonAnswer.copy()
            jsonAnswer['context'] = self

        # Callback caller without answer
        if jsonAnswer is not None:
            jsonAnswer['context'] = self
        step['answer_cbk'](context = self, jsonAnswer = jsonAnswer)

        # Clear step
        step.pop('answer_cbk')

        # Change client mode
        jsonData = {}
        jsonData['type'] = 'command'
        jsonData['command'] = 'kws'
        self.factory.sendToClients(client_uids = step['clients'], zone_uids = step['zones'], jsonData = jsonData)
        return True

    #-----------------------------------------------------------------------------
    def log(self):
        # Lock access
        NeoContext.__lock.acquire()

        uid = NeoContext.__steps['first']
        while uid is not None:
            print NeoContext.__history[uid]
            uid = NeoContext.__history[uid]['next']

        # Release access
        NeoContext.__lock.release()

    #-----------------------------------------------------------------------------
    def _create_step(self, plugin_uid = None):
        # Lock access
        NeoContext.__lock.acquire()

        # Create a step
        step_uid = str(uuid.uuid1())
        step = {'uid': step_uid, 'date': datetime.now(), 'previous': None, 'next': None, 'client_uid': self.client['uid'], 'client_previous': None, 'client_next': None, 'plugin_uid': plugin_uid, 'plugin_previous': None, 'plugin_next': None}
        NeoContext.__history[step_uid] = step

        # First step
        NeoContext.__steps['count'] += 1
        if NeoContext.__steps['first'] is None:
            NeoContext.__steps['first'] = step_uid

        # Link to last step
        if NeoContext.__steps['last'] is not None:
            NeoContext.__history[NeoContext.__steps['last']]['next'] = step_uid
            step['previous'] = NeoContext.__history[NeoContext.__steps['last']]['uid']
        NeoContext.__steps['last'] = step_uid

        # First client step
        self._client_steps['count'] += 1
        if self._client_steps['first'] is None:
            self._client_steps['first'] = step_uid

        # Link to client last step
        if self._client_steps['last'] is not None:
            NeoContext.__history[self._client_steps['last']]['client_next'] = step_uid
            step['client_previous'] = NeoContext.__history[self._client_steps['last']]['uid']
        self._client_steps['last'] = step_uid

        # link to a plugin
        if plugin_uid is not None:
            # First plugin step
            NeoContext.__plugins[plugin_uid]['steps']['count'] += 1
            if NeoContext.__plugins[plugin_uid]['steps']['first'] is None:
                NeoContext.__plugins[plugin_uid]['steps']['first'] = step_uid

            # Link to plugin last step
            if NeoContext.__plugins[plugin_uid]['steps']['last'] is not None:
                NeoContext.__history[NeoContext.__plugins[plugin_uid]['steps']['last']]['plugin_next'] = step_uid
                step['plugin_previous'] = NeoContext.__history[NeoContext.__plugins[plugin_uid]['steps']['last']]['uid']
            NeoContext.__plugins[plugin_uid]['steps']['last'] = step_uid

        # Release access
        NeoContext.__lock.release()

        return step

    #-----------------------------------------------------------------------------
    def createClientVar(self, name, default = None):
        # Create Vars if needed
        if hasattr(self, 'Vars') == False:
            self.Vars = {}

        # If var doesn't exists
        if self.Vars.has_key(name) == False:
            # Add client variable
            self.Vars[name] = default

        # If property doesn't exist
        if hasattr(self.__class__, name) == False:
            # Create local fget and fset functions
            fget = lambda self: self._get_client_var(name)
            fset = lambda self, value: self._set_client_var(name, value)

            # Add property to self
            setattr(self.__class__, name, property(fget, fset))

    #-----------------------------------------------------------------------------
    def createGlobalVar(self, name, default = None):
        # Create Vars if needed
        if hasattr(NeoContext, 'Vars') == False:
            NeoContext.Vars = {}

        # If var doesn't exists
        if NeoContext.Vars.has_key(name) == False:
            # Add client variable
            NeoContext.Vars[name] = default

        # If property doesn't exist
        if hasattr(self.__class__, name) == False:
            # Create local fget and fset functions
            fget = lambda self: self._get_global_var(name)
            fset = lambda self, value: self._set_global_var(name, value)

            # Add property to self
            setattr(self.__class__, name, property(fget, fset))

    #-----------------------------------------------------------------------------
    def _set_client_var(self, name, value):
        self.Vars[name] = value

    #-----------------------------------------------------------------------------
    def _get_client_var(self, name):
        return self.Vars[name]

    #-----------------------------------------------------------------------------
    def _set_global_var(self, name, value):
        NeoContext.Vars[name] = value

    #-----------------------------------------------------------------------------
    def _get_global_var(self, name):
        return NeoContext.Vars[name]


#-----------------------------------------------------------------------------
# NeoDialog
#-----------------------------------------------------------------------------
class NeoDialog:
    """
    Dialog manager
    """
    #-----------------------------------------------------------------------------
    def __init__(self, factory, client_uid):
        self.configuration_server = ConfigManagerSingleton.get().getConfiguration()
        client = MongoClient(self.configuration_server['database']['server'], self.configuration_server['database']['port'])
        self.database = client.lisa

        self.wit = Wit(self.configuration_server['wit_token'])
        self.intentscollection = self.database.intents

        # Initialize dialogs
        self.factory = factory
        self.client = factory.clients[client_uid]
        self.client['context'] = NeoContext(factory = factory, client_uid = client_uid)

    #-----------------------------------------------------------------------------
    def __del__(self):
        # Clean context
        self.client['context'].clean()
        self.client.pop('context')
        try:
            pass
        except:
            pass

    #-----------------------------------------------------------------------------
    def parse(self, jsonData):
        # If input has already a decoded intent
        if jsonData.has_key("outcome") == True:
            jsonInput = {}
            jsonInput['outcome'] = jsonData['outcome']
        elif len(jsonData['body']) > 0:
            # Ask Wit for intent decoding
            jsonInput = self.wit.get_message(unicode(jsonData['body']))
        else:
            # No input => no output
            return

        # Initialize output from input
        jsonInput['from'], jsonInput['type'], jsonInput['zone'] = jsonData['from'], jsonData['type'], jsonData['zone']

        # Show wit result
        if self.configuration_server['debug']['debug_wit']:
            log.msg("WIT: " + str(jsonInput['outcome']))

        # Execute intent
        oIntent = self.intentscollection.find_one({"name": jsonInput['outcome']['intent']})
        if oIntent is not None:
            # Call plugin
            self.client['context'].parse(jsonInput = jsonInput, module_name = oIntent["module"], function_name = oIntent['function'])
        else:
            # Parse without intent
            self.client['context'].parse(jsonInput = jsonInput)

# --------------------- End of NeoDialog.py  ---------------------
