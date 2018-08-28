from datetime import datetime

def to_readable_time(string_time_time):

    int_time_time = int(string_time_time)

# if you encounter a "year is out of range" error the timestamp
# may be in milliseconds, try `ts /= 1000` in that case
    return (datetime.utcfromtimestamp(int_time_time).strftime('%Y-%m-%d %H:%M:%S'))