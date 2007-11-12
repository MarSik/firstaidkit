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


class FAKConfigMixIn(ConfigParser.SafeConfigParser):
    """Enhance ConfigParser so we can use it in the python way (config.section.value)"""

    def __getattr__(self, section):
        return FAKConfigSection(self, section)

class FAKConfig(ConfigParser.SafeConfigParser, FAKConfigMixIn):
    pass

Config = FAKConfig()
Config.readfp(StringIO(defaultconfig), "<default>")
Config.read(cfgfile)


