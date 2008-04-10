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

Logger = logging.getLogger("firstaidkit")

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
QUESTION = 999 #type of message which contains respond-to field
END = 1000 #End of operations, final message

class Origin(object):
    """Class which defines mandatory interface for origin, when using the reporting system"""
    name = "Origin:Unknown"

    def __init__(self, name):
        self.name = name

class Reports(object):
    """Instances of this class are used as reporting mechanism by which the
    plugins can comminucate back to whatever frontend we are using.

    Message has four parts:
    origin - who sent the message (instance of the plugin, Pluginsystem, ...)
    level - which level of First Aid Kit sent the message (PLUGIN, TASKER, ..)
    action - what action does the message describe
                (INFO, ALERT, PROGRESS, START, STOP, DATA, END)
    importance - how is that message important (debug, info, error, ...)
                 this must be number, possibly the same as in logging module
    message - the message itself
              for INFO and ALERT semantics, this is an arbitrary  text
              for PROGRESS, this is  (x,y) pair denoting progress
                (on step x from y steps) or None to hide the progress
              for START and STOP, there is no mandatory message and the
                importance specifies the level
    reply - the instance of Queue.Queue, which should receive the replies
    title - title of the message
    """

    def __init__(self, maxsize=-1):
        self._queue = Queue.Queue(maxsize = maxsize)
        self._mailboxes = []

    def put(self, message, level, origin, action, importance = logging.INFO, reply = None, title = "", destination = None):
        if destination is None:
            destination = self._queue
        return destination.put({"level": level, "origin": origin, "action": action, "importance": importance, "message": message, "reply": reply, "title": title})

    def get(self, mailbox = None, *args, **kwargs):
        if mailbox is None:
            mailbox = self._queue
        return mailbox.get(*args, **kwargs)

    def openMailbox(self, maxsize=-1):
        """Allocate new mailbox for replies"""
        mb = Queue.Queue(maxsize = maxsize)
        self._mailboxes.append(mb)
        return mb

    def closeMailbox(self, mb):
        """Close mailbox when not needed anymore"""
        self._mailboxes.remove(mb)

    #There will be helper methods inspired by logging module
    def end(self):
        return self.put(None, FIRSTAIDKIT, None, END, importance = 1000)

    def error(self, message, level, origin, action = INFO):
        Logger.error(origin.name+": "+message)
        return self.put(message, level, origin, action, importance = logging.ERROR)

    def start(self, level, origin, message = ""):
        return self.put(message, level, origin, START, importance = logging.DEBUG)
    def stop(self, level, origin, message = ""):
        return self.put(message, level, origin, STOP, importance = logging.DEBUG)

    def progress(self, position, maximum, level, origin, importance = logging.INFO):
        return self.put((position, maximum), level, origin, PROGRESS, importance = importance)

    def info(self, message, level, origin, importance = logging.INFO):
        Logger.info(origin.name+": "+message)
        return self.put(message, level, origin, INFO, importance = importance)
    def debug(self, message, level, origin, importance = logging.DEBUG):
        Logger.debug(origin.name+": "+message)
        return self.put(message, level, origin, INFO, importance = importance)

    def tree(self, message, level, origin, importance = logging.INFO, title = ""):
        return self.put(message, level, origin, TREE, importance = importance, title = title)
    def table(self, message, level, origin, importance = logging.INFO, title = ""):
        return self.put(message, level, origin, TABLE, importance = importance, title = title)

    def alert(self, message, level, origin, importance = logging.WARNING):
        return self.put(message, level, origin, ALERT, importance = importance)
    def exception(self, message, level, origin, importance = logging.ERROR):
        Logger.error(origin.name+": "+message)
        return self.put(message, level, origin, EXCEPTION, importance = importance)

