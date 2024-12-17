def get_fd(object):
    if isinstance(object, int):
        return object
    return object.fileno()
