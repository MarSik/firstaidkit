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
import signal
import _undelpart

class UndeletePartition(Plugin):
    """Plugin to detect and correct deleted partitions from system disks.

    Uses parted libriary to search for partitions that are not included in
    the partition table of a disk.  If it is possible, this plugin will put
    the partition back into the parition table so it is visible to the 
    system again.
    """

    flows = Flow.init(Plugin)
    # We have not resotre in the noBackup flow because we have no information to restore with.
    flows["noBackup"] = Flow({
                    Plugin.initial: {Return: "prepare"},
                    "prepare"     : {ReturnSuccess: "diagnose"},
                    "diagnose"    : {ReturnSuccess: "clean", ReturnFailure: "fix"},
                    "fix"         : {ReturnSuccess: "clean", ReturnFailure: "clean"},
                    "clean"       : {ReturnSuccess: Plugin.final}
                    }, description="This flow skips the backup test.  Use with care.")

    name = "Undelete Partitions"
    version = "0.1.0"
    author = "Joel Andres Granados"
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        # The reporting object

        # Dictionary that will hold the partitions that are not included in the
        # partition table of a certain disk and can be recovered. It will also
        # house the initial partition table and the partition table that is a 
        # result of running the fix.  The structure is:
        # slef.disks={diskname: [ [recoverables], initialPT, finalPT ], .... }
        self.disks = {}

    def prepare(self):
        # For now there is no real action in the prepare task.
        self._result=ReturnSuccess
        self._reporting.info("Prepare task", UndeletePartition.name)

    def diagnose(self):
        self._reporting.info("Beginning Diagnose...", UndeletePartition.name)
        self.disks = _undelpart.getDiskList()
        self._reporting.info("%s: Disks present in the system %s" %
                (UndeletePartition.name, self.disks.keys()), self )
        # When we find a rescuable partition we change this to true.
        rescuablePresent = False
        for key, value in self.disks.iteritems():
            self.disks[key] = [ _undelpart.getRescuable(key), _undelpart.getPartitionTable(key), [] ]
            if len(self.disks[key][0]) > 0:
                self._reporting.info("Found %s recoverable partitions in %s disk." %
                        (self.disks[key], key), UndeletePartition.name )
                rescuablePresent = True
        if not rescuablePresent:
            self._result = ReturnSuccess
            self._reporting.info("Did not find any partitions that need rescueing.",
                    UndeletePartition.name)
        else:
            self._result = ReturnFailure

    def backup(self):
        self._reporting.info("Backing up partition table." , UndeletePartition.name)
        # We actually already have the backup of the partition table in the self.disks dict.
        # Lets check anyway.
        backupSane = True
        for disk, members in self.disks.iteritems():
            if members[1] == None or len(members[1]) <= 0:
                # We don't really have the partition table backup.
                self._reporting.info("%s: Couldn't backup the partition table for %s."%
                        (UndeletePartition.name, disk), self)
                self._reporting.info("To force the recovery of this disk without the backup " \
                    "please run the flow named noBackup from this plugin.", UndeletePartition.name)
                backupSane = False
                self._result = ReturnFailure

        if backupSane:
            self._result = ReturnSuccess

    def fix(self):
        self._reporting.info("Lets see if I can fix this... Starting fix task.", UndeletePartition.name )
        self._result = ReturnSuccess
        try:
            for disk, members in self.disks.iteritems():
                if len(members[0]) > 0:
                    self._reporting.info("Recovering %s from %s."% (members[0], disk),UndeletePartition.name)
                    recoveredDisks = _undelpart.rescue(disk, members[0])
                    self._reporting.info("Recovered %s of %s from %s partitions."%(recoveredDisks,
                        members[0], disk),UndeletePartition.name )
                    self.disks[disk][2] = _undelpart.getPartitionTable(disk)
                elif len(members[0]) ==  0:
                    self._reporting.info("Nothing to recover on disk %s."%disk,UndeletePartition.name )
                else:
                    self_result = ReturnFailure
                    break
        except KeyboardInterrupt, e:
            self._reporting.info("Received a user interruption... Moving to Restore task.",UndeletePartition.name)
            # The user might want to keep on pushing ctrl-c, lets lock the SIGINT signal.
            signal.signal(signal.SIGINT, keyboaordInterruptHandler)
            self._reporting.info("Please wait until the original partition table is recovered.",UndeletePartition.name)
            self._result = ReturnFailure

    def restore(self):
        self._reporting.info("Starting Restoring task." , UndeletePartition.name)
        # All the disks that have a new partition are ok,  Lets make sure that we
        # restore all of the other disks.
        for disk, members in self.disks.iteritems():
            if len(members[2]) == 0:
                self._reporting.info("Restoring %s partition table."%disk,UndeletePartition.name)
                _undelpart.setPartitionTable(disk, members[1])
            else:
                self._reporting.info("Disk %s does not need restore."%disk, UndeletePartition.name)

        # Return the signal to its previous state.
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self._result = ReturnSuccess

    def clean(self):
        self._reporting.info("Cleanning...",UndeletePartition.name)
        self._result = ReturnSuccess

def keyboardInterruptHandler(signum, frame):
    pass
