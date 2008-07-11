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

import os
import sys
import subprocess
from backup import *
from errors import *

def chroot_func(dir):
    def do_chroot():
        return os.chroot(dir)

    if os.path.abspath(dir)=="/":
        return lambda: True
    else:
        return do_chroot

def spawnvch(executable, args, chroot, env = None):
    """Use Popen to launch program in chroot
 executable - path to binary to execute (in chroot!)
 args - it's parameters
 chroot - directory to chroot to

Returns the subprocess.Popen object"""

    return subprocess.Popen(executable = executable, args = args, preexec_fn = chroot_func(chroot), env = env,
            stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)



