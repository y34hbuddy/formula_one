"""Handles the data layer for formula_one integration."""
import datetime
import json
from json import JSONDecodeError
import logging
import requests
import time

DOMAIN = "formula_one"

_LOGGER = logging.getLogger(DOMAIN)

KEY_DRIVERS = "drivers"
KEY_CONSTRUCTORS = "constructors"
KEY_SEASON = "season"

URL_DRIVERS = "http://ergast.com/api/f1/current/driverStandings.json"
URL_CONSTRUCTORS = "http://ergast.com/api/f1/current/constructorStandings.json"
URL_SEASON = "http://ergast.com/api/f1/current.json"

ERR_JSON_DRIVERS = '{"StandingsTable":{"season":"error","StandingsLists":[{"season":"error","round":"error","DriverStandings":[{"position":"1","positionText":"1","points":"error","wins":"error","Driver":{"driverId":"error","givenName":"error","familyName":"error","nationality":"error"},"Constructors":[{"constructorId":"error","name":"error","nationality":"error"}]}]}]}}'
ERR_JSON_CONSTRUCTORS = '{"StandingsTable":{"season":"error","StandingsLists":[{"season":"error","round":"1","ConstructorStandings":[{"position":"1","positionText":"1","points":"0","wins":"0","Constructor":{"constructorId":"error","url":"error","name":"error","nationality":"error"}}]}]}}'
ERR_JSON_SEASON = '{"xmlns":"http://ergast.com/mrd/1.5","series":"f1","url":"http://ergast.com/api/f1/current.json","limit":"30","offset":"0","total":"1","RaceTable":{"season":"error","Races":[{"season":"error","round":"1","url":"error","raceName":"error","Circuit":{"circuitId":"error","url":"error","circuitName":"error","Location":{"lat":"error","long":"error","locality":"error","country":"error"}},"date":"2022-03-20","time":"15:00:00Z","FirstPractice":{"date":"2022-03-18","time":"12:00:00Z"},"SecondPractice":{"date":"2022-03-18","time":"15:00:00Z"},"ThirdPractice":{"date":"2022-03-19","time":"12:00:00Z"},"Qualifying":{"date":"2022-03-19","time":"15:00:00Z"}}]}}'


class F1Data:
    """Holds the JSON strings for each data set"""

    def __init__(self):
        self.data = {}
        self.data[KEY_DRIVERS] = ""
        self.data[KEY_CONSTRUCTORS] = ""
        self.data[KEY_SEASON] = ""


class F1DataHandler:
    """Handles exchange with F1 data"""

    def __init__(self, hass):
        self.hass = hass

    def download_update_once(self, update_type):
        """Fetches a single update."""
        _LOGGER.info("Fetching an update of %s", update_type)

        url = ""
        if update_type == KEY_DRIVERS:
            url = URL_DRIVERS
        elif update_type == KEY_CONSTRUCTORS:
            url = URL_CONSTRUCTORS
        else:
            url = URL_SEASON

        req = requests.get(url)
        self.hass.data[DOMAIN].data[update_type] = req.text

    def download_update_once_drivers(self):
        """Fetches a single update of driver data."""
        return self.download_update_once(KEY_DRIVERS)

    def download_update_once_constructors(self):
        """Fetches a single update of constructor data."""
        self.download_update_once(KEY_CONSTRUCTORS)

    def download_update_once_season(self):
        """Fetches a single update of season data."""
        self.download_update_once(KEY_SEASON)

    def download_update_regularly(self, url, update_type, freq):
        """Launches an async task that downloads an update from the hosted data regularly."""
        _LOGGER.info("Updating %s every %s seconds", update_type, str(freq))
        while 1:
            time.sleep(freq)
            self.download_update_once(update_type)

    def download_update_regularly_drivers(self, freq):
        """Launches an async task that downloads an update from the hosted driver data regularly."""
        self.download_update_regularly(URL_DRIVERS, KEY_DRIVERS, freq)

    def download_update_regularly_constructors(self, freq):
        """Launches an async task that downloads an update from the hosted constructor data regularly."""
        self.download_update_regularly(URL_CONSTRUCTORS, KEY_CONSTRUCTORS, freq)

    def download_update_regularly_season(self, freq):
        """Launches an async task that downloads an update from the hosted season data regularly."""
        self.download_update_regularly(URL_SEASON, KEY_SEASON, freq)

    def get_drivers_constructors_update(self, update_type):
        """Fetches the update from the cache."""

        err_json = (
            ERR_JSON_DRIVERS if update_type == KEY_DRIVERS else ERR_JSON_CONSTRUCTORS
        )

        try:
            thejson = json.loads(self.hass.data[DOMAIN].data[update_type])
            return thejson["MRData"]

        except JSONDecodeError as error:
            _LOGGER.error(
                "Failed to read cache of F1 %s data: %s",
                update_type,
                error.msg,
            )
            return json.loads(err_json)

    def get_drivers_update(self):
        """Fetches the update from the cache."""
        return self.get_drivers_constructors_update(KEY_DRIVERS)

    def get_driver_count(self):
        """Gets the total number of drivers in the source data."""
        return int(self.get_drivers_update()["total"])

    def get_update_for_drivers_place(self, place):
        """Fetches data for a specific place in the standings."""

        update = self.get_drivers_update()
        driver_data = update["StandingsTable"]["StandingsLists"][0]["DriverStandings"][
            place - 1
        ]
        ret = {}
        ret["driver"] = (
            driver_data["Driver"]["givenName"]
            + " "
            + driver_data["Driver"]["familyName"]
        )
        ret["points"] = driver_data["points"]
        ret["nationality"] = driver_data["Driver"]["nationality"]
        ret["team"] = driver_data["Constructors"][0]["name"]
        ret["driverId"] = driver_data["Driver"]["driverId"]
        ret["season"] = update["StandingsTable"]["season"]
        ret["place"] = place

        return ret

    def get_constructors_update(self):
        """Fetches the update from the cache."""
        return self.get_drivers_constructors_update(KEY_CONSTRUCTORS)

    def get_constructor_count(self):
        """Gets the total number of drivers in the source data."""
        return int(self.get_constructors_update()["total"])

    def get_update_for_constructors_place(self, place):
        """Fetches data for a specific place in the standings."""

        update = self.get_constructors_update()
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

    def get_season_update(self):
        """Fetches the update from the cache."""

        try:
            thejson = json.loads(self.hass.data[DOMAIN].data[KEY_SEASON])
            return thejson["MRData"]

        except JSONDecodeError as error:
            _LOGGER.error(
                "Failed to JSON-decode cache of F1 season data: %s", error.msg
            )
            return json.loads(ERR_JSON_SEASON)

    def get_race_count(self):
        """Gets the total number of races in the source data."""
        return int(self.get_season_update()["total"])

    def get_next_race_round(self):
        """Gets the next race round."""

        current_date = datetime.datetime.now(datetime.timezone.utc).replace(
            tzinfo=datetime.timezone.utc
        )
        races = self.get_season_update()["RaceTable"]["Races"]
        for race in races:
            the_time = race["time"][:-1]
            date_time_str = race["date"] + " " + the_time + " UTC"
            race_date_time = datetime.datetime.strptime(
                date_time_str, "%Y-%m-%d %H:%M:%S %Z"
            ).replace(tzinfo=datetime.timezone.utc)

            if race_date_time >= current_date:
                return int(race["round"])

        return self.get_race_count()

    def get_update_for_race(self, race):
        """Fetches data for a specific race."""

        this_race_update = self.get_season_update()["RaceTable"]["Races"][race - 1]

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
