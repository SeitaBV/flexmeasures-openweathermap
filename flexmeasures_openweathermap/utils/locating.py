from typing import Tuple, List, Optional

import click

from flexmeasures.utils.grid_cells import LatLngGrid, get_cell_nums
from flexmeasures.data.models.time_series import Sensor
from flexmeasures.data.models.generic_assets import GenericAsset

from .. import WEATHER_STATION_TYPE_NAME


def get_locations(
    location: str,
    num_cells: int,
    method: str,
) -> List[Tuple[float, float]]:
    """
    Get locations for getting forecasts for, by parsing the location string, which possibly opens a latitude/longitude grid with several neatly ordered locations.
    """
    if (
        location.count(",") == 0
        or location.count(",") != location.count(":") + 1
        or location.count(":") == 1
        and (
            location.find(",") > location.find(":")
            or location.find(",", location.find(",") + 1) < location.find(":")
        )
    ):
        raise Exception(
            'location parameter "%s" seems malformed. Please use "latitude,longitude" or '
            ' "top-left-latitude,top-left-longitude:bottom-right-latitude,bottom-right-longitude"'
            % location
        )

    location_identifiers = tuple(location.split(":"))

    if len(location_identifiers) == 1:
        ll = location_identifiers[0].split(",")
        locations = [(float(ll[0]), float(ll[1]))]
        click.echo("[FLEXMEASURES] Only one location: %s,%s." % locations[0])
    elif len(location_identifiers) == 2:
        click.echo(
            "[FLEXMEASURES] Making a grid of locations between top/left %s and bottom/right %s ..."
            % location_identifiers
        )
        top_left = tuple(float(s) for s in location_identifiers[0].split(","))
        if len(top_left) != 2:
            raise Exception(
                "top-left parameter '%s' is invalid." % location_identifiers[0]
            )
        bottom_right = tuple(float(s) for s in location_identifiers[1].split(","))
        if len(bottom_right) != 2:
            raise Exception(
                "bottom-right parameter '%s' is invalid." % location_identifiers[1]
            )

        num_lat, num_lng = get_cell_nums(top_left, bottom_right, num_cells)

        locations = LatLngGrid(
            top_left=top_left,
            bottom_right=bottom_right,
            num_cells_lat=num_lat,
            num_cells_lng=num_lng,
        ).get_locations(method)
    else:
        raise Exception("location parameter '%s' has too many locations." % location)
    return locations


def find_weather_sensor_by_location_or_fail(
    location: Tuple[float, float],
    max_degree_difference_for_nearest_weather_sensor: int,
    sensor_name: str,
) -> Sensor:
    """
    Try to find a weather sensor of fitting type close by.
    Complain if the nearest weather sensor is further away than some minimum degrees.
    """
    weather_sensor: Optional[Sensor] = Sensor.find_closest(
        generic_asset_type_name=WEATHER_STATION_TYPE_NAME,
        sensor_name=sensor_name,
        lat=location[0],
        lng=location[1],
        n=1,
    )
    if weather_sensor is not None:
        weather_station: GenericAsset = weather_sensor.generic_asset
        if abs(
            location[0] - weather_station.location[0]
        ) > max_degree_difference_for_nearest_weather_sensor or abs(
            location[1] - weather_station.location[1]
            > max_degree_difference_for_nearest_weather_sensor
        ):
            raise Exception(
                f"No sufficiently close weather sensor found (within 2 degrees distance) for measuring {sensor_name}! We're looking for: {location}, closest available: ({weather_station.location})"
            )
    else:
        raise Exception(
            "No weather sensor set up yet for measuring %s. Try the register-weather-sensor CLI task."
            % sensor_name
        )
    return weather_sensor
