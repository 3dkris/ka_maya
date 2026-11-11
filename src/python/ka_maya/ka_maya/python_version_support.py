# ------------------------------------------------------------------------------
# define global keyword builtins
try:
    # Python 3+
    import builtins

except ImportError:
    # Python 2.7
    import __builtin__ as builtins


# ------------------------------------------------------------------------------
# define global keyword reload
# Python 2.7 it is alread a builtin keyword
if not hasattr(builtins, "reload"):
    try:
        # Python 3.4+
        import importlib

        builtins.reload = importlib.reload

    except ImportError:
        try:
            # Python 3.0 - 3.3
            import imp

            builtins.reload = imp.reload

        except ImportError:
            pass
