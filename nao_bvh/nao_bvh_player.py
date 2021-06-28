#! /bin/env python2.7
import math
import os
import sys
import time

import pandas as pd

from pymo.parsers import BVHParser
from pymo.preprocessing import MocapParameterizer

assert 'QI_SDK_PREFIX' in os.environ
import naoqi
import qi


class NaoGesturePlayer:
    def __init__(self, robot_ip, robot_port, my_ip, my_port, stream_err=sys.stderr):
        self._robot_ip = robot_ip
        self._robot_port = robot_port
        self._my_ip = my_ip
        self._my_port = my_port
        self._stream_err = stream_err

    def play(self, df_gestures):
        """
        Takes a DataFrame of Nao joint rotations, with the index as a series of timestamps, and plays these on the Nao
        robot.
        """

        proxy_motion = naoqi.ALProxy("ALMotion", self._robot_ip, self._robot_port)
        proxy_motion.wakeUp()

        dt_initial = 0.1
        t_begin = time.time() + dt_initial
        for index, series_row in df_gestures.iterrows():
            # Sync timing:
            t_target = index.total_seconds()
            t_elapsed = time.time() - t_begin
            dt = t_target - t_elapsed
            if dt > 0:
                time.sleep(dt)
            else:
                self._stream_err.write("WARNING! Robot fell behind achieving gestures\n")

            # Execute on robot:
            for frame in series_row.index:
                proxy_motion.setAngles(frame, series_row[frame], 1.0)


class NaoBvhConverter:
    def __init__(self):
        pass

    @staticmethod
    def read_mocap_data(bvh_file):
        parser = BVHParser()
        return parser.parse(bvh_file)

    @staticmethod
    def bvh_to_dataframe_of_nao_gestures(mocap_data):
        relevant_bvh_rotations = NaoBvhConverter._get_relevant_bvh_rotations(mocap_data)
        nao_rotations_degrees = NaoBvhConverter._convert_bvh_rotations_to_nao_degrees(relevant_bvh_rotations)
        nao_rotations_radians = {key: NaoBvhConverter._convert_series_degrees_to_radians(nao_rotations_degrees[key]) for
                                 key in nao_rotations_degrees}
        return NaoBvhConverter._convert_dict_of_series_to_df(nao_rotations_radians)

    @staticmethod
    def _get_relevant_bvh_rotations(mocap_data):
        """
        Get the subset of BVH rotations which will be used for robot gestures.
        """

        mp_euler = MocapParameterizer('euler')
        rotations, = mp_euler.fit_transform([mocap_data])
        relevant_frames = [
            "RightArm_Xrotation",
            "RightArm_Yrotation",
            "RightArm_Zrotation",
            "RightForeArm_Xrotation",
            "RightForeArm_Yrotation",
            "RightForeArm_Zrotation",
            "LeftArm_Xrotation",
            "LeftArm_Yrotation",
            "LeftArm_Zrotation",
            "LeftForeArm_Xrotation",
            "LeftForeArm_Yrotation",
            "LeftForeArm_Zrotation",
        ]
        return {key: rotations.values[key] for key in relevant_frames}

    @staticmethod
    def _convert_bvh_rotations_to_nao_degrees(bvh_rotations):
        """
        Take an input dictionary of series of BVH rotations (in degrees), and convert to Nao frames (in degrees)
        """

        return {
            "RShoulderRoll": bvh_rotations["RightArm_Zrotation"] - 90.0,
            "RShoulderPitch": -bvh_rotations["RightArm_Xrotation"] + 90.0,
            "RElbowYaw": -(bvh_rotations["RightForeArm_Zrotation"] + bvh_rotations["RightArm_Yrotation"]) + 90.0,
            "RElbowRoll": bvh_rotations["RightForeArm_Yrotation"],
            "LShoulderRoll": bvh_rotations["LeftArm_Zrotation"] + 90.0,
            "LShoulderPitch": -bvh_rotations["LeftArm_Xrotation"] + 90.0,
            "LElbowYaw": -(bvh_rotations["LeftForeArm_Zrotation"] + bvh_rotations["LeftArm_Yrotation"]) - 90.0,
            "LElbowRoll": bvh_rotations["LeftForeArm_Yrotation"],
        }

    @staticmethod
    def _convert_series_degrees_to_radians(series_degrees):
        """
        Converts a series of floating point numbers in degrees to radians.
        """

        return series_degrees * math.pi / 180.0

    @staticmethod
    def _convert_dict_of_series_to_df(dict_of_series):
        return pd.DataFrame(data=dict_of_series)


if __name__ == "__main__":
    # Get a playable dataframe of gestures:
    mocap_data = NaoBvhConverter.read_mocap_data('../rand_1.bvh')
    df_gestures = NaoBvhConverter.bvh_to_dataframe_of_nao_gestures(mocap_data)

    # Play gestures:
    player = NaoGesturePlayer(
        robot_ip="127.0.0.1",
        robot_port=9559,
        my_ip="127.0.0.1",
        my_port=1234,
    )
    player.play(df_gestures)
