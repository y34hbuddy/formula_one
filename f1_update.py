"""Handles the data layer for formula_one integration."""
import datetime
import logging
import requests
import time

from .const import (
    DOMAIN,
    KEY_DRIVERS,
    KEY_CONSTRUCTORS,
    KEY_SEASON,
    URL_DRIVERS,
    URL_CONSTRUCTORS,
    URL_SEASON,
)

_LOGGER = logging.getLogger(DOMAIN)


class F1Data:
    """Holds the JSON objects for each data set"""

    def __init__(self):
        self.data = {}
        self.data[KEY_DRIVERS] = {}
        self.data[KEY_CONSTRUCTORS] = {}
        self.data[KEY_SEASON] = {}


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

        success = False
        while success is False:
            try:
                req = requests.get(url)
                self.hass.data[DOMAIN].data[update_type] = req.json()
                success = True

            except requests.exceptions.JSONDecodeError as err:
                _LOGGER.error(
                    "Failed to decode JSON from source: %s. Trying again in 5 seconds",
                    err.strerror,
                )
                success = False
                time.sleep(5)

    def download_update_regularly(self, update_type, freq):
        """Launches an async task that downloads an update from the hosted data regularly."""
        _LOGGER.info("Updating %s every %s seconds", update_type, str(freq))
        while 1:
            time.sleep(freq)
            self.download_update_once(update_type)

    def get_update(self, update_type):
        """Fetches the update from the cache."""
        return self.hass.data[DOMAIN].data[update_type]["MRData"]

    def get_driver_count(self):
        """Gets the total number of drivers in the source data."""
        return int(self.get_update(KEY_DRIVERS)["total"])

    def get_update_for_drivers_place(self, place):
        """Fetches data for a specific place in the standings."""

        update = self.get_update(KEY_DRIVERS)
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
        ret["round"] = update["StandingsTable"]["StandingsLists"][0]["round"]
        ret["place"] = place

        return ret

    def get_constructor_count(self):
        """Gets the total number of drivers in the source data."""
        return int(self.get_update(KEY_CONSTRUCTORS)["total"])

    def get_update_for_constructors_place(self, place):
        """Fetches data for a specific place in the standings."""

        update = self.get_update(KEY_CONSTRUCTORS)
        constructor_data = update["StandingsTable"]["StandingsLists"][0][
            "ConstructorStandings"
        ][place - 1]
        ret = {}
        ret["constructor"] = constructor_data["Constructor"]["name"]
        ret["points"] = constructor_data["points"]
        ret["nationality"] = constructor_data["Constructor"]["nationality"]
        ret["constructorId"] = constructor_data["Constructor"]["constructorId"]
        ret["season"] = update["StandingsTable"]["season"]
        ret["round"] = update["StandingsTable"]["StandingsLists"][0]["round"]
        ret["place"] = place

        return ret

    def get_race_count(self):
        """Gets the total number of races in the source data."""
        return int(self.get_update(KEY_SEASON)["total"])

    def get_next_race_round(self):
        """Gets the next race round."""

        current_date = datetime.datetime.now(datetime.timezone.utc).replace(
            tzinfo=datetime.timezone.utc
        )
        races = self.get_update(KEY_SEASON)["RaceTable"]["Races"]
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

        this_race_update = self.get_update(KEY_SEASON)["RaceTable"]["Races"][race - 1]

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
