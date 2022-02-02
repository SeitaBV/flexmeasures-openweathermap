from marshmallow import Schema, validates, ValidationError, fields, validate

import pytz
from flexmeasures.data.models.time_series import Sensor
from flexmeasures.utils.unit_utils import is_valid_unit


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

    @validates("name")
    def validate_name(self, name: str):
        """TODO: within asset (weather station)"""
        sensor = Sensor.query.filter(Sensor.name == name.lower()).one_or_none()
        if sensor:
            raise ValidationError(
                f"A weather sensor with the name {name} already exists."
            )

    @validates("unit")
    def validate_unit(self, unit: str):
        if not is_valid_unit(unit):
            raise ValidationError(f"Unit '{unit}' cannot be handled.")

    @validates("timezone")
    def validate_timezone(self, timezone: str):
        try:
            pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            raise ValidationError(f"Timezone {timezone} is unknown!")
