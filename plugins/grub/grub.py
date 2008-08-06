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
from pyfirstaidkit.issue import SimpleIssue
from pyfirstaidkit import Config
from pyfirstaidkit.errors import *

from grubUtils import Dname
import grubUtils

import os

class Grub(Plugin):
    """Plugin to detect and fix grub failure."""
    flows = Flow.init(Plugin)
    name = "Grub"
    version = "0.0.1"
    author = "Joel Andres Granados"

    @classmethod
    def getDeps(cls):
        return set(["root", "experimental", "filesystem"])

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)

        # The key is a dev name, the value is a list of partitions in drive.
        self.devices = {}

        # The partitions where the grub directory and all the necessary files
        # found.
        self.grub_dir_parts = []

        # The partitions where the grub binary is found in the first 446 bytes.
        self.grub_bin_parts = []

        # The devs where the grub binary is found in the first 446 bytes.
        self.grub_bin_devs = []

        # Initialize our list of related issues.
        self.issue_grub_dir = SimpleIssue(self.name, "Missing grub dir or " \
                "dir files.")
        self.issue_grub_image = SimpleIssue(self.name, "Bad grub stage1 image.")

        # Initialize the backup space.
        self.backupSpace = self._backups.getBackup(str(self))

    def prepare(self):
        self._reporting.info("Initializing the search for all the grub " \
                "related elements.", origin = self)

        try:
            # We end up with a structure where the keys are the drive names.
            self.devices = grubUtils.get_all_devs()

            self._reporting.info("Searching for grub related files in the " \
                    "system storage devices.", origin = self)
            # We must search in all the possible partitions for the grub files:
            # stage1, stage1.5, stage2....  When we find these directories we
            # will be able to install grub from there.  And the vmliuz (kernel
            # image), initrd.img, the grub.conf is probably in these places as
            # well.
            for (dev, parts) in self.devices.iteritems():
                for part in parts:
                    try:
                        if grubUtils.grub_dir_in_partition(part):
                            self._reporting.info("Found grub dir in %s " \
                                    "partition." % part.path(), origin = self)
                            self.grub_dir_parts.append(part)
                    except Exception, e:
                        # If something happened while checking the partition 
                        # it will not be taken into account.
                        self._reporting.error("There was an error while " \
                                "searching partition %s. Error: %s." % \
                                (part.path(), e) ,origin = self)

            self._reporting.info("Searching for the grub stage1 image.", \
                    origin = self)
            # We must search in all the possible partitions and devices for the
            # grub binary.
            for (dev, parts) in self.devices.iteritems():

                # We look for grub in the device
                try:
                    if grubUtils.grub_bin_in_dev(Dname(dev)):
                        self._reporting.info("Found grub stage1 image in %s " \
                                "device" % Dname.asPath(dev), origin = self)
                        self.grub_bin_devs.append(grubUtils.Dname(dev))

                except Exception, e:
                    self._reporting.error("There was an error searching for " \
                            "the grub images in device %s. Error %s." % \
                            (Dname.asPath(dev), e), origin = self)

                # No we look for the grub in the partitions.
                for part in parts:
                    try:
                        if grubUtils.grub_bin_in_part(Dname(part)):
                            self._reporting.info("Found grub stage1 image " \
                                    "in %s partition" % Dname.asPath(dev), \
                                    origin = self)
                            self.grub_bin_parts.append(Dname(part))

                    except Exception, e:
                        self._reporting.error("There was an error searching " \
                                "for grub images in partition %s. Error %s." % \
                                (Dname.asPath(part), e), origin = self)

            self._result = ReturnSuccess
        except Exception, e:
            self._reporting.error("An error has ocurred while searching for " \
                    "grubs elements.  Error: %s" % e, origin = self)
            self._result = ReturnFailure

    def diagnose(self):
        # FIXME ATM we will not take care of the cases that are missing some
        # stuff from the grub directory, like images and conffile.
        #
        # The diagnose is tricky because we have no way of knowing (yet) if
        # the images found in the devices actually map correctly to the stuff
        # that we found on the directories.  This means that we will allways
        # reinstall grub in the mbr (the changes will be revertable so its
        # not that bad) unless we don't find any directory.  If no dir is
        # found, then we fail (fail in this case means postponing the decision
        # until the fix step to actually ReturnFailure)
        self._reporting.info("Diagnosing the current state of grub.",
                origin = self)
        if len(self.grub_dir_parts) < 0:
            self._reporting.error("No grub directories where found.",
                    origin = self)

            self.issue_grub_dir.set(checked = True, happened = True,
                    reporting = self._reporting, origin = self)
            self.issue_grub_image.set(checked = False,
                    reporting = self._reporting, origin = self)

            self._result = ReturnFailure
            return
        self.issue_grub_dir.set(checked = True, happened = False,
                reporting = self._reporting, origin = self)

        # At this point we know that we are going to reinstall the grub.  We
        # inform the user about the state of the stage1 in the partitions but
        # we do nothing else with this information.
        if len(self.grub_bin_parts) == 0:
            self._reporting.info("No valid grub image was found in any " \
                    "partition in the system.", origin = self)
        if len(self.grub_bin_devs) == 0:
            self._reporting.info("No valid grub image was found in any " \
                    "device in the system.", origin = self)

        # Only if there is no recognizable image do we consider it to be
        # an issue.
        if len(self.grub_bin_parts) == 0 and len(self.grub_bin_devs) == 0:
            self.issue_grub_image.set(checked = True, happened = True,
                    reporting = self._reporting, origin = self)
        else:
            self.issue_grub_image.set(checked = True, happened = False,
                    reporting = self._reporting, origin = self)

        self._result = ReturnFailure


    def  backup(self):
        # The grub process is related to the 446 firsta bytes of the partitions
        # of the device.  This means we must backup all the beginings fo the
        # partitions and devices that we will possibly modify.

        # Since we are going to install the stage1 grub image in all the
        # devices, we will backup all of them.
        self._reporting.info("Going to backup all the first 446 bytes of " \
                "all storage devices in the system.", origin = self)
        for (device, partitions) in self.devices.iteritems():
            fd = os.open(Dname.asPath(device), os.O_RDONLY)
            first446btemp = os.read(fd, 446)
            os.close(fd)
            self.backupSpace.backupValue(first446btemp, Dname.asName(device))
        self._result = ReturnSuccess


    def fix(self):
        # We ar to fail if there is no dirs.
        if len(self.grub_dir_parts) == 0:
            self._reporting.error("No grub directories where found... exiting.",
                    origin = self)
            self.issue_grub_image.set(fixed = False, \
                    reporting = self._reporting, origin = self)
            self.issue_grub_image.set(fixed = False, \
                    reporting = self._reporting, origin = self)

            self._result = ReturnFailure
            return

        # Choose and prepare one root in the system.
        # FIXME: extend the root concept so it can handle varous roots in a
        #        system.  For now we just select the first and hope it has
        #        everything.

        # Install the grub in all devs pointing at the special root part.
        for (drive, partitions) in self.devices.iteritems():
            self._reporting.info("Trying to install grub on drive %s, " \
                    "pointing to grub directory in %s."%(Dname.asName(drive), \
                    self.grub_dir_parts[0].path()), origin = self)
            try:
                grubUtils.install_grub(self.grub_dir_parts[0], Dname(drive))
            except Exception, e:
                self._reporting.error("Grub installation on drive %s, " \
                        "pointing to grub directory in %s has failed." % \
                        (Dname.asName(drive), self.grub_dir_parts[0].path()), \
                        origin = self)
                # If one installation fails its safer to just restore
                # everything
                self._result = ReturnFailure
                return

        self._reporting.info("Grub has successfully installed in all the " \
                "devices.", origin = self)
        self._result = ReturnSuccess

    def restore(self):
        self._reporting.info("Starting the restore process....", level=PLUGIN, \
                origin = self)
        for (device, partitions) in self.devices.iteritems():
            self._reporting.info("Restoring data from device %s" % \
                    Dname.asPath(device), origin = self)
            try:
                # Get the value from the backup space
                first446btemp = self.backupSpace.restoreValue(
                        Dname.asName(device))

                # Copy the value over the existing stuff.
                fd = os.open(Dname.asPath(device), os.O_WRONLY)
                os.write(fd, first446btemp)
                os.close(fd)
            except Exception, e:
                self._reporting.info("An error has occurred while trying to " \
                        "recover %s device." % Dname.asName(device), \
                        origin = self)
                continue
        self._result = ReturnSuccess

    def clean(self):
        self._result = ReturnSuccess