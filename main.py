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

import sys
import getopt
import tasker.plugins
from tasker.configuration import Config

def usage(name):
    print """Usage:
 %s [params] [plugin [flow]]
 %s [params] -t plugin task
 params is none or more items from:
  -c <config file> - select different config file
  -v               - verbose mode
  -l <method>      - select different log method
  -x <plugin>      - exclude plugin from run
  -h               - this help
""" % (name, name)

if __name__=="__main__":
    params, rest = getopt.getopt(sys.argv[1:], "tc:vl:x:h", ["task", "config=", "verbose", "log=", "exclude=", "help"])
    for key,val in params:
        if key in ("-t", "--task"):
            Config.operation.mode = "task"
        elif key in ("-c", "--config"):
            Config.read(val)
        elif key in ("-v", "--verbose"):
            Config.operation.verbose = "True"
        elif key in ("-l", "--log"):
            Config.log.method = val
        #elif key in ("-x", "--exclude"):
        #    Config.plugin.disabled.append(val)
        #    print "Excluding plugin %s\n" % (val,)
        elif key in ("-h", "--help"):
            usage(sys.argv[0])
            sys.exit(1)

    pluginSystem = tasker.plugins.PluginSystem()

    for plugin in pluginSystem.list():
        pluginSystem.autorun(plugin)

