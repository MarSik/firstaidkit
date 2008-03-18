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

from pyfirstaidkit.plugins import IssuesPlugin,Flow
from pyfirstaidkit.returns import *
from pyfirstaidkit.utils import *
from pyfirstaidkit.reporting import PLUGIN,TASK
from pyfirstaidkit import Config

from issue_packages import Packages

class RPMLowlevelPlugin(IssuesPlugin):
    """This plugin provides lowlevel checks for RPM database."""
    #
    # Additional flow defprepareion.
    #
    flows = Flow.init(IssuesPlugin)

    name = "RPM lowlevel structure plugin"
    version = "0.0.1"
    author = "Martin Sivak"

    issue_tests = [Packages]
    set_flags = ["rpm_lowlevel"]

    @classmethod
    def getDeps(cls):
        return set(["root", "experimental", "filesystem"])

    def __init__(self, *args, **kwargs):
        IssuesPlugin.__init__(self, *args, **kwargs)
        self.rpm = None

    def prepare(self):
        IssuesPlugin.prepare(self)

    def backup(self):
        self._result=ReturnSuccess

    def restore(self):
        self._result=ReturnSuccess

    def clean(self):
        self._result=ReturnSuccess

def get_plugin():
    return RPMLowlevelPlugin
