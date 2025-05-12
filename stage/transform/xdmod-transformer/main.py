#!/usr/bin/env python3
"""
Merge XDMOD PI data with XDMOD data extracted
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
import click

MAP_FILE = "./_data/pi_2024-10-16T21.56.12.csv"


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "input_csv",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
)
@click.argument(
    "output_csv",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    default="./__output__/out.tsv",
)
def cli(input_csv: Path, output_csv: Path) -> None:
    # Generates CPU averages
    wide = pd.read_csv(input_csv, dtype_backend="pyarrow")
    year = int(re.match(r"(\d{4})-", Path(input_csv).name)[1])
    long = wide.melt(var_name="username", value_name="cpu_hours")
    long["Year"] = year

    u2d = pd.read_csv(
        MAP_FILE, usecols=["sAMAccountName", "department"], dtype_backend="pyarrow"
    ).rename(columns={"sAMAccountName": "username", "department": "Dept"})

    out = (
        long.merge(u2d, how="inner")
        .groupby(["Dept", "Year"], sort=True, as_index=False)
        .agg(Num=("cpu_hours", "sum"))
    )

    out.to_csv(output_csv, sep="\t", index=False)


if __name__ == "__main__":
    cli()
