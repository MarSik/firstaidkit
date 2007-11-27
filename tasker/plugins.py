# First Aid Kit - diagnostic and repair tool for Linux
# Copyright (C) 2007 Martin Sivak <msivak@redhat.com>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from configuration import Config
from returns import *
from errors import *

import FirstAidKit
from log import Logger

import imp
import os
import subprocess
from cStringIO import StringIO

class Plugin(object):
    #
    # Some information vars.
    #
    name = "Plugin"
    version = "0.0.0"
    author = "nobody"
    #
    # Dictionary that holds all the flows.  The keys for each flow is its
    # name.  The flow will be addressed by this name.  The plugin developer
    # Can add as many flows as he wants. The developer must use the instance.
    # obj._flows["name"] = SomeFlow.  Be aware that you can overwirhte 
    # previously added flows.  This class attribute has to be overriden by 
    # each plugin.
    #
    flows = {}

    #
    # The initial and final states are here to give more flexibilty to the
    # Development process.  All flows will start and end with these two
    # Variables.
    #
    initial = 0
    final = 1

    #
    # The flow to use with the automated repair mode
    #

    default_flow = "defflow"

    #
    # This is the default flow that all classes deriving from plugin must
    # have.  As the initial state has no return value it will be indexed
    # with the parent of all ReturnValue classes.
    #
    _defflows = {}
    _defflows["defflow"] = {
            initial : {ReturnValue: "prepare"},
            "prepare"    : {ReturnValueTrue: "diagnose"},
            "diagnose"   : {ReturnValueTrue: "clean", ReturnValueFalse: "backup"},
            "backup"     : {ReturnValueTrue: "fix", ReturnValueFalse: "clean"},
            "fix"        : {ReturnValueTrue: "clean", ReturnValueFalse: "restore"},
            "restore"    : {ReturnValueTrue: "clean", ReturnValueFalse: "clean"},
            "clean"      : {ReturnValueTrue: final}
            }

    def __init__(self, flow):
        """ Initialize the instance.

        flow -- Name of the flow to be used with this instance.

        The flow is defined in the __init__ so we don't have to worry about changing it.
        """
        #
        # state we are in.
        #
        self._state = Plugin.initial

        #
        # Used to hold the return value of the functions in the class.
        #
        self._result = None  #edge from the state we are in

        #
        # Choose the flow for the instance.
        #
        self.defineFlow(flow)

    def call(self, step):
        """call one step from plugin"""
        self._result = None #mark new unfinished step
        self._state = step
        return getattr(self, step)()

    @classmethod
    def info(cls):
        """Returns tuple (Plugin name, Plugin version, Plugin author)"""
        return (cls.name, cls.version, cls.author)

    #
    # The flow functions.
    #
    def defineFlow(self, flow):
        """Defines the current flow to name.

        flow -- Name of the flow
        This function is to be called from the __init__ only. There will be the flows defined by the
        Plugin class and the flows defined by the actual plugin.  We will first search the Plugin
        class and then the plugin itself for the name.
        """
        #
        # The flow that will be used for the instance.
        #
        if flow in Plugin._defflows.keys():
            self.cflow = Plugin._defflows[flow]
        elif flow in self.__class__.flows.keys():
            self.cflow = self.__class__.flows[flow]
        else:
            raise InvalidFlowNameException(flow)

    @classmethod
    def getFlows(cls):
        """Return a set with the names of all possible flows."""
        fatherf = Plugin._defflows.keys()
        pluginf = cls.flows.keys()
        return set(fatherf+pluginf)

    #list of all actions provided
    def actions(self):
        """Returns list of available actions"""
        return set(["prepare", "backup", "diagnose", "describe", "fix", "restore", "clean"])

    def nextstate(self, state=None, result=None):
        """Returns next state when analizing self._state, self._result and the self.cflow in automode.

        state -- Name of hte function.
        result -- The return value of the previous function
        We do not check for validity of the key in the self.cflow.  If key is invalid, function will
        Traceback.  When self._state = self.final the function will traceback.  This situation must
        be handled outside this function.  If an automatica iteration is needed that avoids the 
        necesity to address the self.final state, use __iter__ and next.
        """
        # If any of the vals are missing, we default to the current ones.
        if state is None or result is None:
            state=self._state
            result=self._result
        # The self.initial state does not have any return code.
        # It will only work with the ReturnValue.
        try:
            if state == self.initial:
                self._state = self.cflow[self.initial][ReturnValue]
            else:
                self._state = self.cflow[state][result]
            return self._state
        except KeyError:
            raise InvalidFlowStateException(self.cflow)

    #
    #iterate protocol allows us to use loops
    #
    def __iter__(self):
        self._state = self.initial
        self._result = None
        return self

    def next(self):
        """Iteration function.

        Will return (self._state, self._result).  The function that was executed and the return value.
        """
        func = self.nextstate()
        if func == self.final:
            raise StopIteration()
        else:
            # Execute the function.
            getattr(self, func)()
        return (self._state, self._result)

    #
    #default (mandatory) plugin actions
    #
    def prepare(self):
        """Initial actions.

        All the actions that must be done before the execution of any plugin function.
        This function generaly addresses things that are global to the plugin.
        """
        #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            Logger.warning("Clean is an abstract method, it should be used as such.")

    def clean(self):
        """Final actions.

        All the actions that must be done after the exection of all plugin functions.
        This function generaly addresses things that are global and need to be closed
        off, like file descriptos, or mounted partitions....
        """
        #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            Logger.warning("Clean is an abstract method, it should be used as such.")

    def backup(self):
        """Gather important information needed for restore."""
        #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            Logger.warning("Clean is an abstract method, it should be used as such.")

    def restore(self):
        """Try to restore the previous state described in backup."""
        #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            Logger.warning("Clean is an abstract method, it should be used as such.")

    def diagnose(self):
        """Diagnose the situation."""
        #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            Logger.warning("Clean is an abstract method, it should be used as such.")

    def fix(self):
        """Try to fix whatever is wrong in the system."""
         #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            Logger.warning("Clean is an abstract method, it should be used as such.")

