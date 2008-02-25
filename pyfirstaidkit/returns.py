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

#
# The Favorable and Unfavorable return classes are implemented to give a more
# intuitive/logical approach to the default flow.  The value given to the return
# of each task depends on the objectives of the task and of the place where the
# task is situated inside the totality of the flow.
# Examples:
# 1. If the plugin is in the diagnose flow and if found nothing wrong with the
#    system it is analysing, the return value would be Favorable.
# 2. If the plugin is in backup and the backup action is unseccessfull, the
#    proper return value would be Unfavorable.  In this Favorable would mean that
#    the backup was successfull and the plugin can move toward the fix task.
# 3. If the plugin is in fix stage and the problem was not fixed, the return
#    value should be ResutltNotOk.  On the other hand if the fix has been done
#    the return value should be Favorable.
# Remember that the actual values of the classes is not checked,  what is checked
# is that the return value be of a specific class.
#

class ReturnFavorable(ReturnValue):
    """Use whenever the result of a task is positive, expected or offers the
    least resistence.

    """
    def __init__(self):
        pass

class ReturnUnfavorable(ReturnValue):
    """Used whenever the result of a task is not possitive, not expected or
    offerst the most resistence.
    """
    def __init__(self):
        pass
