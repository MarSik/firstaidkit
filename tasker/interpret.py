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

from log import Logger
from plugins import PluginSystem
from reporting import Reports, TASKER
import logging
import copy

class RunDependencies(object):
    """Encapsulate flags used to control the dependencies between plugins"""
    def __init__(self):
        self._provide = set()

    def provide(self, id):
        """Add flag"""
        self._provide.add(id)

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

        if self._config.operation.mode == "auto":
            oldlist = set()
            actlist = set(pluginSystem.list())
            #iterate through plugins until there is no plugin left or no action performed during whole iteration
            while len(actlist)>0 and oldlist!=actlist:
                oldlist = copy.copy(actlist)
                for plugin in oldlist:
                    if pluginSystem.autorun(plugin): #False when dependencies are not met
                        actlist.remove(plugin)
            for plugin in aclist:
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
        else:
            Logger.error("Incorrect task specified")
            return False

        return True
