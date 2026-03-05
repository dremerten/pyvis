import importlib
import importlib.util
import sys
import types


def reload(module):
    return importlib.reload(module)


def find_module(name, path=None):
    spec = importlib.util.find_spec(name, path)
    if spec is None:
        raise ModuleNotFoundError(name)
    # mimic imp.find_module return tuple (file, pathname, description)
    return None, spec.origin, (None, None, None)


def load_module(name, file=None, filename=None, details=None):
    spec = importlib.util.find_spec(name)
    if spec is None:
        raise ModuleNotFoundError(name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def new_module(name):
    return types.ModuleType(name)
