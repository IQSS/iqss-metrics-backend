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

  u2d = (pd.read_csv(MAP_FILE, usecols=["sAMAccountName", "department"],
                   dtype_backend="pyarrow")
         .rename(columns={"sAMAccountName": "username", "department": "Dept"}))

  out = (long.merge(u2d, how="inner")
          .groupby(["Dept", "Year"], sort=True, as_index=False)
          .agg(Num=("cpu_hours", "sum")))

  out.to_csv(output_csv, sep="\t", index=False)

if __name__ == "__main__":
    cli()

#import pandas as pd
#pd.options.mode.dtype_backend = "pyarrow"
#
#cpu = pd.read_csv(CPU_FILE, dtype_backend="pyarrow").sum()
#cpu = cpu.reset_index().rename(columns={"index": "username", 0: "cpu_hours"})
#u2d = pd.read_csv(MAP_FILE, names=["username", "Dept"])
#out = (cpu.merge(u2d)
#           .groupby("Dept", as_index=False, sort=True)
#           .agg(Num=("cpu_hours", "sum"))
#           .assign(Year=int(YEAR))[["Dept", "Year", "Num"]])
#out.to_csv(OUT_FILE, sep="\t", index=False)