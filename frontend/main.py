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
import os.path
import thread

class CallbacksMainWindow(object):
    def __init__(self, dialog, cfg, tasker, glade):
        self._dialog = dialog
        self._tasker = tasker
        self._glade = glade
        self._cfg = cfg
        self._running_lock = thread.allocate_lock()

    def execute(self):
        if not self._running_lock.acquire(0):
            return

        def worker():
            self._cfg.lock()
            self._tasker.run()
            self._cfg.unlock()
            self._running_lock.release()

        thread.start_new_thread(worker, ())

    #menu callbacks
    def on_mainmenu_open_activate(self, widget, *args):
        print "on_mainmenu_open_activate"
        d = gtk.FileChooserDialog(title="Load the configuration file", parent=self._dialog, action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        print d.run()
        d.destroy()
        return True

    def on_mainmenu_save_activate(self, widget, *args):
        print "on_mainmenu_save_activate"
        d = gtk.FileChooserDialog(title="Save the configuration file", parent=self._dialog, action=gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        ret=d.run()

        if ret==gtk.RESPONSE_ACCEPT:
            try:
                filename = d.get_filename()
                fd = open(filename, "w")
                self._cfg.write(fd)
            except IOError, e:
                pass

        d.destroy()
        return True

    def on_quit_activate(self, widget, *args):
        print "on_quit_activate"
        if True: #XXX destroy right now, but warn, in final code we have to wait until plugin finishes
            print "!!! You should wait until the running plugin finishes!!"
            self._dialog.destroy()
            del self._tasker
            del self._cfg
        return True

    def on_destroy(self, widget, *args):
        print "on_destroy"
        gtk.main_quit()

    def on_mainmenu_about_activate(self, widget, *args):
        print "on_mainmenu_about_activate"
        return True

    #simple mode callbacks
    def on_b_StartSimple_activate(self, widget, *args):
        print "on_b_StartSimple_activate"

        self.execute()
        return True

    #advanced mode callbacks
    def on_b_StartAdvanced_activate(self, widget, *args):
        print "on_b_StartAdvanced_activate"
        
        self.execute()
        return True

    #expert mode callbacks
    def on_b_FlagsExpert_activate(self, widget, *args):
        print "on_b_FlagsExpert_activate"
        FlagList(self._cfg, self._tasker.flags(), dir = os.path.dirname(self._glade.relative_file(".")))
        return True

    def on_b_InfoExpert_activate(self, widget, *args):
        print "on_b_InfoExpert_activate"
        return True

    def on_b_StartExpert_activate(self, widget, *args):
        print "on_b_StartExpert_activate"

        self.execute()
        return True

    #results callbacks
    def on_b_ResetResults_activate(self, widget, *args):
        print "on_b_ResetResults_activate"
        return True

    def on_b_StopResults_activate(self, widget, *args):
        print "on_b_StopResults_activate"
        return True

class CallbacksFlagList(object):
    def __init__(self, dialog, cfg, flags):
        self._dialog = dialog
        self._flags = flags
        self._cfg = cfg

    def on_b_OK_activate(self, widget, *args):
        print "on_b_OK_activate"

        f = set()
        for k,w in self._flags.iteritems():
            if w.get_active():
                f.add(k)

        if len(f)==0:
            self._cfg.operation.flags = ""
        else:
            self._cfg.operation.flags = '"'+'" "'.join(f)+'"'

        self._dialog.destroy()
        return True

    def on_b_Cancel_activate(self, widget, *args):
        print "on_b_Cancel_activate"
        self._dialog.destroy()
        return True

class MainWindow(object):
    def __init__(self, cfg, tasker, importance = logging.INFO, dir=""):
        self._importance = importance
        self._glade = gtk.glade.XML(os.path.join(dir, "firstaidkit.glade"), "MainWindow")
        self._window = self._glade.get_widget("MainWindow")
        self._cb = CallbacksMainWindow(self._window, cfg, tasker, self._glade)
        self._glade.signal_autoconnect(self._cb)
        self._window.connect("destroy", self._cb.on_destroy)

        self.status_text = self._glade.get_widget("status_text")
        self.status_progress = self._glade.get_widget("status_progress")

    def update(self, message):
        def _o(func, *args, **kwargs):
            """Always return False -> remove from the idle queue after first execution"""
            func(*args, **kwargs)
            return False

        """Read the reporting system message and schedule a call to update stuff in the gui using gobject.idle_add(_o, func, params...)"""
        if message["action"]==reporting.END:
            gobject.idle_add(_o, self._window.destroy)
        elif message["action"]==reporting.QUESTION:
            print "FIXME: Questions not implemented yet"
        elif message["action"]==reporting.START:
            if self._importance<=message["importance"]:
                ctx = self.status_text.get_context_id(message["origin"].name)
                gobject.idle_add(_o, self.status_text.push, ctx, "START: %s (%s)" % (message["origin"].name, message["message"]))
        elif message["action"]==reporting.STOP:
            if self._importance<=message["importance"]:
                ctx = self.status_text.get_context_id(message["origin"].name)
                gobject.idle_add(_o, self.status_text.push, ctx, "STOP: %s (%s)" % (message["origin"].name, message["message"]))
        elif message["action"]==reporting.PROGRESS:
            if self._importance<=message["importance"]:
                if message["message"] is None:
                  gobject.idle_add(self.status_progress.hide)
                else:
                  gobject.idle_add(_o, self.status_progress.set_text, "%d/%d - %s" % (message["message"][0], message["message"][1], message["origin"].name))
                  gobject.idle_add(_o, self.status_progress.set_fraction, float(message["message"][0])/message["message"][1])
                  gobject.idle_add(_o, self.status_progress.show)
        elif message["action"]==reporting.INFO:
            if self._importance<=message["importance"]:
                ctx = self.status_text.get_context_id(message["origin"].name)
                gobject.idle_add(_o, self.status_text.push, ctx, "INFO: %s (%s)" % (message["message"], message["origin"].name))
        elif message["action"]==reporting.ALERT:
            if self._importance<=message["importance"]:
                ctx = self.status_text.get_context_id(message["origin"].name)
                gobject.idle_add(_o, self.status_text.push, ctx, "ALERT: %s (%s)" % (message["message"], message["origin"].name))
        elif message["action"]==reporting.EXCEPTION:
            ctx = self.status_text.get_context_id(message["origin"].name)
            gobject.idle_add(_o, self.status_text.push, ctx, "EXCEPTION: %s (%s)" % (message["message"], message["origin"].name))
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
        gtk.gdk.threads_init()
        gtk.main()

class FlagList(object):
    def __init__(self, cfg, flags, dir=""):
        self._glade = gtk.glade.XML(os.path.join(dir, "firstaidkit.glade"), "FlagList")
        self._window = self._glade.get_widget("FlagList")
        self._window.set_modal(True)
        self.flags = {}
        self._cb = CallbacksFlagList(self._window, cfg, self.flags)
        self._glade.signal_autoconnect(self._cb)
        fl_gui = self._glade.get_widget("box_flags")
        flags_set = cfg.operation._list("flags")
        for f in sorted(flags.known()):
            b = gtk.CheckButton(label=f)
            self.flags[f] = b
            b.set_active(f in flags_set)
            b.show()
            fl_gui.pack_start(b, expand=False, fill=True)
        l = gtk.Label("")
        l.show()

        fl_gui.pack_end(l, expand=True, fill=True)

if __name__=="__main__":
    w = MainWindow(None, None, None)
    w.run()

