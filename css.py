from google_sheets import *
import pandas as pd
import numpy as np

sheets = [
    ["cssQuarterlyTickets", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Q1234 Tickets Resolved!A:F", []],
    ["cssMonthlyTickets", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Monthly Resolved Tickets!A:F", []],
    ["cssDeviceType", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Device Type!A:K", []],
    ["cssPatronCommunity", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Patron Community!A:W", []],
    # ["cssTypeOfRequest", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Type of Request!A:U", []],
    ["cssTypeOfRequestPCMac", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Type of Request  PC & MAC!A:U", []],
]


def harvest_css(path):
    """Harvest a range of google spreadsheet of CSS
    """

    logging.info("Harvesting CSS Spreadsheets")
    for s in sheets:
        collection = s[0]
        sheet_id = s[1]
        range_name = s[2]
        columns = s[3]
        harvest_sheet_tsv(path, collection, sheet_id, range_name, columns)
    return


def aggregate_css(path):
    css_quarterly_tickets(path)
    css_monthly_tickets(path)
    css_device_type(path)
    css_patron_community(path)
    css_mac_pc(path)


# ---------------

def last_FY(df, column):
    df_year = df.apply(lambda row: row[column][2:4], axis=1)
    last_FY = f"FY{df_year.unique().max()}"
    return last_FY


def combine_lower_n_percent(df, column, treshold=5, decimals=0):
    df = df.sort_values(column, ascending=False)
    total = df[column].sum()
    df["percentage"] = 100.0 * df["count"] / total

    other = df[df["percentage"] < treshold][column].sum()

    # keep
    df = df[df["percentage"] >= treshold]
    other = pd.DataFrame({"count": other, "percentage": 100 * other / total}, index=["Other"])
    df = df.append(other)
    if decimals > 0:
        df["percentage"] = df.apply(lambda row: np.round(row["percentage"], decimals), axis=1)
    elif decimals == 0:
        df["percentage"] = df.apply(lambda row: round(row["percentage"]), axis=1)

    return df


# ----------------


def css_quarterly_tickets(path):
    # cssQuarterlyTickets:
    df = pd.read_csv(path + 'cssQuarterlyTickets.tsv', delimiter="\t",
                     dtype={'RCE': 'Int64', 'Dataverse': 'Int64', 'Desktop': 'Int64'})
    df = df.reindex(columns =["Year", "Quarter", "Year_Quarter", "Desktop", "RCE", "Dataverse"])
    # tickets last 5 years
    df["year_number"] = df.apply(lambda row: int(row["Year"][2:4]), axis=1)
    last_FY = df["year_number"].unique().max()
    last_5yr = last_FY - 4
    df_aggr = df.query(f"year_number >= {last_5yr}")
    print(df_aggr)
    df_aggr.to_csv(path + "css_quarterly_tickets_last_5yr.tsv", sep='\t', index=True, index_label="id")

    # # tickets last quarter
    df["quarter_number"] = df.apply(lambda row: int(row.Quarter[1:2]), axis=1)
    last_quarter = df[df["year_number"] == last_FY]["quarter_number"].max()
    df_aggr = df.query(f"year_number == {last_FY} & quarter_number == {last_quarter}")
    df_aggr.to_csv(path + "css_quarterly_tickets_last_year.tsv", sep='\t', index=True, index_label="id")
    return


def css_monthly_tickets(path):
    # cssMonthlyTickets
    df = pd.read_csv(path + 'cssMonthlyTickets.tsv', delimiter="\t",
                     dtype={'Year': 'Int64', 'Month': 'Int64', 'Desktop': 'Int64', 'RCE': 'Int64',
                            'Dataverse': 'Int64'})

    # tickets last 3 years
    yr3 = df.Year.max() - 3
    df_aggr = df[df["Year"] >= yr3]
    df_aggr = df_aggr.reset_index(drop=True)
    df_aggr.to_csv(path + "css_monthly_tickets_last_3yr.tsv", sep='\t', index=True, index_label="id")
    return df_aggr


def css_device_type(path):
    # cssDeviceType
    df = pd.read_csv(path + 'cssDeviceType.tsv', delimiter="\t")

    # tickets last available year
    df["year_number"] = df.apply(lambda row: int(row["FY"][2:4]), axis=1)
    last_FY = df["year_number"].unique().max()
    df_aggr = df[df["year_number"] == last_FY]

    df_aggr = df_aggr.reset_index(drop=True)
    df_aggr.to_csv(path + "css_device_type_last_year.tsv", sep='\t', index=True, index_label="id")

    return df_aggr


def css_patron_community(path):
    # cssPatronCommunity
    df = pd.read_csv(path + 'cssPatronCommunity.tsv', delimiter="\t")

    # tickets, last available year
    df["year_number"] = df.apply(lambda row: int(row["Year"][2:4]), axis=1)
    last_FY = df["year_number"].unique().max()
    df_aggr = df[df["year_number"] == last_FY]
    df_aggr = df_aggr.drop("year_number", axis=1)

    # transpose the table
    df_aggr = df_aggr.reset_index(drop=True)
    df_aggr2 = df_aggr.T
    df_aggr2 = df_aggr2.rename(columns={0: "count"})
    year_FY = f"FY{last_FY}"
    df_aggr2["Year"] = year_FY
    df_aggr2 = df_aggr2[df_aggr2.index != "Year"]

    # other category: < 3 %
    df_aggr2 = combine_lower_n_percent(df_aggr2, "count", treshold=3, decimals=0)

    # clean up the index so we can keep the order in the index
    df_aggr2 = df_aggr2.reset_index()
    df_aggr2 = df_aggr2.rename(columns={"index": "patron"})

    df_aggr2.to_csv(path + "css_patron_community_last_year.tsv", sep='\t', index=True, index_label="id")
    return df_aggr2


def css_mac_pc(path):
  df = pd.read_csv(path + 'cssTypeOfRequestPCMac.tsv', delimiter="\t")


  #last FY, Mac and PC
  last_year = last_FY(df, "Year")
  df = df[df["Year"] == last_year]
  df = df.drop("Year", axis = 1)

  df = df.set_index("Type")
  df = df.T
  df["Sum"] = df.apply(lambda row: row.PC + row.Mac, axis= 1)
  df = df.sort_values("Sum", ascending = False)
  df["Year"] = last_year
  df.to_csv(path + "css_pc_mac_last_year.tsv", sep='\t', index=True, index_label="id")


  # last FY, Mac and PC, total
  df_aggr = pd.DataFrame(df[["PC","Mac"]].sum(axis=0), columns=["count"])
  df_aggr["year"] = last_year
  df_aggr.reset_index()
  df_aggr.to_csv(path + "css_pc_mac_last_year_total.tsv", sep='\t', index=True, index_label="id")


  # totals PC and MAC over the years
  df = pd.read_csv(path + 'cssTypeOfRequestPCMac.tsv', delimiter="\t")
  df["sum"] = df.sum(axis=1)
  df2=df[["Year", "Type", "sum"]]


  df_total = df2[df2["Type"] == "PC"][["Year","sum"]]
  df_mac = df2[df2["Type"] == "Mac"][["Year","sum"]]

  df_total["PC"] = df_total["sum"]
  df_total = df_total.drop("sum", axis =1 )
  df_total.set_index("Year", inplace=True)
  df_mac["Mac"] = df_mac["sum"]
  df_mac = df_mac.drop("sum", axis =1 )
  df_mac.set_index("Year", inplace=True)
  df_total["Mac"] = df_mac["Mac"]
  df_total.to_csv(path + "css_pc_mac.tsv", sep='\t', index=True, index_label="year")