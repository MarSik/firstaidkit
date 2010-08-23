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
import openscap_api as openscap
import time

class OpenSCAPPlugin(Plugin):
    """Performs security audit according to the SCAP policy"""
    name = "OpenSCAP audit"
    version = "0.0.1"
    author = "Martin Sivak <msivak@redhat.com>"

    flows = Flow.init(Plugin)
    del flows["fix"]
    flows["oscap_scan"] = flows["diagnose"]
    del flows["diagnose"]
    flows["oscap_scan"].description = "Performs a security and configuration audit of running system"
    flows["oscap_scan"].title = "Security Audit"

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self._oval = "/usr/share/openscap/oval.xml"
        self._xccdf = "/usr/share/openscap/scap-xccdf.xml"
        self._issues = {}
    
    def prepare(self):
        self._objs = openscap.xccdf.init(self._xccdf)
        self._xccdf_policy_model = self._objs["policy_model"]
        self._policy = None
        
        self._xccdf_policy_model.register_output_callback(self.oscap_callback, self)
        # Select the last available policy
        self._policy = self._xccdf_policy_model.policies[-1]
            
        if self._policy is None:
            self._result=ReturnFailure
            self._reporting.error("OpenSCAP failed to initialize", origin = self, level = PLUGIN)
            return
        else:
            self._reporting.info("OpenSCAP initialized", origin = self, level = PLUGIN)

        tailor_items = self._policy.get_tailor_items()
        preproces_tailor_items = lambda i: (i["id"], i["titles"][0][1] or "", i["selected"][1] or "", len(i["descs"]) and i["descs"][0][1] or "")
        tailor_items = map(preproces_tailor_items, tailor_items)

        self._reporting.info("Pre Options: %s" % repr(tailor_items), origin = self,
                             level = PLUGIN)

        s = self._reporting.config_question_wait("Setup OpenScap policy",
                                                 "Set preferred values and press OK",
                                                 tailor_items, origin = self,
                                                 level = PLUGIN)

        preprocess_s = lambda v: {"id": v[0], "value": v[1]}
        s = map(preprocess_s, s)
        self._reporting.info("Options: %s" % repr(s), origin = self,
                             level = PLUGIN)
        
        self._policy.set_tailor_items(s)
        
        self._result=ReturnSuccess
            
    def backup(self):
        self._result=ReturnSuccess

    def restore(self):
        self._result=ReturnSuccess

    def oscap_callback(self, Msg, Plugin):
        try:
            Id = Msg.user1str
            Issue = Plugin._issues.get(Id, None)
            if Issue is None:
                title = Msg.user3str
                description = Msg.string
                result = Msg.user2num
                Issue = SimpleIssue(Id, title)
                Issue.set(reporting  = Plugin._reporting, origin = Plugin, level = PLUGIN)
                Plugin._issues[Id] = Issue
                
                Issue.set(checked = (result in (openscap.OSCAP.OVAL_RESULT_FALSE, openscap.OSCAP.OVAL_RESULT_TRUE)),
                                happened = (result == openscap.OSCAP.OVAL_RESULT_FALSE),
                                fixed = False,
                                reporting  = Plugin._reporting,
                                origin = Plugin,
                                level = PLUGIN)
        except Exception, e:
            print e

        if Plugin.continuing():
            return 0
        else:
            return 1

    def diagnose(self):
        self._policy.evaluate()
        self._result=ReturnSuccess
        
    def fix(self):
        self._result=ReturnFailure
        
    def clean(self):
        #openscap.xccdf.destroy(self._objs)
        self._reporting.info("OpenSCAP deinitialized", origin = self, level = PLUGIN)
        self._result=ReturnSuccess


def get_plugin():
    return OpenSCAPPlugin
