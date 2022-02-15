from typing import List


def cli_params_from_dict(d) -> List[str]:
    cli_params = []
    for k, v in d.items():
        cli_params.append(f"--{k}")
        cli_params.append(v)
    return cli_params
