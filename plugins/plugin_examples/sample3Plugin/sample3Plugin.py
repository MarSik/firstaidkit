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

from pyfirstaidkit.returns import *
from pyfirstaidkit.plugins import Plugin,Flow
from pyfirstaidkit import Config
import subprocess

class Sample3Plugin(Plugin):
    """This plugin will use a shell script as backend."""
    name = "Sample3Plugin"
    version = "0.0.1"
    author = "Joel Andres Granados"

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self,  *args, **kwargs)

    def prepare(self):
        # Prepare command line.
        prepare = [Config.plugin.path+"/sample3Plugin/plugin", "--task", "prepare"]
        proc = subprocess.Popen(prepare, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue

    def clean(self):
        clean = [Config.plugin.path+"/sample3Plugin/plugin", "--task", "clean"]
        proc = subprocess.Popen(clean, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue

    def backup(self):
        backup = [Config.plugin.path+"/sample3Plugin/plugin", "--task", "backup"]
        proc = subprocess.Popen(backup, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue

    def restore(self):
        restore = [Config.plugin.path+"/sample3Plugin/plugin", "--task", "restore"]
        proc = subprocess.Popen(restore, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue

    def diagnose(self):
        diagnose = [Config.plugin.path+"/sample3Plugin/plugin", "--task", "diagnose"]
        proc = subprocess.Popen(diagnose, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue

    def fix(self):
        fix = [Config.plugin.path+"/sample3Plugin/plugin", "--task", "fix"]
        proc = subprocess.Popen(fix, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.strip()
        if out[-5:] == "false":
            self._result=ReturnValueFalse
        elif out[-4:] == "true":
            self._result=ReturnValueTrue
