#!/usr/bin/env python3
"""
Fetch CPU and GPU usage from Harvard's XDMoD instance for the previous
calendar year and write the results to CSV files in the chosen directory
(default: current working directory).

Usage
-----
python xdmod_annual_usage.py [OUTPUT_DIR]

Dependencies
------------
pip install xdmod-data click pandas

Environment
-----------
Create an environment variable named ``XDMOD_API_TOKEN`` containing a valid
token for https://xdmod.rc.fas.harvard.edu.
"""
from __future__ import annotations

import datetime as _dt
import os
from time import time
from pathlib import Path

import click
import pandas as _pd
from xdmod_data.warehouse import DataWarehouse
from typing import TypeAlias, Tuple, List

DimensionLabelT: TypeAlias = Tuple[str, str]
ExecutionsT: TypeAlias = List[DimensionLabelT]

# Metric display name → filename fragment
_METRICS: dict[str, ExecutionsT] = {
    "CPU Hours: Total": [
        ("person", "cpu-consumed-x-user"),
        ("pi", "cpu-consumed-x-pi"),
    ],
    "GPU Hours: Total": [
        ("person", "gpu-consumed-x-user"),
        ("pi", "gpu-consumed-x-pi"),
    ],
    "Number of Jobs Ended": [
        ("person", "jobs-executed-x-user"),
        ("pi", "jobs-executed-x-pi")
    ],
}


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default="./__output__",
)
@click.argument(
    "year",
    type=int,
    default= _dt.date.today().year,
)
def cli(output_dir: Path, year: int) -> None:
    """Generate last-year usage CSVs and save them in OUTPUT_DIR."""
    start, end = f"{year}-01-01", f"{year}-12-31"

    output_dir.mkdir(parents=True, exist_ok=True)

    token = os.getenv("XDMOD_API_TOKEN")
    if token is None:
        raise RuntimeError("Please set XDMOD_API_TOKEN in your environment")

    dw = DataWarehouse("https://xdmod.rc.fas.harvard.edu")

    with dw:
        for metric_name, executions in _METRICS.items():
            for dimension, stem in executions:
                ts: int = int(time())
                csv_path = output_dir / f"{year}-{stem}-xdmod-rc-fas-harvard-edu.{ts}.csv"

                if Path.exists(csv_path):
                    click.echo(f"{csv_path} exists. skipping...")
                    continue

                data = dw.get_data(
                    duration=(start, end),  # type: ignore
                    filters={},
                    dimension=dimension,
                    dataset_type="timeseries",
                    aggregation_unit="Auto",
                    metric=metric_name,
                )

                df = _pd.DataFrame(data)  # ensure DataFrame regardless of return type
                df.to_csv(csv_path, index=False)
                click.echo(f"Wrote {csv_path}")


if __name__ == "__main__":
    cli()
