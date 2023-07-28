from marshmallow import (
    Schema,
    validates,
    validates_schema,
    ValidationError,
    fields,
    validate,
)

import pytz

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
    def validate_name_is_given(self, data, **kwargs):
        if "name" not in data:
            return  # That's a different validation problem

    @validates("timezone")
    def validate_timezone(self, timezone: str):
        try:
            pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            raise ValidationError(f"Timezone {timezone} is unknown!")
