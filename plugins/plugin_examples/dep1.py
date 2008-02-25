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
    name = "SampleDepends 1 -> 2"
    version = "0.0.1"
    author = "Joel Andres Granados"
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)

    @classmethod
    def getDeps(cls):
        return set(["sample_dependency"]).union(Plugin.getDeps())

    def prepare(self):
        self._result=ReturnFavorable

    def backup(self):
        self._result=ReturnFavorable

    def restore(self):
        self._result=ReturnFavorable

    def diagnose(self):
        self._result=ReturnFavorable
        self.provide("sample_dependency2")

    def fix(self):
        self._result=ReturnUnfavorable

    def clean(self):
        self._result=ReturnFavorable

def get_plugin():
    return Sample1Plugin
