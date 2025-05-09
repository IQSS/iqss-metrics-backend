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

def main():
    print("Hello from xdmod-transformer!")


if __name__ == "__main__":
    main()
