from itertools import count


def tmp_unique_name():
    for name in count():
        yield str(name)
