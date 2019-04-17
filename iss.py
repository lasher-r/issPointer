import os
import queue
import requests
import threading
import time

api_key = os.environ['ISS_API_KEY']
# todo set max size for queue
positionsQueue = queue.SimpleQueue()


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


def pointerLoop():
    pos = positionsQueue.get()
    while 1:
        time.sleep(1)
        while int(time.time()) != pos['timestamp']:
            pos = positionsQueue.get()
        print("{} {}".format(pos, int(time.time())))


if __name__ == '__main__':
    denLat = "39.910154"
    denLng = "-105.073380"
    denAlt = "1609"

    apiThread = threading.Thread(target=getSatellitePos, args=(denLat, denLng, denAlt,))
    apiThread.start()

    pointerLoop()

    apiThread.join()

    print(positionsQueue.qsize())
