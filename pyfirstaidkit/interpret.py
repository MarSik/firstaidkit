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
from reporting import Reports, TASKER, PLUGINSYSTEM
import logging
import copy
from errors import *
from utils import FileBackupStore
from dependency import Dependencies

Logger=logging.getLogger("firstaidkit")

class Tasker:
    """The main interpret of tasks described in Config object"""

    name = "Task interpreter"

    def __init__(self, cfg):
        self._provide = Dependencies()
        self._config = cfg
        self._reporting = Reports()
        self._backups = FileBackupStore(cfg.backup.path)
        self.pluginSystem = PluginSystem(reporting = self._reporting, dependencies = self._provide, backups = self._backups)

    def reporting(self):
        return self._reporting

    def pluginsystem(self):
        return self.pluginSystem

    def end(self):
        """Signalize end of operations to all necessary places"""
        self._reporting.end()

    def run(self):
        self._reporting.start(level = TASKER, origin = self)
        pluginSystem = self.pluginSystem

        # Check the root privilegies
        if os.geteuid() == 0:
            self._reporting.info("You are running the firstaidkit as root.",
                    level = TASKER, origin = self, importance = logging.WARNING)
            self._provide.provide("root")
        else:
            self._reporting.info("You are not running the firstaidkit as root." \
                    "Some plugins may not be available.", level = TASKER, origin = self, importance = logging.WARNING)
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
                    if ((flow and not flow in pluginSystem.getplugin(plugin).getFlows()) or
                                (not flow and not pluginSystem.getplugin(plugin).default_flow in
                                pluginSystem.getplugin(plugin).getFlows())):
                        self._reporting.info("Plugin %s does not contain flow %s"%
                                (plugin, flow or pluginSystem.getplugin(plugin).default_flow,), 
                                level = TASKER, origin = self)
                        actlist.remove(plugin)
                    elif pluginSystem.autorun(plugin, flow = flow):
                        actlist.remove(plugin)
            for plugin in actlist:
                self._reporting.info("Plugin %s was not called because of unsatisfied dependencies"%
                        (plugin,), level = TASKER, origin = self, importance = logging.WARNING)
        elif self._config.operation.mode == "flow":
            try:
                pluginSystem.autorun(self._config.operation.plugin, 
                        flow = self._config.operation.flow, dependencies = False)
            except InvalidFlowNameException, e:
                pass
        elif self._config.operation.mode == "plugin":
            try:
                pluginSystem.autorun(self._config.operation.plugin, dependencies = False)
            except (InvalidPluginNameException, InvalidFlowNameException),  e:
                pass
        elif self._config.operation.mode == "task":
            pass
        elif self._config.operation.mode == "flags":
            self._reporting.table(self._provide.known(), level = TASKER, origin = self, title = "List of flags")
        elif self._config.operation.mode == "list":
            #get list of plugins
            rep = []
            for k in pluginSystem.list():
                p = pluginSystem.getplugin(k)
                flowinfo = [ (f, p.getFlow(f).description) for f in p.getFlows() ]
                rep.append((k, p.name, p.version, p.author, p.description, p.default_flow, flowinfo))
            self._reporting.table(rep, level = TASKER, origin = self, title = "List of plugins")
        elif self._config.operation.mode == "info":
            #get info about plugin
            try:
                p = pluginSystem.getplugin(self._config.operation.params)
            except KeyError:
                Logger.error("No such plugin '%s'" % (self._config.operation.params,))
                return False
            flowinfo = [ (f, p.getFlow(f).description) for f in p.getFlows() ]
            rep = {"id": self._config.operation.params, "name": p.name, 
                    "version": p.version, "author": p.author, 
                    "description": p.description, "flow": p.default_flow, "flows": flowinfo}
            self._reporting.tree(rep, level = TASKER, origin = self, 
                    title = "Information about plugin %s" % (self._config.operation.params,))
        else:
            Logger.error("Incorrect task specified")
            self._reporting.stop(level = TASKER, origin = self)
            return False

        self._reporting.stop(level = TASKER, origin = self)
        return True
