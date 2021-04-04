import math
import os
import random
import time

import naoqi

print os.environ['PYTHONPATH']
print os.environ['QI_SDK_PREFIX']

IP = "127.0.0.1"
PORT = 9559

# Note that naoqi.ALProxy wraps C++ code of the module provided as an argument, and seamlessly converts method calls
# which are valid in that module to Python module method calls.
# See inaoqi.py:471 for more info.


def rad2deg(rad):
    return rad / (math.pi / 180)


def deg2rad(deg):
    return deg * (math.pi / 180.0)


assert abs(rad2deg(deg2rad(12)) - 12) < 1e-6
assert abs(rad2deg(deg2rad(-12)) - (-12)) < 1e-6


def initialize_robot():
    """Wake up (stiff joints) and disable autonomous life (autonomous human-like motions)"""

    proxy_autonomous_life = naoqi.ALProxy("ALAutonomousLife", IP, PORT)
    proxy_autonomous_life.setState("disabled")

    proxy_motion = naoqi.ALProxy("ALMotion", IP, PORT)
    proxy_motion.wakeUp()


def speech():
    """Say something"""

    proxy_tts = naoqi.ALProxy("ALTextToSpeech", IP, PORT)
    proxy_tts.say("Hello, world!")


def posture():
    """Read and command posture"""

    proxy_posture = naoqi.ALProxy("ALRobotPosture", IP, PORT)
    print("posture list={}".format(proxy_posture.getPostureList()))
    print("current posture={}".format(proxy_posture.getPosture()))
    proxy_posture.goToPosture("Sit", 0.75)
    proxy_posture.goToPosture("Stand", 0.75)


def joint_angles():
    """Read/write joint angles"""

    proxy_motion = naoqi.ALProxy("ALMotion", IP, PORT)
    target_head_pitch_deg = random.randrange(-10, 10)
    print "Target head pitch = {}".format(target_head_pitch_deg)
    print "HeadPitch(actual)={}".format([rad2deg(rad) for rad in proxy_motion.getAngles("HeadPitch", True)])
    print proxy_motion.setAngles(["HeadPitch"], [deg2rad(target_head_pitch_deg)], [1.0])
    for _ in range(10):
        print "HeadPitch(actual)={}".format([rad2deg(rad) for rad in proxy_motion.getAngles("HeadPitch", True)])
        time.sleep(0.01)


def stimulus():
    # TODO(TK): Responding to stimulus

    proxy_basic_awareness = naoqi.ALProxy("ALBasicAwareness", IP, PORT)
    proxy_basic_awareness.triggerStimulus([0, 0, 0, 0, 0, 0])


def main():
    initialize_robot()

    # speech()
    # posture()
    # joint_angles()
    # stimulus()


if __name__ == "__main__":
    main()
