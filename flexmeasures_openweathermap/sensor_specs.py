from datetime import timedelta


"""
This maps sensor specs which we can use in FlexMeasures to OWM labels.
Note: Sensor names we use in FM need to be unique per weather station.
At the moment, we only extract from OWM hourly data.
"""


weather_seasonality = {
    "daily_seasonality": True,
    "weekly_seasonality": False,
    "yearly_seasonality": True,
}


owm_to_sensor_map = dict(
    temp={
        "name": "temperature",
        "unit": "°C",
        "event_resolution": timedelta(minutes=60),
        "seasonality": weather_seasonality,
    },
    wind_speed={
        "name": "wind speed",
        "unit": "m/s",
        "event_resolution": timedelta(minutes=60),
        "seasonality": weather_seasonality,
    },
    clouds={
        "name": "irradiance",
        "unit": "kW/m²",
        "event_resolution": timedelta(minutes=60),
        "seasonality": weather_seasonality,
    },
)
