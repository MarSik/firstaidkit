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

import Queue
import logging

#semantics values
#first the "task" levels for START and STOP
FIRSTAIDKIT = 100
TASKER = 90
PLUGINSYSTEM = 80
PLUGIN = 70
FLOW = 60
TASK = 50

#semantics
START = 0
STOP = 1
PROGRESS = 2
INFO = 3
ALERT = 4
EXCEPTION = 5
TABLE = 6 #types for arbitrary table-like organized iterables
TREE = 7  #nested iterables organized as tree
END = 1000 #End of operations, final message

class Reports(object):
    """Instances of this class are used as reporting mechanism by which the
    plugins can comminucate back to whatever frontend we are using.

    Message has four parts:
    origin - who sent the message (name of the plugin, Pluginsystem, ...)
    semantics - what action does the message describe
                (INFO, ALERT, PROGRESS, START, STOP, DATA, END)
    importance - how is that message important (debug, info, error, ...)
                 this must be number, possibly the same as in logging module
    message - the message itself
              for INFO and ALERT semantics, this is an arbitrary  text
              for PROGRESS, this is  (x,y) pair denoting progress
                (on step x from y steps) or None to hide the progress
              for START and STOP, there is no mandatory message and the
                importance specifies the level
    """

    def __init__(self, maxsize=-1):
        self._queue = Queue.Queue(maxsize = maxsize)

    def put(self, message, origin, semantics, importance = logging.INFO):
        return self._queue.put((origin, semantics, importance, message))

    def get(self, *args, **kwargs):
        return self._queue.get(*args, **kwargs)


    #There will be helper methods inspired by logging module
    def end(self):
        return self.put(None, None, END, importance = 1000)

    def error(self, message, origin, semantics):
        return self.put(message, origin, semantics, importance = logging.ERROR)

    def start(self, message, origin, what = TASK):
        return self.put(message, origin, START, importance = what)
    def stop(self, message, origin, what = TASK):
        return self.put(message, origin, START, importance = what)

    def progress(self, position, maximum, origin, importance = logging.INFO):
        return self.put((position, maximum), origin, PROGRESS, importance = importance)
    def info(self, message, origin, importance = logging.INFO):
        return self.put(message, origin, INFO, importance = importance)


    def tree(self, message, origin, importance = logging.INFO):
        return self.put(message, origin, TREE, importance = importance)
    def table(self, message, origin, importance = logging.INFO):
        return self.put(message, origin, TABLE, importance = importance)

    def alert(self, message, origin, importance = logging.WARNING):
        return self.put(message, origin, ALERT, importance = importance)
    def exception(self, message, origin, importance = logging.ERROR):
        return self.put(message, origin, EXCEPTION, importance = importance)

