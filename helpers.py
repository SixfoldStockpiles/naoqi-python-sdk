import sys
import time


def retry_wrapper(func):
    def wrapped_func(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                sys.stderr.write(str(exc))
                sys.stderr.flush()
                time.sleep(0.1)

    return wrapped_func


def parse_face_expressions(data):
    if len(data) != 5:
        raise ValueError("Incorrect number of data fields")
    return {
        "neutral": data[0],
        "happy": data[1],
        "surprised": data[2],
        "angry": data[3],
        "sad": data[4],
    }
