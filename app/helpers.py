# https://stackoverflow.com/a/58045927
def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + "." + obj.__class__.__name__


def wrap_exception(e, message, log=True):
    if log:
        print(f"Exception: {get_full_class_name(e)}: {e}")
    error = {
        "message": message,
        "exception": str(e),
    }
    return error
