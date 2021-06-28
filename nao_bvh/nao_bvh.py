import os
import math
import time

import naoqi
import qi
from pymo.parsers import BVHParser
from pymo.preprocessing import MocapParameterizer
from pymo.viz_tools import draw_stickfigure
import matplotlib.pyplot as plt


print os.environ['PYTHONPATH']
print os.environ['QI_SDK_PREFIX']


def rad2deg(rad):
    return rad / (math.pi / 180)


def deg2rad(deg):
    return deg * (math.pi / 180.0)


def initialize_robot():
    """Wake up (stiff joints) and disable autonomous life (autonomous human-like motions)"""

    # proxy_motion = naoqi.ALProxy("ALMotion", IP_ROBOT, PORT_ROBOT)
    # proxy_motion.wakeUp()
    #
    # proxy_autonomous_life = naoqi.ALProxy("ALAutonomousLife", IP_ROBOT, PORT_ROBOT)
    # proxy_autonomous_life.setState("disabled")

    proxy_motion = naoqi.ALProxy("ALMotion", IP_ROBOT, PORT_ROBOT)
    proxy_motion.wakeUp()


assert abs(rad2deg(deg2rad(12)) - 12) < 1e-6
assert abs(rad2deg(deg2rad(-12)) - (-12)) < 1e-6


if __name__ == '__main__':
    IP_ROBOT = "127.0.0.1"
    PORT_ROBOT = 9559
    IP_ME = "127.0.0.1"
    PORT_ME = 1234

    parser = BVHParser()
    parsed_data = parser.parse('rand_1.bvh')

    from pymo.viz_tools import print_skel
    print_skel(parsed_data)

    initialize_robot()

    mp_euler = MocapParameterizer('euler')
    rotations, = mp_euler.fit_transform([parsed_data])

    for frame_idx in range(rotations.values["RightArm_Xrotation"].size):
        time_begin = time.time()

        r_arm_x_rot = rotations.values["RightArm_Xrotation"].iloc[frame_idx]
        r_arm_y_rot = rotations.values["RightArm_Yrotation"].iloc[frame_idx]
        r_arm_z_rot = rotations.values["RightArm_Zrotation"].iloc[frame_idx]
        r_forearm_x_rot = rotations.values["RightForeArm_Xrotation"].iloc[frame_idx]
        r_forearm_y_rot = rotations.values["RightForeArm_Yrotation"].iloc[frame_idx]
        r_forearm_z_rot = rotations.values["RightForeArm_Zrotation"].iloc[frame_idx]

        l_arm_x_rot = rotations.values["LeftArm_Xrotation"].iloc[frame_idx]
        l_arm_y_rot = rotations.values["LeftArm_Yrotation"].iloc[frame_idx]
        l_arm_z_rot = rotations.values["LeftArm_Zrotation"].iloc[frame_idx]
        l_forearm_x_rot = rotations.values["LeftForeArm_Xrotation"].iloc[frame_idx]
        l_forearm_y_rot = rotations.values["LeftForeArm_Yrotation"].iloc[frame_idx]
        l_forearm_z_rot = rotations.values["LeftForeArm_Zrotation"].iloc[frame_idx]

        proxy_motion = naoqi.ALProxy("ALMotion", IP_ROBOT, PORT_ROBOT)

        proxy_motion.setAngles("RShoulderRoll", deg2rad(r_arm_z_rot - 90), 1.0)
        proxy_motion.setAngles("RShoulderPitch", deg2rad(-r_arm_x_rot + 90), 1.0)
        proxy_motion.setAngles("RElbowYaw", deg2rad(-(r_forearm_z_rot + r_arm_y_rot) + 90), 1.0)
        proxy_motion.setAngles("RElbowRoll", deg2rad(r_forearm_y_rot), 1.0)

        proxy_motion.setAngles("LShoulderRoll", deg2rad(l_arm_z_rot + 90), 1.0)
        proxy_motion.setAngles("LShoulderPitch", deg2rad(-l_arm_x_rot + 90), 1.0)
        proxy_motion.setAngles("LElbowYaw", deg2rad(-(l_forearm_z_rot + l_arm_y_rot) - 90), 1.0)
        proxy_motion.setAngles("LElbowRoll", deg2rad(l_forearm_y_rot), 1.0)

        # TODO(TK): this should really reference an absolute, not relative, objective timestamp to avoid accumulating
        #  error
        t_sleep = rotations.framerate - (time.time() - time_begin)
        time.sleep(t_sleep)
