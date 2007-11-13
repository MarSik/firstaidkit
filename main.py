import tasker.plugins
pluginSystem = tasker.plugins.PluginSystem()

if __name__=="__main__":
    for plugin in pluginSystem.list():
        pluginSystem.autorun(plugin)