class PluginSystem(object):
    """Encapsulate all plugin detection and import stuff"""

    def __init__(self, config = Config):
        self._path = Config.plugin.path
        self._plugins = {}

        #create list of potential modules in the path
        importlist = set()
        for f in os.listdir(self._path):
            fullpath = os.path.join(self._path, f)
            Logger.debug("Processing file: %s", f)
            if os.path.isdir(fullpath) and os.path.isfile(os.path.join(self._path, f, "__init__.py")):
                importlist.add(f)
                Logger.debug("Adding python module (directory): %s", f)
            elif os.path.isfile(fullpath) and (f[-3:]==".so" or f[-3:]==".py"):
                importlist.add(f[:-3])
                Logger.debug("Adding python module (file): %s", f)
            elif os.path.isfile(fullpath) and (f[-4:]==".pyc" or f[-4:]==".pyo"):
                importlist.add(f[:-4])
                Logger.debug("Adding python module (compiled): %s", f)

        #try to import the modules as FirstAidKit.plugins.modulename
        for m in importlist:
            if m in Config.plugin.disabled:
                continue

            imp.acquire_lock()
            try:
                Logger.debug("Importing module %s from %s", m, self._path)
                moduleinfo = imp.find_module(m, [self._path])
                module = imp.load_module(".".join([FirstAidKit.__name__, m]), *moduleinfo)
                Logger.debug("... OK")
            finally:
                imp.release_lock()

            self._plugins[m] = module

    def list(self):
        """Return the list of imported plugins"""
        return self._plugins.keys()

    def autorun(self, plugin):
        """Perform automated run of plugin"""
        pklass = self._plugins[plugin].get_plugin() #get top level class of plugin
        Logger.info("Plugin information...")
        Logger.info("name:%s , version:%s , author:%s " % pklass.info())
        flows = pklass.getFlows()
        Logger.info("Provided flows : %s " % flows)
        flowName = pklass.default_flow
        Logger.info("Using %s flow" % flowName)
        p = pklass(flowName)
        for (step, rv) in p: #autorun all the needed steps
            Logger.info("Running step %s in plugin %s ...", step, plugin)
            Logger.info("%s is current step and %s is result of that step." % (step, rv))

    def getplugin(self, plugin):
        """Get instance of plugin, so we can call the steps manually"""
        return self._plugins[plugin].get_plugin()

