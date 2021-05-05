import datetime
import functools
import json
import math
import os
import random
import time

import naoqi
import qi

from helpers import retry_wrapper, parse_face_expressions


print os.environ['PYTHONPATH']
print os.environ['QI_SDK_PREFIX']

# IP = "127.0.0.1"
IP_ROBOT = "192.168.0.100"
PORT_ROBOT = 9559
IP_ME = "192.168.0.102"
PORT_ME = 1234

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
    # print proxy_motion.setAngles(["HeadPitch"], [deg2rad(target_head_pitch_deg)], [1.0])
    print proxy_motion.setAngles("RShoulderPitch", deg2rad(0), 1.0)
    # print proxy_motion.setAngles("LShoulderRoll", deg2rad(90 * random.random()), 0.5)
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
    naoqi.ALBroker("pythonBroker", "127.0.0.1", 1234, IP_ROBOT, PORT_ROBOT)

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
    naoqi.ALBroker("pythonBroker", "127.0.0.1", 1234, IP_ROBOT, PORT_ROBOT)

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


def people_perception():

    retry_proxy = retry_wrapper(naoqi.ALProxy)
    retry_broker = retry_wrapper(naoqi.ALBroker)

    proxy_face_detection = retry_proxy("ALFaceDetection", IP_ROBOT, PORT_ROBOT)
    proxy_people_perception = retry_proxy("ALPeoplePerception", IP_ROBOT, PORT_ROBOT)

    proxy_people_perception.setFastModeEnabled(False)

    print "isTrackingEnabled={}".format(proxy_face_detection.isTrackingEnabled())
    print "isRecognitionEnabled={}".format(proxy_face_detection.isRecognitionEnabled())
    print "isFaceDetectionEnabled={}".format(proxy_people_perception.isFaceDetectionEnabled())
    print "isFastModeEnabled={}".format(proxy_people_perception.isFastModeEnabled())

    retry_broker("pythonBroker", "127.0.0.1", 1234, IP_ROBOT, PORT_ROBOT)
    proxy_memory = naoqi.ALProxy("ALMemory", IP_ROBOT, PORT_ROBOT)
    sess = proxy_memory.session()
    mem = sess.service("ALMemory")

    # Register callback:
    def mycallback(key, value):
        print("qi callback: key={}, value={}".format(key, value))

    events = [
        "PeoplePerception/PeopleDetected",
        "PeoplePerception/JustLeft",
        "PeoplePerception/JustArrived",
        "PeoplePerception/NonVisiblePeopleList",
        "PeoplePerception/VisiblePeopleList",
        "FaceDetected",  # TODO(TK): This only works if "play" is pressed in Choreographe - why?
        # "FaceCharacteristics/PersonSmiling",
    ]
    # TODO(TK): multiple events not working; only last one subscribed to
    for idx_event, event in enumerate(events):
        sub = mem.subscriber(event)
        sub.signal.connect(functools.partial(mycallback, event))

    time.sleep(15)


def face_characteristics():

    global visible_persons

    retry_proxy = retry_wrapper(naoqi.ALProxy)
    retry_broker = retry_wrapper(naoqi.ALBroker)

    proxy_face_detection = retry_proxy("ALFaceDetection", IP_ROBOT, PORT_ROBOT)
    proxy_people_perception = retry_proxy("ALPeoplePerception", IP_ROBOT, PORT_ROBOT)
    proxy_gaze_analysis = retry_proxy("ALGazeAnalysis", IP_ROBOT, PORT_ROBOT)

    proxy_people_perception.setFastModeEnabled(False)
    proxy_gaze_analysis.setFaceAnalysisEnabled(True)

    print "isTrackingEnabled={}".format(proxy_face_detection.isTrackingEnabled())
    print "isRecognitionEnabled={}".format(proxy_face_detection.isRecognitionEnabled())
    print "isFaceDetectionEnabled={}".format(proxy_people_perception.isFaceDetectionEnabled())
    print "isFastModeEnabled={}".format(proxy_people_perception.isFastModeEnabled())
    print "isFaceAnalysisEnabled={}".format(proxy_gaze_analysis.isFaceAnalysisEnabled())

    retry_broker("pythonBroker", "127.0.0.1", 1234, IP_ROBOT, PORT_ROBOT)
    proxy_memory = naoqi.ALProxy("ALMemory", IP_ROBOT, PORT_ROBOT)

    while True:
        people_list = proxy_memory.getData("PeoplePerception/PeopleList")
        candidate_keys = proxy_memory.getDataList("PeoplePerception/Person")
        for person in people_list:
            print str(proxy_memory.getData("PeoplePerception/Person/{}/AgeProperties".format(person)))
            print str(parse_face_expressions(proxy_memory.getData("PeoplePerception/Person/{}/ExpressionProperties".format(person))))
            # print str(proxy_memory.getData("PeoplePerception/Person/{}/SmileProperties".format(person)))

            gaze_direction_key = "PeoplePerception/Person/{}/GazeDirection".format(person)
            # FIXME(TK): gaze detection not working
            if gaze_direction_key in candidate_keys:
                print "looking at robot? {}".format(str(proxy_memory.getData(gaze_direction_key)))
            else:
                print "Unknown gaze"
        time.sleep(1)


def record_limb_trajectory():
    retry_proxy = retry_wrapper(naoqi.ALProxy)

    proxy_motion = retry_proxy("ALMotion", IP_ROBOT, PORT_ROBOT)
    proxy_posture = retry_proxy("ALRobotPosture", IP_ROBOT, PORT_ROBOT)

    proxy_posture.goToPosture("Stand", 0.5)

    for t_remaining in reversed(range(5)):
        time.sleep(1)
        print "Waiting... {}".format(t_remaining)

    # Make joints compliant:
    proxy_motion.setStiffnesses("Body", 0.1)

    # TODO(TK): for 5 seconds, record joint poisitions at high frequency
    t_gesture_begin = time.time()
    pd_gesture = 0.05
    gesture_duration = 5
    recording_speed = 0.2
    waypoints = []
    print("Recording gesture")
    while time.time() - t_gesture_begin < gesture_duration / recording_speed:
        waypoints.append(proxy_motion.getAngles("Body", True))
        time.sleep(pd_gesture / recording_speed)

    # Make joints stiff:
    proxy_posture.goToPosture("Stand", 0.5)
    proxy_motion.setStiffnesses("Body", 1.0)

    for t_remaining in reversed(range(5)):
        time.sleep(1)
        print "Waiting... {}".format(t_remaining)

    print("Replaying gesture")
    for waypoint in waypoints:
        proxy_motion.setAngles("Body", waypoint, 1.0)
        time.sleep(pd_gesture)

    proxy_posture.goToPosture("Stand", 0.5)


def get_video():
    pass



def main():
    # initialize_robot()

    # speech()
    # posture()
    # joint_angles()

    # people_perception()
    # face_characteristics()
    record_limb_trajectory()
    # get_video()

    # events_and_callbacks_naoqi()
    # events_and_callbacks_qi_framework()


if __name__ == "__main__":
    main()
