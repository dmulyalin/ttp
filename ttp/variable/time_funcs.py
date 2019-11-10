import time

def get_time(*args, **kwargs):
    strformat="%H:%M:%S"
    return time.strftime(strformat)
    
def get_date(*args, **kwargs):
    strformat="%Y-%m-%d"
    return time.strftime(strformat)
    
def get_timestamp_ms(*args, **kwargs):
    strformat="%Y-%m-%d %H:%M:%S.{ms}"
    return time.strftime(strformat).format(ms=str(time.time()).split(".")[-1][:3])

def get_timestamp(*args, **kwargs):
    strformat="%Y-%m-%d %H:%M:%S"
    return time.strftime(strformat)
    
def get_time_ns(*args, **kwargs):
    # Return the current time in nanoseconds since the Epoch
    return time.time_ns()