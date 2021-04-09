"""
scratch file for experimenting with inspect
"""

import inspect
import kinetic
print(inspect.getmembers(kinetic))
import sys
sys.path.insert(0, "F://swbs//")
import swbs
print(inspect.getmembers(swbs))
from importlib import import_module
inspect_example = import_module("inspect_example")
print(inspect.getmembers(inspect_example.Test))
print(inspect_example.Test.__bases__)
