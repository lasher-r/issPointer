import os
import queue
import requests
import threading
import time

api_key = os.environ['ISS_API_KEY']
MAX_QUEUE_SIZE = 3600  # one hour of data
positionsQueue = queue.Queue(MAX_QUEUE_SIZE)


# get satellite data from api.  25544 is the iss code
# altitude in meters. 
# gets secs worth of data.
# puts it into the position queue
def getSatellitePos(obsLat, obsLng, obsAlt, satId="25544", secs="60"):
    while 1:
            # id #lat #lng #alt #secs
        args = "{}/{}/{}/{}/{}/&apiKey={}".format(satId, obsLat, obsLng, obsAlt, secs, api_key)
        url = "https://www.n2yo.com/rest/v1/satellite/positions/{}".format(args)
        r = requests.get(url)
        resultPosLst = r.json()['positions']
        for pos in resultPosLst:
            positionsQueue.put(pos)

        time.sleep(2 * int(secs) / 3)


# Consumes data from the positions queue.
# gets azimuth and altitude for current time.
# 
def pointerLoop():
    pos = positionsQueue.get()
    while 1:
        time.sleep(1)
        while int(time.time()) != pos['timestamp']:
            pos = positionsQueue.get()
        print("az: {}\talt: {}\tts: {}".format(pos['azimuth'], pos['elevation'], pos['timestamp']))


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

    print(positionsQueue.qsize())
