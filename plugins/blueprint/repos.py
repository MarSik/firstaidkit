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

import os

class RepositoriesPlugin(BlueprintPlugin):
    """This blueprint plugin retrieve list of all installed Yum repositories."""
    name = "Yum repositories"
    version = "0.0.1"
    author = "Martin Sivak"

    flows = Flow.init(Plugin)
    del flows["fix"]
    flows["blueprint"] = flows["diagnose"]
    
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self._issue = SimpleIssue(self.name, self.description)
        self._yum_repos_d = "/etc/yum.repos.d"

    def prepare(self):
        self._result=ReturnSuccess
        self._issue.set(reporting  = self._reporting, origin = self, level = PLUGIN)

    def diagnose(self):
        self._reporting.info("Getting list of Yum repository files", origin = self, level = PLUGIN)
        repos = [n[:-5] for n in os.listdir(self._yum_repos_d) if n.endswith(".repo")]

        for fn in repos:
            repo_issue = None
            try:
                repo_issue = SimpleIssue("reading Yum repo config %s" % fn, "I was unable to process the repository configuration.")
                repo_issue.set(checked = False, happened = False, reporting  = self._reporting, origin = self, level = PLUGIN)
                f = open(os.path.join(self._yum_repos_d, fn+".repo"))
                content = f.read().replace("\\", "\\\\").replace("\n","\\n")
                setattr(self._info, fn, content)
                f.close()
                repo_issue.set(checked = True, happened = False, reporting  = self._reporting, origin = self, level = PLUGIN)
            except IOError:
                repo_issue.set(checked = True, happened = True, reporting  = self._reporting, origin = self, level = PLUGIN)
            
        self._result=ReturnSuccess
        self._issue.set(checked = True, happened = False, reporting  = self._reporting, origin = self, level = PLUGIN)

    def clean(self):
        self._result=ReturnSuccess

def get_plugin():
    return RepositoriesPlugin
