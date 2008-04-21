# File name: main.py
# Date:      2008/04/21
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

import gtk
import gtk.glade
import gobject #we need gobject.idle_add
import copy
import logging
from pyfirstaidkit import reporting
import pprint

class CallbacksMainWindow(object):
    def __init__(self, dialog, pluginsystem, flags, reporting):
        self._dialog = dialog
        self._pluginsystem = pluginsystem
        self._flags = flags
        self._reporting = reporting

    #menu callbacks
    def on_mainmenu_open_activate(self, widget, *args):
        print "on_mainmenu_open_activate"
        return True

    def on_mainmenu_save_activate(self, widget, *args):
        print "on_mainmenu_save_activate"
        return True

    def on_mainmenu_save_as_activate(self, widget, *args):
        return True

    def on_quit_activate(self, widget, *args):
        print "on_quit_activate"
        if True: #XXX destroy right now, but warn, in final code we have to wait until plugin finishes
            print "!!! You should wait until the running plugin finishes!!"
            self._dialog.destroy()
        return True

    def on_destroy(self, widget, *args):
        gtk.main_quit()

    def on_mainmenu_about_activate(self, widget, *args):
        print "on_mainmenu_about_activate"
        return True

    #simple mode callbacks
    def on_b_StartSimple_activate(self, widget, *args):
        print "on_b_StartSimple_activate"
        return True

    #advanced mode callbacks
    def on_b_StartAdvanced_activate(self, widget, *args):
        print "on_b_StartAdvanced_activate"
        return True

    #expert mode callbacks
    def on_b_FlagsExpert_activate(self, widget, *args):
        print "on_b_FlagsExpert_activate"
        FlagList(self._flags)
        return True

    def on_b_InfoExpert_activate(self, widget, *args):
        print "on_b_InfoExpert_activate"
        return True

    def on_b_StartExpert_activate(self, widget, *args):
        print "on_b_StartExpert_activate"
        return True

    #results callbacks
    def on_b_ResetResults_activate(self, widget, *args):
        print "on_b_ResetResults_activate"
        return True

    def on_b_StopResults_activate(self, widget, *args):
        print "on_b_StopResults_activate"
        return True

class CallbacksFlagList(object):
    def __init__(self, dialog, flags):
        self._dialog = dialog
        self._flags = flags
        self._working = copy.copy(self._flags)

    def on_b_AddFlag_activate(self, widget, *args):
        print "on_b_AddFlag_activate"
        return True

    def on_b_OK_activate(self, widget, *args):
        print "on_b_OK_activate"
        self._dialog.destroy()
        return True

    def on_b_Cancel_activate(self, widget, *args):
        print "on_b_Cancel_activate"
        self._dialog.destroy()
        return True

    def on_b_Flag_activate(self, widget, *args):
        print "on_b_Flag_activate"
        return True

class MainWindow(object):
    def __init__(self, pluginsystem, flags, reporting, importance = logging.INFO):
        self._importance = importance
        self._glade = gtk.glade.XML("frontend/firstaidkit.glade", "MainWindow")
        self._window = self._glade.get_widget("MainWindow")
        self._cb = CallbacksMainWindow(self._window, pluginsystem, flags, reporting)
        self._glade.signal_autoconnect(self._cb)
        self._window.connect("destroy", self._cb.on_destroy)

        self.status_text = self._glade.get_widget("status_text")
        self.status_progress = self._glade.get_widget("status_progress")

    def update(self, message):
        """Read the reporting system message and schedule a call to update stuff in the gui using gobject.idle_add"""
        if message["action"]==reporting.END:
            gobject.idle_add(self._window.destroy)
        elif message["action"]==reporting.QUESTION:
            print "FIXME: Questions not implemented yet"
        elif message["action"]==reporting.START:
            if self._importance<=message["importance"]:
                ctx = self.status_text.get_context_id(message["origin"].name)
                gobject.idle_add(self.status_text.push, ctx, "START: %s (%s)" % (message["origin"].name, message["message"]))
        elif message["action"]==reporting.STOP:
            if self._importance<=message["importance"]:
                ctx = self.status_text.get_context_id(message["origin"].name)
                gobject.idle_add(self.status_text.push, ctx, "STOP: %s (%s)" % (message["origin"].name, message["message"]))
        elif message["action"]==reporting.PROGRESS:
            if self._importance<=message["importance"]:
                if message["message"] is None:
                  gobject.idle_add(self.status_progress.hide)
                else:
                  gobject.idle_add(self.status_progress.set_text, "%d/%d - %s" % (message["message"][0], message["message"][1], message["origin"].name))
                  gobject.idle_add(self.status_progress.set_fraction, float(message["message"][0])/message["message"][1])
                  gobject.idle_add(self.status_progress.show)
        elif message["action"]==reporting.INFO:
            if self._importance<=message["importance"]:
                ctx = self.status_text.get_context_id(message["origin"].name)
                gobject.idle_add(self.status_text.push, ctx, "INFO: %s (%s)" % (message["message"], message["origin"].name))
        elif message["action"]==reporting.ALERT:
            if self._importance<=message["importance"]:
                ctx = self.status_text.get_context_id(message["origin"].name)
                gobject.idle_add(self.status_text.push, ctx, "ALERT: %s (%s)" % (message["message"], message["origin"].name))
        elif message["action"]==reporting.EXCEPTION:
            ctx = self.status_text.get_context_id(message["origin"].name)
            gobject.idle_add(self.status_text.push, ctx, "EXCEPTION: %s (%s)" % (message["message"], message["origin"].name))
        elif message["action"]==reporting.TABLE:
            if self._importance<=message["importance"]:
                print "TABLE %s FROM %s" % (message["title"], message["origin"].name,)
                pprint.pprint(message["message"])
        elif message["action"]==reporting.TREE:
            if self._importance<=message["importance"]:
                print "TREE %s FROM %s" % (message["title"], message["origin"].name,)
                pprint.pprint(message["message"])
        else:
            print "FIXME: Unknown message action %d!!" % (message["action"],)
            print message

    def run(self):
        gtk.main()

class FlagList(object):
    def __init__(self, flags):
        self._glade = gtk.glade.XML("frontend/firstaidkit.glade", "FlagList")
        self._window = self._glade.get_widget("FlagList")
        self._window.set_modal(True)
        self._cb = CallbacksFlagList(self._window, flags)
        self._glade.signal_autoconnect(self._cb)

if __name__=="__main__":
    w = MainWindow(None, None, None)
    #w.run()

