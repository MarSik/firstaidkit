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

import FirstAidKit
from log import Logger

import imp
import os
import subprocess
from cStringIO import StringIO

class Plugin(object):
    def __init__(self):
        self._state = "pre" #state we are in
        self._result = True  #edge from the state we are in
        self._flow = {       #define transition rules for state changes
                "pre" : {True: "init"},
                "init": {True: "diagnose", False: None, None: None},
                "diagnose": {True: "destroy", False: "backup", None: "destroy"},
                "backup": {True: "fix", False: "destroy", None: "destroy"},
                "fix": {True: "destroy", False: "restore", None: "restore"},
                "restore": {True: "destroy", "False": "destroy", None: "destroy"},
                "destroy": {True: None, False: None, None: None}
                }
        pass

    #workaround, so we can use special plugins not composed of python objects
    #like shell scripts or arbitrary binaries
    def get_plugin(self):
        return self

    def call(self, step):
        """call one step from plugin"""
        self._result = None #mark new unfinished step
        self._state = step
        return getattr(self, step)()

    def info(self):
        """Returns tuple (Plugin name, Plugin version, Plugin author)"""
        return ("Dummy plugin", "0.0.1", "Martin Sivak <msivak@redhat.com>")

    #list of all actions provided
    def actions(self):
        """Returns list of available actions"""
        return set(["init", "backup", "diagnose", "describe", "fix", "restore", "destroy"])

    #investigate internal state and tell us next action to perform in auto-mode
    def nextstep(self, step = None, result = None):
        """Returns next step needed for automated mode"""
        if step is None:
            step=self._state
        if result is None:
            result=self._result
        self._state = self._flow[step][result]
        return self._state

    #iterate protocol allows us to use loops
    def __iter__(self):
        self._state = "pre"
        self._result = True
        return self

    def next(self):
        s = self.nextstep()
        if s==None:
            raise StopIteration()
        return s

    #default (mandatory) plugin actions
    def init(self):
        """Initial actions.

        All the actions that must be done before the execution of any plugin function.
        This function generaly addresses things that are global to the plugin.
        """
        #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            raise TypeError, "Plugin is an abstract class."

    def destroy(self):
        """Final actions.

        All the actions that must be done after the exection of all plugin functions.
        This function generaly addresses things that are global and need to be closed
        off, like file descriptos, or mounted partitions....
        """
        #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            raise TypeError, "Plugin is an abstract class."

    def backup(self):
        """Gather important information needed for restore."""
        #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            raise TypeError, "Plugin is an abstract class."

    def restore(self):
        """Try to restore the previous state described in backup."""
        #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            raise TypeError, "Plugin is an abstract class."

    def diagnose(self):
        """Diagnose the situation."""
        #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            raise TypeError, "Plugin is an abstract class."

    def fix(self):
        """Try to fix whatever is wrong in the system."""
         #We want these functions to be overridden by the plugin developer.
        if self.__class__ is Plugin:
            raise TypeError, "Plugin is an abstract class."

class BinPlugin(Plugin):
    def __init__(self, bin):
        Plugin.__init__(self)
        self._binpath = bin
        self._output = {}
    
    def common(self, step, okresult = True, failresult = False):
        ind = ""
        proc = subprocess.Popen([self._binpath, step], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (out, _) = proc.communicate(ind)
        err = proc.returncode
        self._output[step] = out
        if err==0:
            self._result = okresult
            return True
        else:
            self._result = failresult
            return False

    def init(self):
        return self.common("init")

    def destroy(self):
        return self.common("destroy")

    def backup(self):
        return self.common("backup")

    def restore(self):
        return self.common("restore")

    def diagnose(self):
        return self.common("diagnose")

    def fix(self):
        return self.common("fix")

    def describe(self):
        r = self.common("describe")
        return self._output["describe"]

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
            elif os.path.isfile(fullpath) and f[-7:]==".plugin":
                self._plugins[f[:-7]] = BinPlugin(fullpath)
                Logger.debug("Importing special module: %s", f)

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
        p = self._plugins[plugin].get_plugin() #get instance of plugin
        for step in p: #autorun all the needed steps
            Logger.info("Running step %s in plugin %s ...", step, plugin)
            try:
                res = p.call(step)
                Logger.info("Result is: "+str(res))
            except Exception, e:
                Logger.error("Step %s caused an unhandled exception %s", step, str(e))

    def getplugin(self, plugin):
        """Get instance of plugin, so we can call the steps manually"""
        return self._plugins[plugin].get_plugin()

