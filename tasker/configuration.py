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

import ConfigParser
import os
from StringIO import StringIO

if os.environ.has_key("FIRST_AID_KIT_CONF"):
    cfgfile = os.environ["FIRST_AID_KIT_CONF"].split(":")
else:
    cfgfile = ["/etc/firstaidkit.conf", os.environ["HOME"]+"/.firstaidkit.conf"]

defaultconfig = """
[plugin]
path = /usr/lib/FirstAidKit/plugins
disabled =

[operation]
mode = auto
verbose = False
gui = console

[log]
method = stdout
"""

class FAKConfigSection(object):
    """Proxy object for one configuration section"""

    def __init__(self, cfg, name):
        self.__dict__["section_name"] = name
        self.__dict__["configuration"] = cfg

    def __getattr__(self, key):
        if not self.__dict__["configuration"].has_section(self.__dict__["section_name"]):
            raise ConfigParser.NoSectionError(self.__dict__["section_name"])

        if not self.__dict__["configuration"].has_option(self.__dict__["section_name"], key):
            raise ConfigParser.NoOptionError(key)

        return self.__dict__["configuration"].get(self.__dict__["section_name"], key)

    def __setattr__(self, key, value):
        if not self.__dict__["configuration"].has_section(self.__dict__["section_name"]):
            self.__dict__["configuration"].add_section(self.__dict__["section_name"])
        self.__dict__["configuration"].set(self.__dict__["section_name"], key, value)


class FAKConfigMixIn(object):
    """Enhance ConfigParser so we can use it in the python way (config.section.value)"""

    def __getattr__(self, section):
        return FAKConfigSection(self, section)

class FAKConfig(ConfigParser.SafeConfigParser, FAKConfigMixIn):
    pass

Config = FAKConfig()
Config.readfp(StringIO(defaultconfig), "<default>")
Config.read(cfgfile)


