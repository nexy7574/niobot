import functools
import warnings

__all__ = ("deprecated",)


def deprecated(use_instead: str = None, removal_version: str = None):
    """Marks a function as deprecated and will warn users on call."""

    def wrapper(func):
        @functools.wraps(func)
        def caller(*args, **kwargs):
            parts = ["{} is deprecated.".format(func.__qualname__)]
            if removal_version:
                parts.append("It will be removed in version {}.".format(removal_version))
            if use_instead:
                parts.append("Please use %r instead." % use_instead)
            value = " ".join(parts)
            warn = DeprecationWarning(value)
            warnings.warn(warn)
            return func(*args, **kwargs)

        caller.__doc__ = func.__doc__
        return caller

    return wrapper
