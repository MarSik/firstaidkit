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


#
# These classes expressed here are to be the keys in the flow dictionary.
# In most default cases the values are unimportant.  They are placed there
# for printing or other purposes.

class ReturnValue:
    """Its just a parent class for any Return class that might be create.

    The parent has no value.
    """
    def __init__(self):
        pass

class ReturnValueTrue(ReturnValue):
    def __init__(self):
        self.value = True

class ReturnValueFalse(ReturnValue):
    def __init__(self):
        self.value = False

class ReturnValueNone(ReturnValue):
    def __init__(self):
        self.value = None
