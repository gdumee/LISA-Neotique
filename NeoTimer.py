# -*- coding: UTF-8 -*-
#-----------------------------------------------------------------------------
# project     : Lisa server
# module      : Neotique
# file        : NeoTimer.py
# description : Timer with callback
# author      : G.Dumee, G.Audet
#-----------------------------------------------------------------------------
# copyright   : Neotique
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from threading import Timer
from time import time, sleep


#-----------------------------------------------------------------------------
# Timer class
#-----------------------------------------------------------------------------
class NeoTimer():
    """
    Timer with a user callback
    """
    def __init__(self, duration_s, user_cbk, user_param):
        """
        Create a new timer
        """
        # Set internals
        self.running = True
        self.end = time() + duration_s
        self.user_cbk = user_cbk
        self.user_param = user_param

        # Start timer
        self.timer = Timer(duration_s, self._timer_cbk)
        self.timer.start()

    #-----------------------------------------------------------------------------
    def __del__(self):
        #TODO debug delete context and timers
        print "Del timer"
        self.stop()

    #-----------------------------------------------------------------------------
    def _timer_cbk(self):
        """
        Internal Timer callback
        """
        # Call user callback
        self.user_cbk(self.user_param)
        self.timer.cancel()

        # Set running state
        self.running = False

    #-----------------------------------------------------------------------------
    def stop(self):
        """
        Stop current timer
        """
        # If not running
        if self.running == False:
            return

        # Stop timer
        self.running = False
        self.timer.cancel()

    #-----------------------------------------------------------------------------
    def get_left_time_s(self):
        """
        Return timer left time in seconds
        """
        # If not running
        if self.running == False:
            return 0

        return self.end - time()

# --------------------- End of NeotTimer.py  ---------------------
