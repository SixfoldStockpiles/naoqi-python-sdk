import sys
import time

import numpy as np


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


def parse_image(image):

    color_space = image[3]
    assert color_space == ColorSpace.kYUV422ColorSpace  # this is the only one supported for raw images

    width = image[0]
    height = image[1]
    layers = image[2]

    data_raw = image[6]
    data_raw = bytes(data_raw)
    data_array = np.frombuffer(data_raw, dtype=np.int8)
    # assert data_array.shape[0] == height * width * layers

    # Grab brightness only from YUV format
    # (https://www.flir.com.au/support-center/iis/machine-vision/knowledge-base/understanding-yuv-data-formats/)
    data_array = np.reshape(data_array, (-1, 2))
    data_array = data_array[:, 0]  # just brightness

    data_array = np.reshape(data_array, (height, width), order='A')
    # assert data_array.shape == (height, width)

    data_array = (data_array + 128.0) / 256.0

    print(np.max(data_array), np.min(data_array))

    return data_array

    # return {
    #     "width": width,
    #     "height": height,
    #     "numberOfLayers": layers,
    #     "colorSpace": color_space,
    #     "ts_s": image[4],
    #     "ts_ms": image[5],
    #     "data": data_array,
    #     "cameraId": image[7],
    #     "leftAngle": image[8],
    #     "topAngle": image[9],
    #     "rightAngle": image[10],
    #     "bottomAngle": image[11],
    # }


class CameraResolution:
    k16VGA = 4  # 2560x1920px up to 15fps
    k4VGA = 3  # 1280x960px up to 30fps
    kVGA = 2  # 640x480px up to 30fps
    kQVGA = 1  # 320x240px up to 30fps


class ColorSpace:
    kYUV422ColorSpace = 9
