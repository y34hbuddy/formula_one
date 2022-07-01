"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import const, f1_update

import threading

KEY_DRIVERS = const.KEY_DRIVERS
KEY_CONSTRUCTORS = const.KEY_CONSTRUCTORS
KEY_SEASON = const.KEY_SEASON


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

    hass.data[const.DOMAIN] = f1_update.F1Data()
    f1_data_handler = f1_update.F1DataHandler(hass)

    f1_data_handler.download_update_once(KEY_DRIVERS)
    f1_data_handler.download_update_once(KEY_CONSTRUCTORS)
    f1_data_handler.download_update_once(KEY_SEASON)

    driver_count = f1_data_handler.get_driver_count()
    constructor_count = f1_data_handler.get_constructor_count()
    race_count = f1_data_handler.get_race_count()

    thread_drivers = threading.Thread(
        target=f1_data_handler.download_update_regularly,
        args=(
            KEY_DRIVERS,
            cfg_update_frequency_sec,
        ),
        daemon=True,
    )
    thread_drivers.start()

    thread_constructors = threading.Thread(
        target=f1_data_handler.download_update_regularly,
        args=(
            KEY_CONSTRUCTORS,
            cfg_update_frequency_sec,
        ),
        daemon=True,
    )
    thread_constructors.start()

    thread_season = threading.Thread(
        target=f1_data_handler.download_update_regularly,
        args=(
            KEY_SEASON,
            cfg_update_frequency_sec,
        ),
        daemon=True,
    )
    thread_season.start()

    entities_to_add = [
        F1NextRaceNameSensor(f1_data_handler),
        F1NextRaceDateSensor(f1_data_handler),
    ]

    for i in range(1, driver_count + 1):
        entities_to_add.append(F1DriversSensor(f1_data_handler, i))

    for i in range(1, constructor_count + 1):
        entities_to_add.append(F1ConstructorsSensor(f1_data_handler, i))

    for i in range(1, race_count + 1):
        entities_to_add.append(F1RaceSensor(f1_data_handler, i))

    add_entities(entities_to_add)


class F1DriversSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, f1_data_handler, driver_num) -> None:
        super().__init__()

        self.driver_num = driver_num
        self.f1_data_handler = f1_data_handler

        self._attr_name = "F1 Driver "
        if driver_num < 10:
            self._attr_name += "0"
        self._attr_name += str(driver_num)

        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""

        driver_data = self.f1_data_handler.get_update_for_drivers_place(self.driver_num)
        ret = {}
        ret["points"] = driver_data["points"]
        ret["nationality"] = driver_data["nationality"]
        ret["team"] = driver_data["team"]
        ret["driverId"] = driver_data["driverId"]
        ret["season"] = driver_data["season"]
        ret["place"] = driver_data["place"]
        return ret

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        driver_data = self.f1_data_handler.get_update_for_drivers_place(self.driver_num)
        self._attr_native_value = driver_data["driver"]


class F1ConstructorsSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, f1_data_handler, constructor_num) -> None:
        super().__init__()

        self.constructor_num = constructor_num
        self.f1_data_handler = f1_data_handler

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

        constructor_data = self.f1_data_handler.get_update_for_constructors_place(
            self.constructor_num
        )
        ret = {}
        ret["points"] = constructor_data["points"]
        ret["nationality"] = constructor_data["nationality"]
        ret["constructorId"] = constructor_data["constructorId"]
        ret["season"] = constructor_data["season"]
        ret["place"] = constructor_data["place"]
        return ret

    def update(self) -> None:
        """Fetch new state data for the sensor."""

        constructor_data = self.f1_data_handler.get_update_for_constructors_place(
            self.constructor_num
        )
        self._attr_native_value = constructor_data["constructor"]


class F1NextRaceNameSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, f1_data_handler) -> None:
        super().__init__()
        self.f1_data_handler = f1_data_handler
        self._attr_name = "F1 Next Race Name"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = None

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        race_data = self.f1_data_handler.get_update_for_race(
            self.f1_data_handler.get_next_race_round()
        )
        self._attr_native_value = race_data["raceName"]


class F1NextRaceDateSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, f1_data_handler) -> None:
        super().__init__()
        self.f1_data_handler = f1_data_handler
        self._attr_name = "F1 Next Race Date"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = None

    def update(self) -> None:
        """Fetch new state data for the sensor."""

        race_data = self.f1_data_handler.get_update_for_race(
            self.f1_data_handler.get_next_race_round()
        )
        self._attr_native_value = race_data["date"] + "T" + race_data["time"]


class F1RaceSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, f1_data_handler, race_num) -> None:
        super().__init__()

        self.race_num = race_num
        self.f1_data_handler = f1_data_handler

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

        race_data = self.f1_data_handler.get_update_for_race(self.race_num)
        ret = {}
        ret["season"] = race_data["season"]
        ret["round"] = race_data["round"]
        ret["date"] = race_data["date"]
        ret["time"] = race_data["time"]
        ret["fp1_date"] = race_data["fp1_date"]
        ret["fp1_time"] = race_data["fp1_time"]
        ret["fp2_date"] = race_data["fp2_date"]
        ret["fp2_time"] = race_data["fp2_time"]

        if "fp3_date" in race_data:
            ret["fp3_date"] = race_data["fp3_date"]
            ret["fp3_time"] = race_data["fp3_time"]

        ret["qual_date"] = race_data["qual_date"]
        ret["qual_time"] = race_data["qual_time"]

        if "sprint_date" in race_data:
            ret["sprint_date"] = race_data["sprint_date"]
            ret["sprint_time"] = race_data["sprint_time"]

        return ret

    def update(self) -> None:
        """Fetch new state data for the sensor."""

        race_data = self.f1_data_handler.get_update_for_race(self.race_num)
        self._attr_native_value = race_data["raceName"]
