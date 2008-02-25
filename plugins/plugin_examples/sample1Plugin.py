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
from pyfirstaidkit.returns import *

class Sample1Plugin(Plugin):
    """This plugin uses the predefined flow in the Plugin abstract class."""
    name = "Sample1Plugin"
    version = "0.0.1"
    author = "Joel Andres Granados"
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.reporting = kwargs.get('reporting')

    def prepare(self):
        self._result=Favorable
        self.reporting.info("Sample1Plugin in Prepare task", self)

    def backup(self):
        self._result=Favorable
        self.reporting.info("Sample1Plugin in backup task", self)

    def restore(self):
        self._result=Favorable
        self.reporting.info("Sample1Plugin in Restore task", self)

    def diagnose(self):
        self._result=Favorable
        self.reporting.info("Sample1Plugin in diagnose task", self)

    def fix(self):
        self._result=Unfavorable
        self.reporting.info("Sample1Plugin in Fix task", self)

    def clean(self):
        self._result=Favorable
        self.reporting.info("Sample1Plugin in Clean task", self)

def get_plugin():
    return Sample1Plugin
