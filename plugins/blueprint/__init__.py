from . import packages
from . import repos

subplugins = [
    "packages",
    "repos"
    ]

submodules = [(n,locals()[n]) for n in subplugins]

def get_plugin():
    return submodules
