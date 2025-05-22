#!/usr/bin/env python3
"""
Merge XDMOD PI data with XDMOD data extracted
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
import click

FASRC_MAP_FILE = "./_data/pi_2024-10-16T21.56.12.csv"
IQSS_MAP_FILE = "./_data/iq_2025.csv"


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "by_user_csv",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
)
@click.argument(
    "output_csv",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    default="./__output__/out.tsv",
)
def cli(by_user_csv: Path, output_csv: Path) -> None:
    # Generates CPU averages
    wide = pd.read_csv(by_user_csv, dtype_backend="pyarrow")
    year = int(re.match(r"(\d{4})-", Path(by_user_csv).name)[1])  # type: ignore
    long = wide.melt(var_name="username", value_name="cpu_hours")
    long["Year"] = year

    u2d = pd.read_csv(
        FASRC_MAP_FILE,
        usecols=["sAMAccountName", "PrimaryGroup", "department"],
        dtype_backend="pyarrow",
    ).rename(
        columns={
            "sAMAccountName": "username",
            "PrimaryGroup": "PI",
            "department": "Dept_orig",
        }
    )

    i2d = pd.read_csv(
        IQSS_MAP_FILE, usecols=["Dept", "PI"], dtype_backend="pyarrow"
    ).rename(columns={"Dept": "Dept_override"})

    cpu_with_pi = long.merge(u2d, how="inner",on="username")
    # This will only use the keys we care about
    cpu_resolved = cpu_with_pi.merge(i2d, on="PI", how="right").assign(
        Dept=lambda df: df["Dept_override"].fillna(df["Dept_orig"])
    )
    out = (
        cpu_resolved
        .groupby(["Dept", "Year"], sort=True, as_index=False)
        .agg(Num=("cpu_hours", "sum"))
    )

    out.to_csv(output_csv, sep="\t", index=False)


if __name__ == "__main__":
    cli()
