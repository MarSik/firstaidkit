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

from log import Logger
from plugins import PluginSystem

class Tasker:
    """The main interpret of tasks described in Config object"""

    def __init__(self, cfg):
        self._config = cfg

    def run(self):
        pluginSystem = PluginSystem()

        if self._config.operation.mode == "auto":
            for plugin in pluginSystem.list():
                pluginSystem.autorun(plugin)
        elif self._config.operation.mode == "flow":
            pluginSystem.autorun(self._config.operation.plugin, flow = self._config.operation.flow)
        elif self._config.operation.mode == "plugin":
            pluginSystem.autorun(self._config.operation.plugin)
        elif self._config.operation.mode == "task":
            pass
        else:
            Logger.error("Incorrect task specified")
            return False

        return True
