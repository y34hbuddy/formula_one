"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import f1_update

import threading


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    cfg_update_frequency_sec = 300

    if "update_frequency_sec" in config.keys():
        cfg_update_frequency_sec = config["update_frequency_sec"]

    f1_update.download_update_once(
        "http://ergast.com/api/f1/current/driverStandings.json", "f1_drivers.json"
    )
    f1_update.download_update_once(
        "http://ergast.com/api/f1/current/constructorStandings.json",
        "f1_constructors.json",
    )
    f1_update.download_update_once(
        "http://ergast.com/api/f1/current.json", "f1_season.json"
    )

    driver_count = f1_update.get_driver_count()
    constructor_count = f1_update.get_constructor_count()
    race_count = f1_update.get_race_count()

    thread_drivers = threading.Thread(
        target=f1_update.download_update_regularly,
        args=(
            "http://ergast.com/api/f1/current/driverStandings.json",
            "f1_drivers.json",
            cfg_update_frequency_sec,
        ),
        daemon=True,
    )
    thread_drivers.start()

    thread_constructors = threading.Thread(
        target=f1_update.download_update_regularly,
        args=(
            "http://ergast.com/api/f1/current/constructorStandings.json",
            "f1_constructors.json",
            cfg_update_frequency_sec,
        ),
        daemon=True,
    )
    thread_constructors.start()

    thread_season = threading.Thread(
        target=f1_update.download_update_regularly,
        args=(
            "http://ergast.com/api/f1/current.json",
            "f1_season.json",
            cfg_update_frequency_sec,
        ),
        daemon=True,
    )
    thread_season.start()

    entities_to_add = [F1NextRaceNameSensor(), F1NextRaceDateSensor()]

    for i in range(1, driver_count + 1):
        entities_to_add.append(F1DriversSensor(i))

    for i in range(1, constructor_count + 1):
        entities_to_add.append(F1ConstructorsSensor(i))

    for i in range(1, race_count + 1):
        entities_to_add.append(F1RaceSensor(i))

    add_entities(entities_to_add)


class F1DriversSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, driver_num) -> None:
        super().__init__()

        self.driver_num = driver_num

        attr_name = "F1 Driver "

        if driver_num < 10:
            attr_name += "0"

        attr_name += str(driver_num)

        self._attr_name = attr_name
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        stuff = f1_update.get_update_for_drivers_place(self.driver_num)
        ret = {}
        ret["points"] = stuff["points"]
        ret["nationality"] = stuff["nationality"]
        ret["team"] = stuff["team"]
        ret["driverId"] = stuff["driverId"]
        ret["season"] = stuff["season"]
        ret["place"] = stuff["place"]
        return ret

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        stuff = f1_update.get_update_for_drivers_place(self.driver_num)
        self._attr_native_value = stuff["driver"]


class F1ConstructorsSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, constructor_num) -> None:
        super().__init__()

        self.constructor_num = constructor_num

        attr_name = "F1 Constructor "

        if constructor_num < 10:
            attr_name += "0"

        attr_name += str(constructor_num)

        self._attr_name = attr_name
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        stuff = f1_update.get_update_for_constructors_place(self.constructor_num)
        ret = {}
        ret["points"] = stuff["points"]
        ret["nationality"] = stuff["nationality"]
        ret["constructorId"] = stuff["constructorId"]
        ret["season"] = stuff["season"]
        ret["place"] = stuff["place"]
        return ret

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        stuff = f1_update.get_update_for_constructors_place(self.constructor_num)
        self._attr_native_value = stuff["constructor"]


class F1NextRaceNameSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "F1 Next Race Name"
    _attr_native_unit_of_measurement = None
    _attr_device_class = None
    _attr_state_class = None

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        stuff = f1_update.get_update_for_race(f1_update.get_next_race_round())
        self._attr_native_value = stuff["raceName"]


class F1NextRaceDateSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "F1 Next Race Date"
    _attr_native_unit_of_measurement = None
    _attr_device_class = None
    _attr_state_class = None

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        stuff = f1_update.get_update_for_race(f1_update.get_next_race_round())
        self._attr_native_value = stuff["date"] + "T" + stuff["time"]


class F1RaceSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, race_num) -> None:
        super().__init__()

        self.race_num = race_num

        attr_name = "F1 Race "

        if race_num < 10:
            attr_name += "0"

        attr_name += str(race_num)

        self._attr_name = attr_name
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        stuff = f1_update.get_update_for_race(self.race_num)
        ret = {}
        ret["season"] = stuff["season"]
        ret["round"] = stuff["round"]
        ret["date"] = stuff["date"]
        ret["time"] = stuff["time"]
        ret["fp1_date"] = stuff["fp1_date"]
        ret["fp1_time"] = stuff["fp1_time"]
        ret["fp2_date"] = stuff["fp2_date"]
        ret["fp2_time"] = stuff["fp2_time"]

        if "fp3_date" in stuff:
            ret["fp3_date"] = stuff["fp3_date"]
            ret["fp3_time"] = stuff["fp3_time"]

        ret["qual_date"] = stuff["qual_date"]
        ret["qual_time"] = stuff["qual_time"]

        if "sprint_date" in stuff:
            ret["sprint_date"] = stuff["sprint_date"]
            ret["sprint_time"] = stuff["sprint_time"]

        return ret

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        stuff = f1_update.get_update_for_race(self.race_num)
        self._attr_native_value = stuff["raceName"]
