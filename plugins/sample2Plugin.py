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

from tasker.plugins import Plugin

class Sample2Plugin(Plugin):
    """This plugin will defin one more function and use it in a newly defined flow."""
    def __init__(self):
        Plugin.__init__(self)

        #
        # Additional flow definition.
        #
        self.customFlow = {
                self.initial : {ReturnValue: "init"},
                "init"       : {ReturnValueTrue: "diagnose"},
                "diagnose"   : {ReturnValueTrue: "purge", ReturnValueFalse: "backup"},
                "backup"     : {ReturnValueTrue: "fix", ReturnValueFalse: "purge"},
                "restore"    : {ReturnValueTrue: "purge", ReturnValueFalse: "purge"},
                "fix"        : {ReturnValueTrue: "extraStep", ReturnValueFalse: "restore"},
                "extraStep"  : {ReturnValueTrue: "purge", ReturnValueFalse: "purge"},
                "purge"      : {ReturnValueTrue: self.final}
                }
        self._flows["default"] = self._defflow

    def init(self):
        self._result=ReturnValueTrue
        return self._result

    def purge(self):
        self._result=ReturnValueTrue
        return self._result

    def backup(self):
        self._result=ReturnValueTrue
        return self._result

    def restore(self):
        self._result=ReturnValueTrue
        return self._result

    def diagnose(self):
        self._result=ReturnValueTrue
        return self._result

    def fix(self):
        self._result=ReturnValueFalse
        return self._result

    def extraStep(self):
        self._result=ReturnValueTrue
        return self._result

def get_plugin():
    return Sample2Plugin()

