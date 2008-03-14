# File name: issue.py
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

class Issue(object):
    name = "Parent issue"
    description = "This happens when you use the wrong object in the issues list"

    def __init__(self, plugin):
        self._plugin = plugin
        self.reset()

    def detect(self):
        """Detect if this situation happened and store some information about it, so we can fix it
Return values:
    True - detection OK
    False - detection Failed
    None - no result, please continue with the operation"""

        #if the issue was fixed. the detection is worthless
        #if it was detected, no need to do the detection again
        if self._detected or self._fixed:
            return not self._fixed and self._detected

        return None #no error, please do the detection (so the child-class knows to actually do something)

    def fix(self):
        """Fix the situation if needed
Return values:
    True - fix OK
    False - fix Failed
    None - no result, please continue with the operation"""

        #if the issue was fixed. no need to do the fix again
        #if it was not detected, the detection si needed too
        if not self._detected or self._fixed:
            return self._fixed and self._detected

        return None #no fix error, please do the fix (so the child-class knows to actually do something)

    def happened(self):
        """Get the 'issue happened' flag.
Return values:
    True - YES it happened
    False - NO, it is OK
    None - I don't know, there was an error"""
        #if the issue was fixed or not detected, the detection si needed
        if not self._detected or self._fixed:
            return None
        else:
            return self._happened
        

    def reset(self):
        """Reset the object's state"""
        self._detected = False
        self._happened = False
        self._fixed = False

    def __str__(self):
        s = []
        if self._fixed:
            s.append("Fixed")
        elif self._happened and self._detected:
            s.append("Detected")
        elif self._detected:
            s.append("No problem with")
        else:
            s.append("Waiting for check on")

        s.append(self.name)

        if self._happened and self._detected:
            s.append("--")
            s.append(self.description)

        return " ".join(s)

    def str(self):
        return self.__str__()

