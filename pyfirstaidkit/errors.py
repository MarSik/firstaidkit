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


class InvalidFlowStateException(Exception):
    def __init__(self, flow):
        self.message="There appears to be an inconsistency with the %s " \
                "varialbe. " % flow
    def __str__(self):
        return self.message

class InvalidFlowNameException(Exception):
    def __init__(self, name):
        self.message="There are no flows by the name of %s" % name
    def __str__(self):
        return self.message

class InvalidPluginNameException(Exception):
    def __init__(self, name):
        self.message="There are no flows by the name of %s" % name
    def __str__(self):
        return self.message

class GeneralPluginException(Exception):
    """General exception

    This exception should be used for all exceptions that come from the
    plugins and have no specific exception class yet.
    """
    def __init__(self, plugin, message):
        self.message="There was an exception in plugin %s with message %s"% \
                (plugin,message)
    def __str__(self):
        return self.message
