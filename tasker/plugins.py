from configuration import Config

import FirstAidKit

import imp
import os
import subprocess

class DummyPlugin(object):
    def __init__(self):
        self._diagnosed = False #diagnoistics has not been run yet
        self._state = "init" #we have no internal state yet
        pass

    #workaround, so we can use special plugins not composed of python objects
    #like shell scripts or arbitrary binaries
    def get_plugin(self):
        return self

    def call(self, step):
        """call one step from plugin"""
        return getattr(self, step)()

    def info(self):
        """Returns tuple (Plugin name, Plugin version, Plugin author)"""
        return ("Dummy plugin", "0.0.1", "Martin Sivak <msivak@redhat.com>")

    #list of all actions provided
    def actions(self):
        """Returns list of available actions"""
        return set(["init", "backup", "diagnose", "describe", "fix", "restore", "destroy"])

    #investigate internal state and tell us next action to perform in auto-mode
    def nextstep(self):
        """Returns next step needed for automated mode"""
        return self._state

    #iterate protocol allows us to use loops
    def __iter__(self):
        return self

    def next(self):
        s = self.nextstep()
        if s==None:
            raise StopIteration()
        return s

    #default (mandatory) plugin actions
    def init(self):
        self._state = "backup"
        return True

    def destroy(self):
        self._state = None
        return True

    def backup(self):
        self._state = "diagnose"
        return True

    def restore(self):
        self._state = "destroy"
        return True

    def diagnose(self):
        self._diagnosed = True
        self._state = "describe"
        return self._diagnosed

    def fix(self):
        if not self._diagnosed:
            self._state = "diagnose"
            return False

        self._state = "destroy"
        return True

    def describe(self):
        self._state = "fix"
        return ""

class BinPlugin(DummyPlugin):
    def __init__(self, bin):
        DummyPlugin.__init__(self)
        self._binpath = bin
    
    def init(self):
        self._state = "backup"
        return True

    def destroy(self):
        self._state = None
        return True

    def backup(self):
        self._state = "diagnose"
        return True

    def restore(self):
        self._state = "destroy"
        return True

    def diagnose(self):
        self._diagnosed = True
        self._state = "describe"
        return self._diagnosed

    def fix(self):
        if not self._diagnosed:
            self._state = "diagnose"
            return False

        self._state = "destroy"
        return True

    def describe(self):
        self._state = "fix"
        return ""

class PluginSystem(object):
    """Encapsulate all plugin detection and import stuff"""

    def __init__(self, config = Config):
        self._path = Config.plugin.path
        self._plugins = {}

        #create list of potential modules in the path
        importlist = set()
        for f in os.listdir(self._path):
            fullpath = os.path.join(self._path, f)
            print "Processing file: ", f
            if os.path.isdir(fullpath) and os.path.isfile(os.path.join(self._path, f, "__init__.py")):
                importlist.add(f)
                print "Adding python module (directory): ", f
            elif os.path.isfile(fullpath) and (f[-3:]==".so" or f[-3:]==".py"):
                importlist.add(f[:-3])
                print "Adding python module (file): ", f
            elif os.path.isfile(fullpath) and (f[-4:]==".pyc" or f[-4:]==".pyo"):
                importlist.add(f[:-4])
                print "Adding python module (compiled): ", f
            elif os.path.isfile(fullpath) and f[-7:]==".plugin":
                self._plugins[f[:-7]] = BinPlugin(fullpath)
                print "Importing special module: ", f

        #try to import the modules as FirstAidKit.plugins.modulename
        for m in importlist:
            if m in Config.plugin.disabled:
                continue

            imp.acquire_lock()
            try:
                print "Importing module %s from %s" % (m, self._path)
                moduleinfo = imp.find_module(m, [self._path])
                module = imp.load_module(".".join([FirstAidKit.__name__, m]), *moduleinfo)
                print "OK"
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
            print "Running step %s in plugin %s ..." % (step, plugin,)
            res = getattr(p, step)()
            print "Result is:", res

    def getplugin(self, plugin):
        """Get instance of plugin, so we can call the steps manually"""
        return self._plugins[plugin].get_plugin()

