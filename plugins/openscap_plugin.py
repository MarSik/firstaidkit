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
import openscap

class OpenSCAPPlugin(Plugin):
    """Performs security audit according to the SCAP policy"""
    name = "OpenSCAP audit"
    version = "0.0.1"
    author = "Martin Sivak <msivak@redhat.com>"

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self._oval = "/usr/share/openscap/scap-fedora12-oval.xml"
        self._issues = {}
    
    def prepare(self):
        self._model = openscap.oval_definition_model_import(self._oval)
        self._session = openscap.oval_agent_new_session(self._model)
        self._reporting.info("OpenSCAP initialized", origin = self, level = PLUGIN)
        self._result=ReturnSuccess

    def backup(self):
        self._result=ReturnSuccess

    def restore(self):
        self._result=ReturnSuccess

    def oscap_callback(Id, Result, Plugin):
        Issue = Plugin._issues.get(Id, None)
        if Issue is None:
            title = openscap.oval_definition_get_title(Plugin._model, Id)
            description = openscap.oval_definition_get_description(Plugin._model, Id)
            Issue = SimpleIssue(Id, title)
            Issue.set(reporting  = Plugin._reporting, origin = Plugin, level = PLUGIN)
            Plugin._issues[Id] = Issue

        self._issue.set(checked = (Result in (openscap.OVAL_RESULT_FALSE, openscap.OVAL_RESULT_TRUE)),
                        happened = (Result == openscap.OVAL_RESULT_FALSE),
                        fixed = False,
                        reporting  = self._reporting,
                        origin = self,
                        level = PLUGIN)

    def diagnose(self):
        self._result=ReturnSuccess
        openscap.oval_agent_eval_system_py(self._session, self.oscap_callback, self)
        
        self._issue.set(checked = True, happened = False, reporting  = self._reporting, origin = self, level = PLUGIN)
        
    def fix(self):
        self._result=ReturnFailure
        
    def clean(self):
        openscap.oval_agent_destroy_session(self._session)
        openscap.oval_definition_model_free(self._model)
        openscap.oscap_cleanup()
        self._reporting.info("OpenSCAP deinitialized", origin = self, level = PLUGIN)
        self._result=ReturnSuccess


def get_plugin():
    return OpenSCAPPlugin
