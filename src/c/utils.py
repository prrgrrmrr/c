from itertools import count

def tmp_unique_name(prefix = None):
    for name in count():
        if prefix:
            yield f"{prefix}name"
        else:
            yield str(name)
