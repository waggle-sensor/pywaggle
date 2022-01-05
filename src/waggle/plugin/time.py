import time

# BUG This *must* be addressed with the behavior written up in the plugin spec.
# We don't want any surprises in terms of accuraccy
try:
    from time import time_ns as get_timestamp
except ImportError:
    def get_timestamp():
        return int(time.time() * 1e9)

# NOTE to preserve the best accuracy, we implement the backwards compatible perf
# counter by only abstracting how to measure the duration between two times in
# nanoseconds
try:
    from time import perf_counter_ns as timeit_perf_counter

    def timeit_perf_counter_duration(start, finish):
        return finish - start
except ImportError:
    from time import perf_counter as timeit_perf_counter

    def timeit_perf_counter_duration(start, finish):
        return int((finish - start) * 1e9)
