from pyfirstaidkit.plugins import Plugin,Flow

class BlueprintPlugin(Plugin):
    """This blueprint plugin template."""
    name = "Yum repositories"
    version = "0.0.1"
    author = "Martin Sivak"

    flows = Flow.init(Plugin)
    del flows["fix"]
    flows["blueprint"] = flows["diagnose"]
    
    def blueprint(self):
        pass
