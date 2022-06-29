"""Handles the data layer for formula_one integration."""
import datetime
import json
from json import JSONDecodeError
import os
import requests
import time
import logging

_LOGGER = logging.getLogger("formula_one")


def get_filepath(filename):
    """Gets the filepath for the cache files"""
    cwd = os.getcwd().removeprefix("/config")
    return cwd + "/config/custom_components/formula_one/" + filename


def download_update_once(url, filepath):
    """Fetches a single update."""
    _LOGGER.info("Fetching an update of %s", filepath)
    try:
        req = requests.get(url)

        cache_file = open(
            get_filepath(filepath),
            mode="w",
            encoding="utf_8",
        )
        cache_file.write(req.text)
        cache_file.close()

    except BlockingIOError as error:
        _LOGGER.error(
            "Failed to fetch/cache update of %s: %s", filepath, error.strerror
        )
    except OSError as error:
        _LOGGER.error(
            "Failed to fetch/cache update of %s: %s", filepath, error.strerror
        )


def download_update_regularly(url, filepath, freq):
    """Launches an async task that downloads an update from the hosted data regularly."""
    _LOGGER.info("Updating %s every %s seconds", filepath, str(freq))
    while 1:
        time.sleep(freq)
        download_update_once(url, filepath)


def get_drivers_update():
    """Fetches the update from the cache."""
    try:
        with open(
            get_filepath("f1_drivers.json"),
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
    ret = {}
    ret["driver"] = (
        update["StandingsTable"]["StandingsLists"][0]["DriverStandings"][place - 1][
            "Driver"
        ]["givenName"]
        + " "
        + update["StandingsTable"]["StandingsLists"][0]["DriverStandings"][place - 1][
            "Driver"
        ]["familyName"]
    )
    ret["points"] = update["StandingsTable"]["StandingsLists"][0]["DriverStandings"][
        place - 1
    ]["points"]
    ret["nationality"] = update["StandingsTable"]["StandingsLists"][0][
        "DriverStandings"
    ][place - 1]["Driver"]["nationality"]
    ret["team"] = update["StandingsTable"]["StandingsLists"][0]["DriverStandings"][
        place - 1
    ]["Constructors"][0]["name"]
    ret["driverId"] = update["StandingsTable"]["StandingsLists"][0]["DriverStandings"][
        place - 1
    ]["Driver"]["driverId"]
    ret["season"] = update["StandingsTable"]["season"]
    ret["place"] = place

    return ret


def get_constructors_update():
    """Fetches the update from the cache."""
    try:
        with open(
            get_filepath("f1_constructors.json"),
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
    ret = {}
    ret["constructor"] = update["StandingsTable"]["StandingsLists"][0][
        "ConstructorStandings"
    ][place - 1]["Constructor"]["name"]
    ret["points"] = update["StandingsTable"]["StandingsLists"][0][
        "ConstructorStandings"
    ][place - 1]["points"]
    ret["nationality"] = update["StandingsTable"]["StandingsLists"][0][
        "ConstructorStandings"
    ][place - 1]["Constructor"]["nationality"]
    ret["constructorId"] = update["StandingsTable"]["StandingsLists"][0][
        "ConstructorStandings"
    ][place - 1]["Constructor"]["constructorId"]
    ret["season"] = update["StandingsTable"]["season"]
    ret["place"] = place

    return ret


def get_season_update():
    """Fetches the update from the cache."""
    try:
        with open(
            get_filepath("f1_season.json"),
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
