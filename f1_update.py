"""Handles the data layer for formula_one integration."""
import datetime
import json
from json import JSONDecodeError
import logging
import os
import requests
import time

_LOGGER = logging.getLogger("formula_one")

URL_DRIVERS = "http://ergast.com/api/f1/current/driverStandings.json"
URL_CONSTRUCTORS = "http://ergast.com/api/f1/current/constructorStandings.json"
URL_SEASON = "http://ergast.com/api/f1/current.json"
FILENAME_DRIVERS = "f1_drivers.json"
FILENAME_CONSTRUCTORS = "f1_constructors.json"
FILENAME_SEASON = "f1_season.json"


def get_filepath(filename):
    """Gets the filepath for the cache files"""
    cwd = os.getcwd().removeprefix("/config")
    return cwd + "/config/custom_components/formula_one/" + filename


def download_update_once(url, filename):
    """Fetches a single update."""
    _LOGGER.info("Fetching an update of %s", filename)
    try:
        req = requests.get(url)

        cache_file = open(
            get_filepath(filename),
            mode="w",
            encoding="utf_8",
        )
        cache_file.write(req.text)
        cache_file.close()

    except BlockingIOError as error:
        _LOGGER.error(
            "Failed to fetch/cache update of %s: %s", filename, error.strerror
        )
    except OSError as error:
        _LOGGER.error(
            "Failed to fetch/cache update of %s: %s", filename, error.strerror
        )


def download_update_once_drivers():
    """Fetches a single update of driver data."""
    download_update_once(URL_DRIVERS, FILENAME_DRIVERS)


def download_update_once_constructors():
    """Fetches a single update of constructor data."""
    download_update_once(URL_CONSTRUCTORS, FILENAME_CONSTRUCTORS)


def download_update_once_season():
    """Fetches a single update of season data."""
    download_update_once(URL_SEASON, FILENAME_SEASON)


def download_update_regularly(url, filename, freq):
    """Launches an async task that downloads an update from the hosted data regularly."""
    _LOGGER.info("Updating %s every %s seconds", filename, str(freq))
    while 1:
        time.sleep(freq)
        download_update_once(url, filename)


def download_update_regularly_drivers(freq):
    """Launches an async task that downloads an update from the hosted driver data regularly."""
    download_update_regularly(URL_DRIVERS, FILENAME_DRIVERS, freq)


def download_update_regularly_constructors(freq):
    """Launches an async task that downloads an update from the hosted constructor data regularly."""
    download_update_regularly(URL_CONSTRUCTORS, FILENAME_CONSTRUCTORS, freq)


def download_update_regularly_season(freq):
    """Launches an async task that downloads an update from the hosted season data regularly."""
    download_update_regularly(URL_SEASON, FILENAME_SEASON, freq)


def get_drivers_update():
    """Fetches the update from the cache."""
    try:
        with open(
            get_filepath(FILENAME_DRIVERS),
            encoding="utf_8",
        ) as cache_file:
            lines = cache_file.read()
        thejson = json.loads(lines)
        return thejson["MRData"]

    except OSError as error:
        _LOGGER.error("Failed to read cache of F1 driver data: %s", error.strerror)
        return json.loads(
            '{"StandingsTable":{"season":"error","StandingsLists":[{"season":"error","round":"error","DriverStandings":[{"position":"1","positionText":"1","points":"error","wins":"error","Driver":{"driverId":"error","givenName":"error","familyName":"error","nationality":"error"},"Constructors":[{"constructorId":"error","name":"error","nationality":"error"}]}]}]}}'
        )
    except JSONDecodeError as error:
        _LOGGER.error("Failed to read cache of F1 driver data: %s", error.msg)
        return json.loads(
            '{"StandingsTable":{"season":"error","StandingsLists":[{"season":"error","round":"error","DriverStandings":[{"position":"1","positionText":"1","points":"error","wins":"error","Driver":{"driverId":"error","givenName":"error","familyName":"error","nationality":"error"},"Constructors":[{"constructorId":"error","name":"error","nationality":"error"}]}]}]}}'
        )


def get_driver_count():
    """Gets the total number of drivers in the source data."""
    update = get_drivers_update()["StandingsTable"]["StandingsLists"][0][
        "DriverStandings"
    ]
    return len(update)


def get_update_for_drivers_place(place):
    """Fetches data for a specific place in the standings."""
    update = get_drivers_update()
    driver_data = update["StandingsTable"]["StandingsLists"][0]["DriverStandings"][
        place - 1
    ]
    ret = {}
    ret["driver"] = (
        driver_data["Driver"]["givenName"] + " " + driver_data["Driver"]["familyName"]
    )
    ret["points"] = driver_data["points"]
    ret["nationality"] = driver_data["Driver"]["nationality"]
    ret["team"] = driver_data["Constructors"][0]["name"]
    ret["driverId"] = driver_data["Driver"]["driverId"]
    ret["season"] = update["StandingsTable"]["season"]
    ret["place"] = place

    return ret


def get_constructors_update():
    """Fetches the update from the cache."""
    try:
        with open(
            get_filepath(FILENAME_CONSTRUCTORS),
            encoding="utf_8",
        ) as cache_file:
            lines = cache_file.read()
        thejson = json.loads(lines)
        return thejson["MRData"]
    except OSError as error:
        _LOGGER.error("Failed to read cache of F1 constructor data: %s", error.strerror)
        return json.loads(
            '{"StandingsTable":{"season":"error","StandingsLists":[{"season":"error","round":"1","ConstructorStandings":[{"position":"1","positionText":"1","points":"0","wins":"0","Constructor":{"constructorId":"error","url":"error","name":"error","nationality":"error"}}]}]}}'
        )
    except JSONDecodeError as error:
        _LOGGER.error("Failed to read cache of F1 constructor data: %s", error.msg)
        return json.loads(
            '{"StandingsTable":{"season":"error","StandingsLists":[{"season":"error","round":"1","ConstructorStandings":[{"position":"1","positionText":"1","points":"0","wins":"0","Constructor":{"constructorId":"error","url":"error","name":"error","nationality":"error"}}]}]}}'
        )


