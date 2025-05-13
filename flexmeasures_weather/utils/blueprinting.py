import sys
import importlib


def ensure_bp_routes_are_loaded_fresh(module_name):
    """
    Reload a module if it has been loaded before.
    It's useful for situations in which some other process has read
    the module before, but you need some action to happen which only
    happens during module import ― decorators are a good example.

    One use case is pytest, which reads all python code when it collects tests.
    In our case, that happens before FlexMeasures' import mechanism
    has had a chance to know which blueprints a plugin has.
    Seemingly, the importing code (plugin's __init__) can be imported later
    than the imported module (containing @route decorators).
    Re-importing helps to get this order right when FlexMeasures reads the
    plugin's __init__.
    """
    m_name = "flexmeasures_weather." + module_name
    if m_name in sys.modules:
        importlib.reload(sys.modules[m_name])
