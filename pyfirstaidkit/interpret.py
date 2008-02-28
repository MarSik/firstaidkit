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

import os
from plugins import PluginSystem
from reporting import Reports, TASKER
import logging
import copy
from errors import *

Logger=logging.getLogger("firstaidkit")

class RunDependencies(object):
    """Encapsulate flags used to control the dependencies between plugins"""
    def __init__(self):
        self._provide = set()

    def provide(self, id, setactionflag = True):
        """Add flag"""
        Logger.info("Setting dependency flag %s", id)
        self._provide.add(id)
        if setactionflag: self._provide.add(id+"?") #Action flags denote activity happening on some regular flag
    
    def unprovide(self, id, setactionflag = True):
        """Remove flag"""
        Logger.info("Resetting dependency flag %s", id)
        try:
            self._provide.remove(id)
        except KeyError: #not there
            pass
        if setactionflag: self._provide.add(id+"?")

    donotprovide = unprovide #alias
    failed = unprovide #alias

    def require(self, id):
        """Return True if flag is present, otherwise false"""
        return id in self._provide

class Tasker:
    """The main interpret of tasks described in Config object"""

    def __init__(self, cfg):
        self._provide = RunDependencies()
        self._config = cfg
        self._reporting = Reports()
        self.pluginSystem = PluginSystem(reporting = self._reporting, dependencies = self._provide)

    def reporting(self):
        return self._reporting

    def pluginsystem(self):
        return self.pluginSystem

    def end(self):
        """Signalize end of operations to all necessary places"""
        self._reporting.end()

    def run(self):
        pluginSystem = self.pluginSystem

        # Check the root privilegies
        if os.geteuid() == 0:
            self._reporting.info("You are running the firstaidkit as root.", origin = TASKER)
            self._provide.provide("root")
        else:
            self._reporting.info("You are not running the firstaidkit as root. Some plugins may not be available.", origin = TASKER)
            self._provide.unprovide("root")

        #initialize the startup set of flags
        for flag in self._config.operation._list("flags"):
            self._provide.provide(flag)

        if self._config.operation.mode in ("auto", "auto-flow"):
            flow = None
            if self._config.operation.mode == "auto-flow":
                flow = self._config.operation.flow
            oldlist = set()
            actlist = set(pluginSystem.list())
            #iterate through plugins until there is no plugin left or no action performed during whole iteration
            while len(actlist)>0 and oldlist!=actlist:
                oldlist = copy.copy(actlist)
                for plugin in oldlist:
                    #If plugin does not contain the automated flow or if it ran correctly, remove it from list
                    if flow and not flow in pluginSystem.getplugin(plugin).getFlows():
                        self._reporting.info("Plugin %s does not contain flow %s" % (plugin, flow,), origin = TASKER)
                        actlist.remove(plugin)
                    elif pluginSystem.autorun(plugin, flow = flow):
                        actlist.remove(plugin)
            for plugin in actlist:
                self._reporting.info("Plugin %s was not called because of unsatisfied dependencies" % (plugin,), origin = TASKER, importance = logging.WARNING)
        elif self._config.operation.mode == "flow":
            try:
                pluginSystem.autorun(self._config.operation.plugin, flow = self._config.operation.flow, dependencies = False)
            except InvalidFlowNameException, e:
                pass
        elif self._config.operation.mode == "plugin":
            pluginSystem.autorun(self._config.operation.plugin, dependencies = False)
        elif self._config.operation.mode == "task":
            pass
        elif self._config.operation.mode == "list":
            #get list of plugins
            rep = []
            for k in pluginSystem.list():
                p = pluginSystem.getplugin(k)
                flowinfo = [ (f, p.getFlow(f).description) for f in p.getFlows() ]
                rep.append((k, p.name, p.version, p.author, p.description, p.default_flow, flowinfo))
            self._reporting.table(rep, origin = TASKER)
        elif self._config.operation.mode == "info":
            #get info about plugin
            try:
                p = pluginSystem.getplugin(self._config.operation.params)
            except KeyError:
                Logger.error("No such plugin '%s'" % (self._config.operation.params,))
                return False
            flowinfo = [ (f, p.getFlow(f).description) for f in p.getFlows() ]
            rep = {"id": self._config.operation.params, "name": p.name, "version": p.version, "author": p.author, "description": p.description, "flow": p.default_flow, "flows": flowinfo}
            self._reporting.tree(rep, origin = TASKER)
        else:
            Logger.error("Incorrect task specified")
            return False

        return True
