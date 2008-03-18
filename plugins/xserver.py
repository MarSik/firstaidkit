# First Aid Kit - diagnostic and repair tool for Linux
# Copyright (C) 2008 Joel Andres Granados <jgranado@redhat.com>
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
from pyfirstaidkit.utils import *
from pyfirstaidkit.reporting import PLUGIN
from pyfirstaidkit import Config

import rhpxl.xserver
import rhpl.keyboard
import tempfile
import subprocess
import time
import signal
import os
import os.path
import shutil

class Xserver(Plugin):
    """ Plugin to detect an rescue faulty xserver configurations. """

    name = "X server"
    version = "0.0.1"
    author = "Joel Andres Granados"
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        # Arbitrary test display
        self.display = ":10"
        # For when we need a temporary log.
        (self.tmpLogfd, self.tmpLogPath) = tempfile.mkstemp()
        self.confPath = "/etc/X11/xorg.conf"

    def prepare(self):
        # Nothing to prepare really.
        self._result = ReturnSuccess

    # If we cant start the server 
    def diagnose(self):
        if self.serverStart():
            self._reporting.info("Everything seems ok with the X server.", level = PLUGIN, origin = self)
            self._result = ReturnSuccess
        else:
            self._reporting.info("X server is missconfigured.", level = PLUGIN, origin = self)
            self._result = ReturnFailure

    # FIXME:Must change this when the backup utils is done.
    def backup(self):
        if os.path.isfile(self.confPath):
            self._reporting.info("Making copy of %s"%self.confPath, level = PLUGIN , origin = self)
            try:
                shutil.copyfile(self.confPath, "%s.FAK-backup"%self.confPath)
                self._result = ReturnSuccess
            except:
                self._result = ReturnFailure
        else:
            self._reporting.info("Expected path to configuration file seems to be nonexistent (%s)"%
                    self.confPath, level = PLUGIN, origin = self)
            self._result = ReturnSuccess

    def fix(self):
        self._reporting.info("Starting the fix task.", level = PLUGIN, origin = self)
        xserver = rhpxl.xserver.XServer()
        self._reporting.info("Probing for HardWare.", level = PLUGIN, origin = self)
        xserver.probeHW()
        xserver.setHWState()
        xserver.keyboard = rhpl.keyboard.Keyboard()
        self._reporting.info("Generating configuration file.", level = PLUGIN, origin = self)
        xserver.generateConfig()
        self._reporting.info("Writing configuration file to %s."%self.confPath, level = PLUGIN, origin = self)
        xserver.writeConfig(self.confPath)

        self._reporting.info("Testing created file", level = PLUGIN, origin = self)
        if self.serverStart():
            self._reporting.info("X server started successfully with new file.", level = PLUGIN, origin = self)
            self._result = ReturnSuccess
        else:
            self._reporting.info("X server is still missconfigured with new file.", level = PLUGIN, origin = self)
            self._result = ReturnFailure

    def restore(self):
        if os.path.isfile("%s.FAK-backup"%self.confPath):
            self._reporting.info("Restoring original file.", level = PLUGIN , origin = self)
            shutil.copyfile("%s.FAK-backup"%self.confPath, self.confPath)
        else:
            self._reporting.info("The backedup file was not present, something strange is going on.",
                    level = PLUGIN, origin = self)

    def clean(self):
        self._reporting.info("Cleaning the backedup file.", level = PLUGIN, origin = self)
        if os.path.isfile("%s.FAK-backup"%self.confPath):
            os.remove("%s.FAK-backup"%self.confPath)



    def serverStart(self):
        self._reporting.info("Trying to start X server", level = PLUGIN, origin = self)
        xorgargs = ["-logfile", self.tmpLogPath, self.display]
        try:
            proc = spawnvch(executable = "/usr/bin/Xorg", args = xorgargs, chroot = Config.system.root)
            self._reporting.info("Waiting for the X server to start...", level = PLUGIN, origin = self)
            time.sleep(5)
            if proc.poll() is not None:
                # process has terminated, failed.
                raise OSError
        except:
            self._reporting.info("The X server has failed to start", level = PLUGIN, origin = self)
            return False
        self._reporting.info("The X server has started successfully", level = PLUGIN, origin = self)
        os.kill(proc.pid, signal.SIGINT)
        return True


def get_plugin():
    return Xserver

