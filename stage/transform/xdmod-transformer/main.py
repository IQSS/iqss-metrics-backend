#!/usr/bin/env python3
"""Merge XDMOD PI data with XDMOD extracted data."""

from pathlib import Path
import re
import pandas as pd
import click

FASRC_MAP_FILE = "./_data/pi_2024-10-16T21.56.12.csv"
IQSS_MAP_FILE = "./_data/iq_2025.csv"


def load_maps():
    u2d = pd.read_csv(
        FASRC_MAP_FILE, usecols=["PrimaryGroup", "department"], dtype_backend="pyarrow"
    ).rename(columns={"PrimaryGroup": "PI", "department": "Dept_orig"})

    i2d = pd.read_csv(
        IQSS_MAP_FILE, usecols=["Dept", "PI"], dtype_backend="pyarrow"
    ).rename(columns={"Dept": "Dept_override"})

    return u2d, i2d


def prepare_data(by_pi_csv: Path, value_name: str):
    wide = pd.read_csv(by_pi_csv, dtype_backend="pyarrow")
    year_match = re.match(r"(\d{4})-", by_pi_csv.name)
    year = int(year_match[1]) if year_match else None

    long = wide.melt(var_name="PI", value_name=value_name)
    long["Year"] = year

    u2d, i2d = load_maps()

    merged = long.merge(u2d, how="inner", on="PI").merge(i2d, how="left", on="PI")
    merged["Dept"] = merged["Dept_override"].fillna(merged["Dept_orig"])

    return merged


def aggregate_and_save(df, value_name, output_csv):
    out = (
        df.groupby(["Dept", "Year"], as_index=False)
        .agg(Num=(value_name, "sum"))
        .sort_values(by=["Dept", "Year"])
    )
    out.to_csv(output_csv, sep="\t", index=False)


@click.group()
def cli():
    """XDMOD Data Processing CLI."""


@cli.command()
@click.argument("by_pi_csv", type=click.Path(exists=True, path_type=Path))
@click.argument(
    "output_csv", type=click.Path(path_type=Path), default="./__output__/cpu.tsv"
)
def cpu(by_pi_csv: Path, output_csv: Path):
    df = prepare_data(by_pi_csv, "cpu_hours")
    aggregate_and_save(df, "cpu_hours", output_csv)


@cli.command()
@click.argument("by_pi_csv", type=click.Path(exists=True, path_type=Path))
@click.argument(
    "output_csv", type=click.Path(path_type=Path), default="./__output__/gpu.tsv"
)
def gpu(by_pi_csv: Path, output_csv: Path):
    df = prepare_data(by_pi_csv, "gpu_hours")
    aggregate_and_save(df, "gpu_hours", output_csv)


@cli.command()
@click.argument("by_pi_csv", type=click.Path(exists=True, path_type=Path))
@click.argument(
    "output_csv", type=click.Path(path_type=Path), default="./__output__/jobs.tsv"
)
def jobs(by_pi_csv: Path, output_csv: Path):
    df = prepare_data(by_pi_csv, "jobs_executed")
    aggregate_and_save(df, "jobs_executed", output_csv)


@cli.command()
@click.argument("by_pi_csv", type=click.Path(exists=True, path_type=Path))
@click.argument(
    "output_csv", type=click.Path(path_type=Path), default="./__output__/dept.tsv"
)
def dept(by_pi_csv: Path, output_csv: Path):
    df = prepare_data(by_pi_csv, "jobs_executed")
    year = df["Year"].iloc[0]
    dept_counts = (
        df["Dept"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "PIs", "index": "Dept"})
    )
    dept_counts["Year"] = year
    dept_counts.to_csv(output_csv, sep="\t", index=False)


if __name__ == "__main__":
    cli()
