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

def spawnvch(executable, params, chroot): #returns errorcode
    """Simpliest chroot modification of spawn
 executable - path to binary to execute (in chroot!)
 params - it's parameters
 chroot - directory to chroot to

Returns the error code returned by process"""

    pid = os.fork()
    if pid==0: #child
        os.chroot(chroot)
        os.execv(executable, params)
        sys.exit(1)
    else:
        res = os.waitpid(pid, 0)
        return os.WEXITSTATUS(res)

