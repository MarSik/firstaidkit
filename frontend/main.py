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
    def __init__(self, dialog, cfg, tasker, glade, data):
        self._dialog = dialog
        self._tasker = tasker
        self._glade = glade
        self._cfg = cfg
        self._data = data
        self._running_lock = thread.allocate_lock()

    def execute(self):
        if not self._running_lock.acquire(0):
            return

        def _o(pages):
            """Always return False -> remove from the idle queue after first execution"""
            for i in range(pages.get_n_pages()):
                pages.get_nth_page(i).set_sensitive(True)
            return False

        def worker(*args):
            self._cfg.lock()
            self._tasker.run()
            self._cfg.unlock()
            gobject.idle_add(_o, *args)
            self._running_lock.release()

        self._data.pages.set_current_page(-1)
        for i in range(self._data.pages.get_n_pages())[:-1]:
            self._data.pages.get_nth_page(i).set_sensitive(False)
        thread.start_new_thread(worker, (self._data.pages,))

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
        return True

    def on_destroy(self, widget, *args):
        print "on_destroy"
        self._tasker.end()
        del self._tasker
        del self._cfg
        gtk.main_quit()

    def on_mainmenu_about_activate(self, widget, *args):
        print "on_mainmenu_about_activate"
        return True

    #simple mode callbacks
    def on_b_StartSimple_activate(self, widget, *args):
        print "on_b_StartSimple_activate"
       
        flags = set(self._cfg.operation._list("flags"))

        #check fix
        if self._glade.get_widget("check_Simple_Fix").get_active():
            self._cfg.operation.mode = "auto-flow"
            self._cfg.operation.flow = "fix"
        else:
            self._cfg.operation.mode = "auto-flow"
            self._cfg.operation.flow = "diagnose"

        #check interactive
        if self._glade.get_widget("check_Simple_Interactive").get_active():
            self._cfg.operation.interactive = "True"
        else:
            self._cfg.operation.interactive = "False"

        #check verbose
        if self._glade.get_widget("check_Simple_Verbose").get_active():
            self._cfg.operation.verbose = "True"
        else:
            self._cfg.operation.verbose = "False"

        #check experimental
        if self._glade.get_widget("check_Simple_Experimental").get_active():
            flags.add("experimental")
        else:
            try:
                flags.remove("experimental")
            except KeyError, e:
                pass

        self._cfg.operation.flags = " ".join(map(lambda x: x.encode("string-escape"), flags))
        self.execute()
        return True

    #advanced mode callbacks
    def on_b_StartAdvanced_activate(self, widget, *args):
        print "on_b_StartAdvanced_activate"
        
        flags = set(self._cfg.operation._list("flags"))
        
        #set the auto-flow
        self._cfg.operation.mode = "auto-flow"

        idx = self._data.flow_list.get_active_iter()
        if idx is None:
            return True
        self._cfg.operation.flow = self._data.flow_list_store.get_value(idx,0)

        #check verbose
        if self._glade.get_widget("check_Advanced_Verbose").get_active():
            self._cfg.operation.verbose = "True"
        else:
            self._cfg.operation.verbose = "False"

        #check experimental
        if self._glade.get_widget("check_Advanced_Experimental").get_active():
            flags.add("experimental")
        else:
            try:
                flags.remove("experimental")
            except KeyError, e:
                pass

        #check interactive
        if self._glade.get_widget("check_Advanced_Interactive").get_active():
            self._cfg.operation.interactive = "True"
        else:
            self._cfg.operation.interactive = "False"

        #check dependency
        if self._glade.get_widget("check_Advanced_Dependency").get_active():
            self._cfg.operation.dependencies = "True"
        else:
            self._cfg.operation.dependencies = "False"

        self._cfg.operation.flags = " ".join(map(lambda x: x.encode("string-escape"), flags))

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

        #check verbose
        if self._glade.get_widget("check_Expert_Verbose").get_active():
            self._cfg.operation.verbose = "True"
        else:
            self._cfg.operation.verbose = "False"

        #check interactive
        if self._glade.get_widget("check_Expert_Interactive").get_active():
            self._cfg.operation.interactive = "True"
        else:
            self._cfg.operation.interactive = "False"

        #check dependency
        if self._glade.get_widget("check_Expert_Dependency").get_active():
            self._cfg.operation.dependencies = "True"
        else:
            self._cfg.operation.dependencies = "False"

        #get the plugin & flow list
        plugins = []
        flows = []

        for pname,iter in self._data.plugin_iter.iteritems():
            childiter = self._data.plugin_list_store.iter_children(iter)
            while childiter is not None:
                if self._data.plugin_list_store.get_value(childiter, 0): #checkbox is checked
                    plugins.append(pname)
                    flows.append(self._data.plugin_list_store.get_value(childiter, 1))
                childiter = self._data.plugin_list_store.iter_next(childiter)

        plugins = map(lambda x: x.encode("string-escape"), plugins)
        flows = map(lambda x: x.encode("string-escape"), flows)

        #set the flow mode
        self._cfg.operation.mode = "flow"
        self._cfg.operation.flow = " ".join(flows)
        self._cfg.operation.plugin = " ".join(plugins)

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
            self._cfg.operation.flags = " ".join(map(lambda x: x.encode("string-escape"), f))

        self._dialog.destroy()
        return True

    def on_b_Cancel_activate(self, widget, *args):
        print "on_b_Cancel_activate"
        self._dialog.destroy()
        return True

