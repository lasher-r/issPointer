from dataclasses import dataclass
import json
import os
import requests

api_key = os.environ['ISS_API_KEY']


@dataclass
class SatellitePos:
    satlatitude: float
    satlongitude: float
    sataltitude: float
    azimuth: float
    elevation: float
    ra: float
    dec: float
    timestamp: float


def getSatellitePos(obsLat, obsLng, obsAlt, satId="25544", secs="60"):
            # id #lat #lng #alt #secs
    args = "{}/{}/{}/{}/{}/&apiKey={}".format(satId, obsLat, obsLng, obsAlt, secs, api_key)
    url = "https://www.n2yo.com/rest/v1/satellite/positions/{}".format(args)
    r = requests.get(url)
    print(r.text)
    pass


if __name__ == '__main__':
    denLat = "39.910154"
    denLng = "-105.073380"
    denAlt = "5280"
    getSatellitePos(denLat, denLng, denAlt)
