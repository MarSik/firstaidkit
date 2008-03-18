# File name: issue_filesystem.py
# Date:      2008/03/14
# Author:    Martin Sivak <msivak at redhat dot com>
#
# Copyright (C) Red Hat 2008
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# in a file called COPYING along with this program; if not, write to
# the Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA
# 02139, USA.

from pyfirstaidkit.issue import Issue
from pyfirstaidkit.reporting import TASK
from pyfirstaidkit.utils import spawnvch
from pyfirstaidkit.configuration import Config
import os.path


class Packages(Issue):
    name = "Required Packages database"
    description = "The file containing the rpm database of packages is missing"

    def detect(self):
        result = Issue.detect(self)
        if result is not None:
            return result

        dbname = Config.system.root+"/var/lib/rpm/Packages"

        if os.path.isfile(os.path.realpath(dbname)):
            self._happened = False
        else:
            self._happened = True

        self._detected = True
        return True

    def fix(self):
        result = Issue.fix(self)
        if result is not None:
            return result

        rpm = spawnvch(executable = "/usr/bin/rpm", args = ["rpm", "--rebuilddb"], chroot = Config.system.root).wait()
        if rpm.returncode==0:
            self._fixed = True
        return True
