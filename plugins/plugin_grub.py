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
from pyfirstaidkit.configuration import Config
from pyfirstaidkit.utils import spawnvch
import os.path
import difflib
import re

class Sample1Plugin(Plugin):
    """This plugin checks the GRUB bootloader."""
    name = "GRUB plugin"
    version = "0.0.1"
    author = "Martin Sivak"

    @classmethod
    def getDeps(cls):
        return set(["experimental", "root", "filesystem"])

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self._partitions = []
        self._grub_dir = []
        self._grub = []
        self._grub_map = {}
        self._grub_mask = re.compile("""\(hd[0-9]*,[0-9]*\)""")

    def prepare(self):
        self._result=ReturnSuccess

    def backup(self):
        self._result=ReturnSuccess

    def restore(self):
        self._result=ReturnSuccess

    def diagnose(self):
        #Find partitions
        self._reporting.debug(origin = self, level = PLUGIN, message = "Reading partition list")
        self._partitions = map(lambda l: l.split()[3], file("/proc/partitions").readlines()[2:])

        #Find grub directories
        self._reporting.debug(origin = self, level = PLUGIN, message = "Locating the grub directories")
        grub = spawnvch(executable = "/sbin/grub", args = ["grub", "--batch"], chroot = Config.system.root)
        (stdout, stderr) = grub.communicate("find /boot/grub/menu.lst\nfind /grub/menu.lst\n")
        for l in stdout.split("\n"):
            if self._grub_mask.search(l):
                self._reporting.info(origin = self, level = PLUGIN, message = "Grub directory found at %s" % (l.strip(),))
                self._grub_dir.append(l.strip())

        #Read the device map
        self._reporting.debug(origin = self, level = PLUGIN, message = "Reading device map")
        for l in file(os.path.join(Config.system.root, "/boot/grub/device.map"), "r").readlines():
            if l.startswith("#"):
                continue
            (v,k) = l.split()
            self._grub_map[k] = v

        #Find out where is the grub installed
        stage1mask = file(os.path.join(Config.system.root, "/boot/grub/stage1"), "r").read(512)
        bootsectors = {}
        for p in self._partitions:
            self._reporting.debug(origin = self, level = PLUGIN, message = "Reading boot sector from %s" % (p,))
            bootsector = file(os.path.join("/dev", p), "r").read(512)
            bootsectors[bootsector] = os.path.join("/dev", p)

        for k in difflib.get_close_matches(stage1mask, bootsectors.keys()):
            self._reporting.info(origin = self, level = PLUGIN, message = "Installed Grub found at %s" % (bootsectors[k],))
            self._grub.append(k)

        self._result=ReturnSuccess

    def fix(self):
        self._result=ReturnFailure

    def clean(self):
        self._result=ReturnSuccess

def get_plugin():
    return Sample1Plugin