class MainWindow(object):
    def __init__(self, cfg, tasker, importance = logging.INFO, dir=""):
        self._importance = importance
        self._cfg = cfg
        self._glade = gtk.glade.XML(os.path.join(dir, "firstaidkit.glade"), "MainWindow")
        self._window = self._glade.get_widget("MainWindow")
        self._cb = CallbacksMainWindow(self._window, cfg, tasker, self._glade, self)
        self._glade.signal_autoconnect(self._cb)
        self._window.connect("destroy", self._cb.on_destroy)

        self.pages = self._glade.get_widget("pages")
        self.status_text = self._glade.get_widget("status_text")
        self.status_progress = self._glade.get_widget("status_progress")

        self.plugin_list_store = gtk.TreeStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.plugin_list = self._glade.get_widget("tree_Expert")
        self.plugin_list.set_model(self.plugin_list_store)

        self.plugin_rend_text = gtk.CellRendererText()
        self.plugin_rend_toggle = gtk.CellRendererToggle()
        self.plugin_rend_toggle.set_radio(False)
        self.plugin_rend_toggle.set_property("activatable", False)

        def plugin_rend_text_func(column, cell_renderer, tree_model, iter, user_data):
            if tree_model.iter_depth(iter)==0:
                cell_renderer.set_property("cell-background-set", True)
                cell_renderer.set_property("cell-background-gdk", gtk.gdk.Color(red=50000, green=50000, blue=50000))
                cell_renderer.set_property("markup", "<b>" + tree_model.get_value(iter, user_data) + "</b>")
            else:
                cell_renderer.set_property("cell-background-set", False)
                cell_renderer.set_property("text", tree_model.get_value(iter, user_data))
            return

        def plugin_rend_toggle_func(column, cell_renderer, tree_model, iter, user_data = None):
            if tree_model.iter_depth(iter)==0:
                cell_renderer.set_property("activatable", False)
                cell_renderer.set_property("active", False)
                cell_renderer.set_property("visible", False)
                cell_renderer.set_property("cell-background-set", True)
                cell_renderer.set_property("cell-background-gdk", gtk.gdk.Color(red=40000, green=40000, blue=40000))
            else:
                cell_renderer.set_property("activatable", True)
                cell_renderer.set_property("active", tree_model.get_value(iter,0))
                cell_renderer.set_property("visible", True)
                cell_renderer.set_property("cell-background-set", False)
            return

        def plugin_rend_toggle_cb(cell, path, data):
            model, col = data
            model[path][0] = not model[path][col]
            return

        self.plugin_list_col_0 = gtk.TreeViewColumn('Use')
        self.plugin_list_col_0.pack_start(self.plugin_rend_toggle, False)
        self.plugin_list_col_0.set_cell_data_func(self.plugin_rend_toggle, plugin_rend_toggle_func)
        self.plugin_rend_toggle.connect("toggled", plugin_rend_toggle_cb, (self.plugin_list_store, 0))

        self.plugin_list_col_1 = gtk.TreeViewColumn('Name')
        self.plugin_list_col_1.pack_start(self.plugin_rend_text, True)
        self.plugin_list_col_1.set_cell_data_func(self.plugin_rend_text, plugin_rend_text_func, 1)

        self.plugin_list_col_2 = gtk.TreeViewColumn('Description')
        self.plugin_list_col_2.pack_start(self.plugin_rend_text, True)
        self.plugin_list_col_2.set_cell_data_func(self.plugin_rend_text, plugin_rend_text_func, 2)

        self.plugin_list_col_3 = gtk.TreeViewColumn('Parameters')
        self.plugin_list_col_3.pack_start(self.plugin_rend_text, True)
        self.plugin_list_col_3.set_cell_data_func(self.plugin_rend_text, plugin_rend_text_func, 3)

        self.plugin_list.append_column(self.plugin_list_col_0)
        self.plugin_list.append_column(self.plugin_list_col_1)
        self.plugin_list.append_column(self.plugin_list_col_2)
        self.plugin_list.append_column(self.plugin_list_col_3)
        self.plugin_list.set_search_column(1)

        pluginsystem = tasker.pluginsystem()
        self.plugin_iter = {}
        self.flow_list_data = set()

        for plname in pluginsystem.list():
            p = pluginsystem.getplugin(plname)
            piter = self.plugin_list_store.append(None, [False, "%s (%s)" % (p.name, p.version), p.description, ""])
            self.plugin_iter[plname] = piter
            for n,d in [ (f, p.getFlow(f).description) for f in p.getFlows() ]:
                self.plugin_list_store.append(piter, [False, n, d, ""])
                self.flow_list_data.add(n)

        self.flow_list_rend_text = gtk.CellRendererText()
        self.flow_list_store = gtk.ListStore(gobject.TYPE_STRING)
        self.flow_list_store_diagnose = -1
        for idx,n in enumerate(sorted(self.flow_list_data)):
            self.flow_list_store.append([n])
            if n=="diagnose":
                self.flow_list_store_diagnose = idx
        self.flow_list = self._glade.get_widget("combo_Advanced_Flows")
        self.flow_list.set_model(self.flow_list_store)
        self.flow_list.pack_start(self.flow_list_rend_text, True)
        self.flow_list.add_attribute(self.flow_list_rend_text, 'text', 0)
        self.flow_list.set_active(self.flow_list_store_diagnose)

    def update(self, message):
        def _o(func, *args, **kwargs):
            """Always return False -> remove from the idle queue after first execution"""
            func(*args, **kwargs)
            return False

        if self._cfg.operation.verbose == "True":
            self._importance = logging.DEBUG
        else:
            self._importance = logging.INFO

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

