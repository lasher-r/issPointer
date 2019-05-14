#!/usr/bin/python3

import os
import queue
import requests
import sys
import threading
import time

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

API_KEY = os.environ['ISS_API_KEY']
MAX_QUEUE_SIZE = 3600  # one hour of data
STEPPER_RESOLUTION = 0.1125  # 0.1125 for micro step, 1.8 for whole step
UPDATE_RESOLUTION = 1  # num of seconds between moving the pointer

positionsQueue = queue.Queue(MAX_QUEUE_SIZE)
motors = MotorKit()


# get satellite data from api.  25544 is the iss code
# altitude in meters.
# gets secs worth of data.
# puts it into the position queue
def getSatellitePos(obsLat, obsLng, obsAlt, satId="25544", secs="60"):
    while 1:
            # id #lat #lng #alt #secs
        args = "{}/{}/{}/{}/{}/&apiKey={}".format(satId, obsLat, obsLng, obsAlt, secs, API_KEY)
        url = "https://www.n2yo.com/rest/v1/satellite/positions/{}".format(args)
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(e)
            time.sleep(30)
            continue

        response = r.json()
        if 'positions' not in response:
            continue

        resultPosLst = response['positions']
        for pos in resultPosLst:
            positionsQueue.put(pos)

        time.sleep(2 * int(secs) / 3)


def stepsFromDeg(angle):
    return angle / STEPPER_RESOLUTION


def degFromSteps(steps):
    return steps * STEPPER_RESOLUTION


def shortAngle(angle):
    shortAngle = angle
    if angle > 180:
        shortAngle = angle - 360
    if angle < -180:
        shortAngle = angle + 360
    return shortAngle


# returns the actual angle the motor is turned to
def setMotor(motor, angle, fromAngle):
    # calc number of [micro]steps and in which direction
    deltAngle = shortAngle(angle - fromAngle)
    numSteps = stepsFromDeg(deltAngle)
    if abs(numSteps) < 1:
        return fromAngle
    direction = stepper.FORWARD
    if numSteps < 0:
        direction = stepper.BACKWARD

    # move motor
    for _ in range(abs(int(numSteps))):
        motor.onestep(direction=direction, style=stepper.MICROSTEP)
        motor.release()

    # calc the angle we actually went
    realSteps = int(numSteps)
    realdAng = degFromSteps(realSteps)
    realAngle = fromAngle + realdAng
    print("motor {} {}=>{} : dAng = {}, steps = {}".format(motor, angle, realAngle, realdAng, realSteps))

    return realAngle


# Consumes data from the positions queue.
# gets azimuth and elevation for current time.
#
def pointerLoop():
    azm = 0.0
    ele = 0.0
    azimuthMotor = motors.stepper1
    elevationMotor = motors.stepper2

    while 1:
        time.sleep(UPDATE_RESOLUTION)

        # this is where i'd put a do...while loop if they existed
        pos = positionsQueue.get()
        while int(time.time()) != pos['timestamp']:
            pos = positionsQueue.get()

        print("az: {}\tele: {}\tts: {}".format(pos['azimuth'], pos['elevation'], pos['timestamp']))

        azm = setMotor(azimuthMotor, pos['azimuth'], azm)
        ele = setMotor(elevationMotor, pos['elevation'], ele)


if __name__ == '__main__':
    denLat = "39.910154"
    denLng = "-105.073380"
    denAlt = "1609"  # meters

    # production thread from api
    apiThread = threading.Thread(target=getSatellitePos, args=(denLat, denLng, denAlt,))
    apiThread.start()

    # consume on main thread
    pointerLoop()

    # never get here
    apiThread.join()
