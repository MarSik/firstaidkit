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

from tasker.returns import *
from tasker.plugins import Plugin
import subprocess

class Sample3Plugin(Plugin):
    """This plugin will use a shell script as backend."""
    def __init__(self):
        Plugin.__init__(self)

    def init(self):
        # Prepare command line.
        init = ["/usr/lib/FirstAidKit/plugins/sample3Plugin/plugin", "--task", "init"]
        proc = subprocess.Popen(init, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue
        return self._result

    def purge(self):
        purge = ["/usr/lib/FirstAidKit/plugins/sample3Plugin/plugin", "--task", "purge"]
        proc = subprocess.Popen(purge, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue
        return self._result

    def backup(self):
        backup = ["/usr/lib/FirstAidKit/plugins/sample3Plugin/plugin", "--task", "backup"]
        proc = subprocess.Popen(backup, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue
        return self._result

    def restore(self):
        restore = ["/usr/lib/FirstAidKit/plugins/sample3Plugin/plugin", "--task", "restore"]
        proc = subprocess.Popen(restore, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue
        return self._result

    def diagnose(self):
        diagnose = ["/usr/lib/FirstAidKit/plugins/sample3Plugin/plugin", "--task", "diagnose"]
        proc = subprocess.Popen(diagnose, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue
        return self._result

    def fix(self):
        fix = ["/usr/lib/FirstAidKit/plugins/sample3Plugin/plugin", "--task", "fix"]
        proc = subprocess.Popen(fix, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue
        return self._result

def get_plugin():
    return Sample3Plugin()

