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
import thread
import weakref

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
ISSUE = 8  #New issue object was created or changed
QUESTION = 999 #type of message which contains respond-to field
END = 1000 #End of operations, final message

class Origin(object):
    """Class which defines mandatory interface for origin,
    when using the reporting system"""
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

    def __init__(self, maxsize=-1, round = False, parent  = None, name = None):
        """round - is this a round buffer?
        maxsize - size of the buffer"""
        self._queue = Queue.Queue(maxsize = maxsize)
        self._queue_lock = thread.allocate_lock()
        self._round = round
        self._mailboxes = []
        self._notify = []
        self._notify_all = []
        self._parent  = parent
        if not name:
            self._name = "Reporting"
        else:
            self._name = name


    def notify(self, cb, *args, **kwargs):
        """When putting anything new into the Queue, run notifications
        callbacks. Usefull for Gui and single-thread reporting.
        The notification function has parameters: reporting object,
        message recorded to the queue, any parameters provided
        when registering"""
        return self._notify.append((cb, args, kwargs))
    
    def notify_all(self, cb, *args, **kwargs):
        """When putting anything new into the Queue or mailboxes
        belonging to this Reporting object, run notifications
        callbacks. Usefull for logging.
        The notification function has parameters: reporting object,
        message recorded to the queue, any parameters provided
        when registering"""
        return self._notify_all.append((cb, args, kwargs))

    def put(self, message, origin, level, action, importance = logging.INFO,
            reply = None, inreplyto = None, title = "", destination = None):
        """destination hold reference to another Reporting object"""

        if destination is not None:
            return destination.put(message = message, origin = origin, level = level, action = action, importance = importance, reply = reply, title = title, inreplyto = inreplyto)
        
        data = {"level": level, "origin": origin, "action": action,
                "importance": importance, "message": message,
                "reply": reply, "inreplyto": inreplyto, "title": title}

        destination = self._queue
        try:
            self._queue_lock.acquire()
            ret=destination.put(data, block = False)
        except Queue.Full, e:
            if not self._round:
                raise
            #Queue is full and it is a round buffer.. remove the oldest item
            #and use the free space to put the new item
            destination.get()
            ret=destination.put(data)
        finally:
            self._queue_lock.release()

        #call all the notify callbacks
        for func, args, kwargs in self._notify:
            func(self, data, *args, **kwargs)
        
        #call all the notify-all callbacks
        self.notifyAll(self, data)

        return ret

    def get(self, mailbox = None, *args, **kwargs):
        if mailbox is not None:
            return mailbox.get(*args, **kwargs)
        
        try:
            self._queue_lock.acquire()
            ret = self._queue.get(*args, **kwargs)
        finally:
            self._queue_lock.release()

        return ret

    def openMailbox(self, maxsize=-1):
        """Allocate new mailbox for replies"""

        mb = None
        try:
            self._queue_lock.acquire()
            mb = Reports(maxsize = maxsize, parent = self)
            self._mailboxes.append(mb)
        finally:
            self._queue_lock.release()

        return mb

    def removeMailbox(self, mb):
        """Remove mailbox from the mailbox list"""
        try:
            self._queue_lock.acquire()
            self._mailboxes.remove(mb)
            mb._parent = None
        finally:
            self._queue_lock.release()

    def closeMailbox(self):
        """Close mailbox when not needed anymore"""
        self._parent.removeMailbox(self)

    def notifyAll(self, data, sender=None):
        if sender is None:
            sender = self

        #call all the notify-all callbacks
        for func, args, kwargs in self._notify_all:
            func(sender, data, *args, **kwargs)

        if self._parent:
            self._parent.notifyAll(data, sender)

    #There will be helper methods inspired by logging module
    def end(self, level = PLUGIN):
        return self.put(None, level, None, END, importance = 1000)

    def error(self, message, origin, inreplyto = None, level = PLUGIN, action = INFO):
        Logger.error(origin.name+": "+message)
        return self.put(message, origin, level, action,
                importance = logging.ERROR, inreplyto = inreplyto)

    def start(self, origin, inreplyto = None, level = PLUGIN, message = ""):
        return self.put(message, origin, level, START,
                importance = logging.DEBUG, inreplyto = inreplyto)
    def stop(self, origin, inreplyto = None, level = PLUGIN, message = ""):
        return self.put(message, origin, level, STOP,
                importance = logging.DEBUG, inreplyto = inreplyto)

    def progress(self, position, maximum, origin, inreplyto = None, level = PLUGIN,
            importance = logging.INFO):
        return self.put((position, maximum), origin, level, PROGRESS,
                importance = importance, inreplyto = inreplyto)

    def issue(self, issue, origin, inreplyto = None, level = PLUGIN, importance = logging.INFO):
        Logger.debug(origin.name+": issue changed state to "+str(issue))
        return self.put(issue, origin, level, ISSUE, importance = importance, inreplyto = inreplyto)

    def info(self, message, origin, inreplyto = None, level = PLUGIN, importance = logging.INFO):
        Logger.info(origin.name+": "+message)
        return self.put(message, origin, level, INFO, importance = importance, inreplyto = inreplyto)

    def debug(self, message, origin, inreplyto = None, level = PLUGIN, importance = logging.DEBUG):
        Logger.debug(origin.name+": "+message)
        return self.put(message, origin, level, INFO, importance = importance, inreplyto = inreplyto)

    def tree(self, message, origin, inreplyto = None, level = PLUGIN, importance = logging.INFO,
            title = ""):
        return self.put(message, origin, level, TREE, importance = importance,
                title = title, inreplyto = inreplyto)

    def table(self, message, origin, inreplyto = None, level = PLUGIN, importance = logging.INFO,
            title = ""):
        return self.put(message, origin, level, TABLE,
                importance = importance, title = title, inreplyto = inreplyto)

    def alert(self, message, origin, inreplyto = None, level = PLUGIN, importance = logging.WARNING):
        return self.put(message, origin, level, ALERT, importance = importance, inreplyto = inreplyto)

    def exception(self, message, origin, inreplyto = None, level = PLUGIN, importance = logging.ERROR):
        Logger.error(origin.name+": "+message)
        return self.put(message, origin, level, EXCEPTION,
                importance = importance, inreplyto = inreplyto)

