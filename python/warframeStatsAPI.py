from pprint import pprint

import requests
import zulu

base_uri = "https://api.warframestat.us/pc/"


def validate(req):
    if req.status_code == 200:
        return True
    else:
        return False


def getCetusTime():
    uri = base_uri + "cetusCycle"
    r = requests.get(uri)
    if validate(r):
        stamp = r.json()['expiry']
        now = zulu.now()
        dt = zulu.parse(stamp)
        delta = zulu.parse_delta(dt.subtract(now))
        dFormat = str(zulu.parse(delta).format("H") + "h " + zulu.parse(delta).format("m") + "m")
        if zulu.parse(delta).format("H") == "0":
            dFormat = str(zulu.parse(delta).format("m") + " minutes")
        return dFormat, r.json()['isDay']
    else:
        return "404 Time", "404 isDay"


def getEarthTime():
    uri = base_uri + "earthCycle"
    r = requests.get(uri)
    if validate(r):
        stamp = r.json()['expiry']
        now = zulu.now()
        dt = zulu.parse(stamp)
        delta = zulu.parse_delta(dt.subtract(now))
        dFormat = str(zulu.parse(delta).format("H") + "h " + zulu.parse(delta).format("m") + "m")
        if zulu.parse(delta).format("H") == "0":
            dFormat = str(zulu.parse(delta).format("m") + " minutes")
        return dFormat, r.json()['isDay']
    else:
        return "404 Time", "404 isDay"


def getVallisTime():
    uri = base_uri + "vallisCycle"
    r = requests.get(uri)
    if validate(r):
        stamp = r.json()['expiry']
        now = zulu.now()
        dt = zulu.parse(stamp)
        delta = zulu.parse_delta(dt.subtract(now)).format(threshold=155, granularity='minute', locale='en_US_POSIX')
        return delta, r.json()['isWarm']
    else:
        return "404 Time", "404 isWarm"


def getCambionTime():
    uri = base_uri + "cambionCycle"
    r = requests.get(uri)
    if validate(r):
        stamp = r.json()['expiry']
        now = zulu.now()
        dt = zulu.parse(stamp)
        delta = zulu.parse_delta(dt.subtract(now))
        dFormat = str(zulu.parse(delta).format("H") + "h " + zulu.parse(delta).format("m") + "m")
        if zulu.parse(delta).format("H") == "0":
            dFormat = str(zulu.parse(delta).format("m") + " minutes")
        return dFormat, r.json()['active']
    else:
        return "404 Time", "404 active"


def getCurrentSortie():
    uri = base_uri + "sortie"
    r = requests.get(uri)
    if validate(r):
        stamp = r.json()['expiry']
        now = zulu.now()
        dt = zulu.parse(stamp)
        delta = zulu.parse_delta(dt.subtract(now))
        dFormat = str(zulu.parse(delta).format("H") + "h " + zulu.parse(delta).format("m") + "m")
        if zulu.parse(delta).format("H") == "0":
            dFormat = str(zulu.parse(delta).format("m") + " minutes")

        missions = []
        for missionInformation in r.json()['variants']:
            missions.append(missionInformation)

        return dFormat, missions, r.json()['boss']
    else:
        return "404 Time", "404 missions", "404 boss"


def getCurrentEvent():
    uri = base_uri + "events"
    r = requests.get(uri)
    events = []
    if validate(r):
        for event in r.json():
            description = event['description']

            iStep = []
            for inter in event['interimSteps']:
                if not inter['reward'] == []:
                    iStep.append(inter['reward']['asString'])

            r = []
            for rewards in event['rewards']:
                if not rewards['items'] == []:
                    r.append(rewards['asString'])
            try:
                tooltip = event['tooltip']
            except KeyError:
                tooltip = ""

            stamp = event['expiry']
            now = zulu.now()
            dt = zulu.parse(stamp)
            delta = zulu.parse_delta(dt.subtract(now))
            dFormat = str(str(int(zulu.parse(delta).format("D")) - 1) + "d " + zulu.parse(delta).format("H") + "h "
                          + zulu.parse(delta).format("m") + "m")
            if zulu.parse(delta).format("H") == "0" and zulu.parse(delta).format("D") == "0":
                dFormat = str(zulu.parse(delta).format("m") + " minutes")

            events.append((dFormat, description, tooltip, r, iStep))
        return events
    return []