def get_constructor_count():
    """Gets the total number of drivers in the source data."""
    update = get_constructors_update()["StandingsTable"]["StandingsLists"][0][
        "ConstructorStandings"
    ]
    return len(update)


def get_update_for_constructors_place(place):
    """Fetches data for a specific place in the standings."""
    update = get_constructors_update()
    constructor_data = update["StandingsTable"]["StandingsLists"][0][
        "ConstructorStandings"
    ][place - 1]
    ret = {}
    ret["constructor"] = constructor_data["Constructor"]["name"]
    ret["points"] = constructor_data["points"]
    ret["nationality"] = constructor_data["Constructor"]["nationality"]
    ret["constructorId"] = constructor_data["Constructor"]["constructorId"]
    ret["season"] = update["StandingsTable"]["season"]
    ret["place"] = place

    return ret


def get_season_update():
    """Fetches the update from the cache."""
    try:
        with open(
            get_filepath(FILENAME_SEASON),
            encoding="utf_8",
        ) as cache_file:
            lines = cache_file.read()
        thejson = json.loads(lines)
        return thejson["MRData"]

    except OSError as error:
        _LOGGER.error("Failed to read cache of F1 season data: %s", error.strerror)
        return json.loads(
            '{"xmlns":"http://ergast.com/mrd/1.5","series":"f1","url":"http://ergast.com/api/f1/current.json","limit":"30","offset":"0","total":"1","RaceTable":{"season":"error","Races":[{"season":"error","round":"1","url":"error","raceName":"error","Circuit":{"circuitId":"error","url":"error","circuitName":"error","Location":{"lat":"error","long":"error","locality":"error","country":"error"}},"date":"2022-03-20","time":"15:00:00Z","FirstPractice":{"date":"2022-03-18","time":"12:00:00Z"},"SecondPractice":{"date":"2022-03-18","time":"15:00:00Z"},"ThirdPractice":{"date":"2022-03-19","time":"12:00:00Z"},"Qualifying":{"date":"2022-03-19","time":"15:00:00Z"}}]}}'
        )
    except JSONDecodeError as error:
        _LOGGER.error("Failed to JSON-decode cache of F1 season data: %s", error.msg)
        return json.loads(
            '{"xmlns":"http://ergast.com/mrd/1.5","series":"f1","url":"http://ergast.com/api/f1/current.json","limit":"30","offset":"0","total":"1","RaceTable":{"season":"error","Races":[{"season":"error","round":"1","url":"error","raceName":"error","Circuit":{"circuitId":"error","url":"error","circuitName":"error","Location":{"lat":"error","long":"error","locality":"error","country":"error"}},"date":"2022-03-20","time":"15:00:00Z","FirstPractice":{"date":"2022-03-18","time":"12:00:00Z"},"SecondPractice":{"date":"2022-03-18","time":"15:00:00Z"},"ThirdPractice":{"date":"2022-03-19","time":"12:00:00Z"},"Qualifying":{"date":"2022-03-19","time":"15:00:00Z"}}]}}'
        )


def get_race_count():
    """Gets the total number of races in the source data."""
    return int(get_season_update()["total"])


def get_next_race_round():
    """Gets the next race round."""
    current_date = datetime.datetime.now(datetime.timezone.utc)
    current_date = current_date.replace(tzinfo=datetime.timezone.utc)
    races = get_season_update()["RaceTable"]["Races"]
    for race in races:
        the_time = race["time"][:-1]
        date_time_str = race["date"] + " " + the_time + " UTC"
        race_date_time = datetime.datetime.strptime(
            date_time_str, "%Y-%m-%d %H:%M:%S %Z"
        )
        race_date_time = race_date_time.replace(tzinfo=datetime.timezone.utc)

        if race_date_time >= current_date:
            return int(race["round"])

    return get_race_count()


def get_update_for_race(race):
    """Fetches data for a specific race."""
    update = get_season_update()
    this_race_update = update["RaceTable"]["Races"][race - 1]

    ret = {}
    ret["raceName"] = this_race_update["raceName"]
    ret["season"] = this_race_update["season"]
    ret["round"] = this_race_update["round"]
    ret["date"] = this_race_update["date"]
    ret["time"] = this_race_update["time"]
    ret["fp1_date"] = this_race_update["FirstPractice"]["date"]
    ret["fp1_time"] = this_race_update["FirstPractice"]["time"]
    ret["fp2_date"] = this_race_update["SecondPractice"]["date"]
    ret["fp2_time"] = this_race_update["SecondPractice"]["time"]

    if "ThirdPractice" in this_race_update:
        ret["fp3_date"] = this_race_update["ThirdPractice"]["date"]
        ret["fp3_time"] = this_race_update["ThirdPractice"]["time"]

    ret["qual_date"] = this_race_update["Qualifying"]["date"]
    ret["qual_time"] = this_race_update["Qualifying"]["time"]

    if "Sprint" in this_race_update:
        ret["sprint_date"] = this_race_update["Sprint"]["date"]
        ret["sprint_time"] = this_race_update["Sprint"]["time"]

    return ret
