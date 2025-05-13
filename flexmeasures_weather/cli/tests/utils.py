from typing import List
from datetime import datetime, timedelta

from flexmeasures.utils.time_utils import as_server_time, get_timezone


def cli_params_from_dict(d) -> List[str]:
    cli_params = []
    for k, v in d.items():
        cli_params.append(f"--{k}")
        cli_params.append(v)
    return cli_params


def mock_owm_response(api_key, location):
    mock_date = datetime.now()
    mock_date_tz_aware = as_server_time(
        datetime.fromtimestamp(mock_date.timestamp(), tz=get_timezone())
    ).replace(second=0, microsecond=0)
    return mock_date_tz_aware, [
        {"dt": mock_date.timestamp(), "temp": 40, "wind_speed": 100},
        {
            "dt": (mock_date + timedelta(hours=1)).timestamp(),
            "temp": 42,
            "wind_speed": 90,
        },
    ]
