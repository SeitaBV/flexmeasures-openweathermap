from datetime import datetime

import pandas as pd
from pvlib.location import Location


def compute_irradiance(
    latitude: float, longitude: float, dt: datetime, cloud_coverage: float
) -> float:
    """Compute the irradiance received on a location at a specific time.
    This uses pvlib to
    1)  compute clear-sky irradiance as Global Horizontal Irradiance (GHI),
        which includes both Direct Normal Irradiance (DNI)
        and Diffuse Horizontal Irradiance (DHI).
    2)  adjust the GHI for cloud coverage
    """
    site = Location(latitude, longitude, tz=dt.tzinfo)
    solpos = site.get_solarposition(pd.DatetimeIndex([dt]))
    ghi_clear = site.get_clearsky(pd.DatetimeIndex([dt]), solar_position=solpos).loc[
        dt
    ]["ghi"]
    return ghi_clear_to_ghi(ghi_clear, cloud_coverage)


def ghi_clear_to_ghi(ghi_clear: float, cloud_coverage: float) -> float:
    """Compute global horizontal irradiance (GHI) from clear-sky GHI, given a cloud coverage between 0 and 1.

    References
    ----------
    Perez, R., Moore, K., Wilcox, S., Renne, D., Zelenka, A., 2007.
    Forecasting solar radiation – preliminary evaluation of an
    approach based upon the national forecast database. Solar Energy
    81, 809–812.
    """
    if cloud_coverage < 0 or cloud_coverage > 1:
        raise ValueError("cloud_coverage should lie in the interval [0, 1]")
    return (1 - 0.87 * cloud_coverage**1.9) * ghi_clear
