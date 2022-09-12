from datetime import timedelta


"""
This maps sensor specs which we can use in FlexMeasures to OWM labels.
Note: Sensor names we use in FM need to be unique per weather station.
At the moment, we only extract from OWM hourly data.
"""


weather_attributes = {
    "daily_seasonality": True,
    "weekly_seasonality": False,
    "yearly_seasonality": True,
}


mapping = [
    dict(
        fm_sensor_name="temperature",
        owm_sensor_name="temp",
        unit="°C",
        event_resolution=timedelta(minutes=60),
        attributes=weather_attributes,
    ),
    dict(
        fm_sensor_name="wind speed",
        owm_sensor_name="wind_speed",
        unit="m/s",
        event_resolution=timedelta(minutes=60),
        attributes=weather_attributes,
    ),
    dict(
        fm_sensor_name="cloud cover",
        owm_sensor_name="clouds",
        unit="%",
        event_resolution=timedelta(minutes=60),
        attributes=weather_attributes,
    ),
    dict(
        fm_sensor_name="irradiance",  # in save_forecasts_to_db, we catch this name and do the actual computation to get to the irradiance
        owm_sensor_name="clouds",
        unit="kW/m²",
        event_resolution=timedelta(minutes=60),
        attributes=weather_attributes,
    ),
]
