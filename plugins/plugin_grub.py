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
from pyfirstaidkit.configuration import Config,getConfigBits
from pyfirstaidkit.utils import spawnvch
import os.path
import difflib
import re

cfgBits = getConfigBits("firstaidkit-plugin-grub")
import sys
sys.path.append(cfgBits.anaconda.path)
sys.path.append(cfgBits.booty.path)
from bootloaderInfo import x86BootloaderInfo

class Sample1Plugin(Plugin):
    """This plugin checks the GRUB bootloader."""
    name = "GRUB plugin"
    version = "0.0.1"
    author = "Martin Sivak"

    @classmethod
    def getDeps(cls):
        return set(["experimental", "root", "filesystem", "arch-x86"])

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self._partitions = [] #partitions in the system
        self._drives = [] #drives in the system
        self._bootable = [] #partitions with boot flag
        self._linux = [] #Linux type partitions (0x83 Linux)
        self._grub_dir = [] #directories with stage1, menu.lst and other needed files
        self._grub = [] #devices with possible grub instalation
        self._grub_map = {} #mapping from linux device names to grub device names
        self._grub_mask = re.compile("""\(hd[0-9]*,[0-9]*\)""")
        self._bootloaderInfo = x86BootloaderInfo()

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

        #and select only partitions with minor number 0 -> drives
        self._drives = map(lambda l: l.split(), file("/proc/partitions").readlines()[2:])
        self._drives = filter(lambda l: l[1]=="0", self._drives)
        self._drives = map(lambda l: l[3], self._drives)

        #get boot flags
        self._reporting.debug(origin = self, level = PLUGIN, message = "Locating bootable partitions")
        for d in self._drives:
            fdisk = spawnvch(executable = "/sbin/fdisk", args = ["fdisk", "-l", "/dev/%s" % (d,)], chroot = Config.system.root)
            ret = fdisk.wait()
            if ret==0:
                for l in fdisk.stdout.readlines():
                    if l.startswith("/dev/%s" % (d,)):
                        data = l.split()
                        if data[1]=="*": #boot flag
                            self._reporting.info(origin = self, level = PLUGIN, message = "Bootable partition found: %s" % (data[0][5:],))
                            self._bootable.append(data[0][5:]) #strip the "/dev/" beginning
                            if data[6]=="Linux":
                                self._linux.append(data[0][5:])
                                self._reporting.debug(origin = self, level = PLUGIN, message = "Linux partition found: %s" % (data[0][5:],))
                        else:
                            if data[5]=="Linux":
                                self._linux.append(data[0][5:])
                                self._reporting.debug(origin = self, level = PLUGIN, message = "Linux partition found: %s" % (data[0][5:],))


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
            bootsectors[bootsector] = self._bootloaderInfo.grubbyPartitionName(p)

        for k in difflib.get_close_matches(stage1mask, bootsectors.keys()):
            self._reporting.info(origin = self, level = PLUGIN, message = "Installed Grub probably found at %s" % (bootsectors[k],))
            self._grub.append(bootsectors[k])

        #if there is the grub configuration dir and the grub appears installed into MBR or bootable partition, then we are probably OK
        if len(self._grub_dir)>0 and len(self._grub)>0 and len(set(self._grub).intersection(set(self._bootable+self._drives)))>0:
            self._result=ReturnSuccess
            self._dependencies.provide("boot-grub")
        else:
            self._result=ReturnFailure

    def fix(self):
        self._result=ReturnFailure

    def clean(self):
        self._result=ReturnSuccess

def get_plugin():
    return Sample1Plugin
