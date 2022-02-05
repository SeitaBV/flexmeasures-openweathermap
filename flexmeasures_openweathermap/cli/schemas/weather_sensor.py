from marshmallow import (
    Schema,
    validates,
    validates_schema,
    ValidationError,
    fields,
    validate,
)

import pytz
from flexmeasures.data.models.time_series import Sensor
from flexmeasures.utils.unit_utils import is_valid_unit
from flexmeasures.data import db

from ...utils.modeling import get_weather_station


# This maps sensor name/unit pairs we can use in FlexMeasures to OWM labels
owm_label_support = dict(
    temp={"name": "temperature", "unit": "°C"},
    wind_speed={"name": "wind_speed", "unit": "m/s"},
    clouds={"name": "radiation", "unit": "kW/m²"},
)


class WeatherSensorSchema(Schema):
    """
    Schema for the weather sennsor registration.
    Based on flexmeasures.Sensor, plus some attributes for the weather station asset.
    """

    name = fields.Str(required=True)
    unit = fields.Str(required=True)
    timezone = fields.Str()
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))

    @validates("unit")
    def validate_unit(self, unit: str):
        if not is_valid_unit(unit):
            raise ValidationError(
                f"Unit '{unit}' cannot be handled within FlexMeasures."
            )

    @validates_schema(skip_on_field_errors=False)
    def validate_name_and_unit_are_supported(self, data, **kwargs):
        if "name" not in data or "unit" not in data:
            return  # That's a different validation problem
        for supported_type in owm_label_support.values():
            if (
                supported_type["name"] == data["name"]
                and supported_type["unit"] == data["unit"]
            ):
                return
        supported_str = ", ".join(
            [f"{o['name']}:{o['unit']}" for o in owm_label_support.values()]
        )
        raise ValidationError(
            f"Weather sensors with name '{data['name']}' and unit '{data['unit']}' are not supported by flexmeasures-openweathermap. For now, the following is supported: [{supported_str}]"
        )

    @validates_schema(skip_on_field_errors=False)
    def validate_name_is_unique_in_weather_station(self, data, **kwargs):
        if "latitude" not in data or "longitude" not in data:
            return  # That's a different validation problem
        weather_station = get_weather_station(data["latitude"], data["longitude"])
        if weather_station.id is None:
            db.session.flush()
        sensor = Sensor.query.filter(
            Sensor.name == data["name"].lower(),
            Sensor.generic_asset_id == weather_station.id,
        ).one_or_none()
        if sensor:
            raise ValidationError(
                f"A weather sensor with the name {data['name']} already exists."
            )

    @validates("timezone")
    def validate_timezone(self, timezone: str):
        try:
            pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            raise ValidationError(f"Timezone {timezone} is unknown!")
