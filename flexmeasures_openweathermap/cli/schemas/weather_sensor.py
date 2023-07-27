from marshmallow import (
    Schema,
    validates,
    validates_schema,
    ValidationError,
    fields,
    validate,
)

import pytz
from flexmeasures import Sensor

from ...utils.modeling import (
    get_or_create_weather_station,
    get_weather_station_by_asset_id,
)
from ...utils.owm import get_supported_sensor_spec, get_supported_sensors_str


class WeatherSensorSchema(Schema):
    """
    Schema for the weather sensor registration.
    Based on flexmeasures.Sensor, plus some attributes for the weather station asset.
    """

    name = fields.Str(required=True)
    timezone = fields.Str()
    asset_id = fields.Int(required=False, allow_none=True)
    latitude = fields.Float(
        required=False, validate=validate.Range(min=-90, max=90), allow_none=True
    )
    longitude = fields.Float(
        required=False, validate=validate.Range(min=-180, max=180), allow_none=True
    )

    @validates("name")
    def validate_name_is_supported(self, name: str):
        if get_supported_sensor_spec(name):
            return
        raise ValidationError(
            f"Weather sensors with name '{name}' are not supported by flexmeasures-openweathermap. For now, the following is supported: [{get_supported_sensors_str()}]"
        )

    @validates_schema(skip_on_field_errors=False)
    def validate_name_is_unique_in_weather_station(self, data, **kwargs):
        if (
            "name" not in data
            or "latitude" not in data
            or "longitude" not in data
            or "asset_id" not in data
        ):
            return  # That's a different validation problem
        if data["latitude"] is not None and data["longitude"] is not None:
            weather_station = get_or_create_weather_station(
                data["latitude"], data["longitude"]
            )
        elif data["asset_id"] is not None:
            weather_station = get_weather_station_by_asset_id(data["asset_id"])
        else:
            return

        sensor = Sensor.query.filter(
            Sensor.name == data["name"].lower(),
            Sensor.generic_asset == weather_station,
        ).one_or_none()
        if sensor:
            raise ValidationError(
                f"A '{data['name']}' weather sensor already exists at this weather station (the station's ID is {weather_station.id})."
            )

    @validates("timezone")
    def validate_timezone(self, timezone: str):
        try:
            pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            raise ValidationError(f"Timezone {timezone} is unknown!")
