try:
    from time import time_ns as get_timestamp
except ImportError:
    from time import time
    def get_timestamp():
        return int(time() * 1e9)
