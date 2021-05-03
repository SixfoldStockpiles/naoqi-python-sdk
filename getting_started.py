import datetime
import functools
import math
import os
import random
import time

import naoqi
import qi

print os.environ['PYTHONPATH']
print os.environ['QI_SDK_PREFIX']

# IP = "127.0.0.1"
IP_ROBOT = "192.168.0.101"
PORT_ROBOT = 9559
IP_ME = "192.168.0.100"
PORT_ME = 9999

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

    proxy_motion = naoqi.ALProxy("ALMotion", IP_ROBOT, PORT_ROBOT)
    proxy_motion.wakeUp()

    proxy_autonomous_life = naoqi.ALProxy("ALAutonomousLife", IP_ROBOT, PORT_ROBOT)
    proxy_autonomous_life.setState("disabled")

    proxy_motion = naoqi.ALProxy("ALMotion", IP_ROBOT, PORT_ROBOT)
    proxy_motion.wakeUp()


def speech():
    """Say something"""

    proxy_tts = naoqi.ALProxy("ALTextToSpeech", IP_ROBOT, PORT_ROBOT)
    proxy_tts.say("Hello, world!")


def posture():
    """Read and command posture"""

    proxy_posture = naoqi.ALProxy("ALRobotPosture", IP_ROBOT, PORT_ROBOT)
    print("posture list={}".format(proxy_posture.getPostureList()))
    print("current posture={}".format(proxy_posture.getPosture()))
    proxy_posture.goToPosture("Sit", 0.75)
    proxy_posture.goToPosture("Stand", 0.75)


def joint_angles():
    """Read/write joint angles"""

    proxy_motion = naoqi.ALProxy("ALMotion", IP_ROBOT, PORT_ROBOT)
    target_head_pitch_deg = random.randrange(-10, 10)
    print "Target head pitch = {}".format(target_head_pitch_deg)
    print "HeadPitch(actual)={}".format([rad2deg(rad) for rad in proxy_motion.getAngles("HeadPitch", True)])
    print proxy_motion.setAngles(["HeadPitch"], [deg2rad(target_head_pitch_deg)], [1.0])
    for _ in range(10):
        print "HeadPitch(actual)={}".format([rad2deg(rad) for rad in proxy_motion.getAngles("HeadPitch", True)])
        time.sleep(0.01)


def events_and_callbacks_naoqi():
    """Example of getting callbacks for events"""

    # ALMemory acts as the hub for the distribution of event notifications.
    # Source: https://developer.softbankrobotics.com/nao6/naoqi-developer-guide/naoqi-apis/naoqi-core/almemory
    # Example: https://developer.softbankrobotics.com/nao6/naoqi-developer-guide/other-tutorials/python-sdk-tutorials/python-sdk-examples/vision/face

    class MyModule(naoqi.ALModule):
        """Mandatory docstring"""

        def myCallback(self, key, value, message):
            """Mandatory docstring"""

            print("Callback: key={}, value={}, message={}".format(key, value, message))

    # Create a broker
    # TODO(TK): why?
    naoqi.ALBroker("pythonBroker", IP_ME, PORT_ME, IP_ROBOT, PORT_ROBOT)

    # Create an instance of our callback handling module, and add it to global scope:
    global myModule  # needs to be in global scope
    myModule = MyModule("myModule")

    # [naoqi] Subscribe to events:
    proxy_memory = naoqi.ALProxy("ALMemory", IP_ROBOT, PORT_ROBOT)
    print "FaceDetected events before={}".format(proxy_memory.getEventHistory("FaceDetected"))
    proxy_memory.subscribeToEvent("FaceDetected", "myModule", "myCallback")

    # qi framework
    def mycallback(key, value):
        print("qi callback: key={}, value={}".format(key, value))
    sess = proxy_memory.session()
    mem = sess.service("ALMemory")
    sub = mem.subscriber("FaceDetected")
    sub.signal.connect(functools.partial(mycallback, "FaceDetected"))

    # Raise an event:
    proxy_memory.raiseEvent("FaceDetected", str(datetime.datetime.now()))
    proxy_memory.raiseEvent("AnotherEvent", str(datetime.datetime.now()))
    print "FaceDetected events after={}".format(proxy_memory.getEventHistory("FaceDetected"))
    time.sleep(0.1)  # give it some time to process


def events_and_callbacks_qi_framework():
    """Example of getting callbacks for events"""

    # ALMemory acts as the hub for the distribution of event notifications.
    # Source: https://developer.softbankrobotics.com/nao6/naoqi-developer-guide/naoqi-apis/naoqi-core/almemory
    # Example: https://developer.softbankrobotics.com/nao6/naoqi-developer-guide/other-tutorials/python-sdk-tutorials/python-sdk-examples/vision/face

    # Create a broker
    # TODO(TK): why?
    naoqi.ALBroker("pythonBroker", IP_ME, PORT_ME, IP_ROBOT, PORT_ROBOT)

    proxy_memory = naoqi.ALProxy("ALMemory", IP_ROBOT, PORT_ROBOT)

    # Register callback:
    def mycallback(key, value):
        print("qi callback: key={}, value={}".format(key, value))
    sess = proxy_memory.session()
    mem = sess.service("ALMemory")
    sub = mem.subscriber("FaceDetected")
    sub.signal.connect(functools.partial(mycallback, "FaceDetected"))

    # Raise an event:
    proxy_memory.raiseEvent("FaceDetected", str(datetime.datetime.now()))
    proxy_memory.raiseEvent("AnotherEvent", str(datetime.datetime.now()))
    time.sleep(0.1)  # give it some time to process


def main():
    # initialize_robot()

    # speech()
    # posture()
    # joint_angles()

    events_and_callbacks_naoqi()
    # events_and_callbacks_qi_framework()


if __name__ == "__main__":
    main()
