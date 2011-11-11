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

from pyfirstaidkit.plugins import Plugin,Flow
from pyfirstaidkit.reporting import PLUGIN
from pyfirstaidkit.returns import *
from pyfirstaidkit.issue import SimpleIssue
from .blueprint import BlueprintPlugin

class PackagesPlugin(BlueprintPlugin):
    """This plugin retrieve list of all installed packages and their versions."""
    name = "RPM Packages"
    version = "0.0.1"
    author = "Martin Sivak"
    
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self._issue = SimpleIssue(self.name, self.description)
        self.rpmlib = None

    def prepare(self):
        import rpm
        self.rpmlib = rpm
        self._result=ReturnSuccess
        self._issue.set(reporting  = self._reporting, origin = self, level = PLUGIN)
        self._reporting.info("RPM properly initialized", origin = self, level = PLUGIN)

    def diagnose(self):
        self._reporting.info("Getting list of RPM packages", origin = self, level = PLUGIN)
        ts = self.rpmlib.TransactionSet()
        mi = ts.dbMatch()
        for h in mi:
            setattr(self._info, h["name"], "%s-%s" % (h["version"], h["release"]))
            
        self._result=ReturnSuccess
        self._issue.set(checked = True, happened = False, reporting  = self._reporting, origin = self, level = PLUGIN)

    def clean(self):
        del self.rpmlib
        self._result=ReturnSuccess

def get_plugin():
    return PackagesPlugin
