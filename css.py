from google_sheets import *
import pandas as pd
import numpy as np
import os
from myfunctions import *

css_tickets_url = os.getenv("SHEET_URL_CSS")
sheets = [
    ["cssQuarterlyTickets", 1265380120, css_tickets_url, "A:F", []],
    ["cssMonthlyTickets", 876621858, css_tickets_url, "A:F", []],
    ["cssDeviceType", 2019277922, css_tickets_url, "A:K", []],
    ["cssPatronCommunity", 1186877879, css_tickets_url, "A:W", []],
    ["cssTypeOfRequestPCMac", 2070549986, css_tickets_url, "A:U", []],
    ["lab_report_master_data", 1299232750, css_tickets_url, "A:Y", []],
]


def harvest_css(path):
    """
    Harvest Google spreadsheet of CSS
    @param path: Directory to write to
    @return: nothing
    """

    logging.info("Harvesting CSS Spreadsheets")
    for s in sheets:
        collection = s[0]
        gid = s[1]
        sheet_url = s[2]
        range_name = s[3]
        columns = s[4]
        harvest_sheet_tsv_http(path, collection, sheet_url,
                               range_name, columns, gid=gid)
    return


def aggregate_css(path):
    """
    Wrapper function for aggreation of CSS data
    @param path: Directory to write to
    @return: nothing
    """
    css_quarterly_tickets(path)
    css_monthly_tickets(path)
    css_device_type(path)
    css_patron_community(path)
    css_mac_pc(path)
    aggregate_lab(path)


def css_quarterly_tickets(path):
    """
    Aggregate Quarterly CSS tickets the last 5 year
    @param path: Directory to write to
    @return: nothing
    """
    df = pd.read_csv(path + 'cssQuarterlyTickets.tsv', delimiter="\t",
                     dtype={'RCE': 'Int64', 'Dataverse': 'Int64', 'Desktop': 'Int64'})
    df = df.reindex(columns=["Year", "Quarter",
                    "Year_Quarter", "Desktop", "RCE", "Dataverse"])
    # tickets last 5 years
    df["year_number"] = df.apply(lambda row: int(row["Year"][2:4]), axis=1)
    last_FY = df["year_number"].unique().max()
    last_5yr = last_FY - 4
    df_aggr = df.query(f"year_number >= {last_5yr}")
    df_aggr.to_csv(path + "css_quarterly_tickets_last_5yr.tsv",
                   sep='\t', index=True, index_label="id")

    # # tickets last quarter
    df["quarter_number"] = df.apply(lambda row: int(row.Quarter[1:2]), axis=1)
    last_quarter = df[df["year_number"] == last_FY]["quarter_number"].max()
    df_aggr = df.query(
        f"year_number == {last_FY} & quarter_number == {last_quarter}")
    df_aggr.to_csv(path + "css_quarterly_tickets_last_year.tsv",
                   sep='\t', index=True, index_label="id")
    return


def css_monthly_tickets(path):
    """
    Aggregate Monthly CSS tickets the last 3 years
    @param path: Directory to write to
    @return: dataframe
    """
    df = pd.read_csv(path + 'cssMonthlyTickets.tsv', delimiter="\t",
                     dtype={'Year': 'Int64', 'Month': 'Int64', 'Desktop': 'Int64', 'RCE': 'Int64',
                            'Dataverse': 'Int64'})

    # tickets last 3 years
    yr3 = df.Year.max() - 3
    df_aggr = df[df["Year"] >= yr3]
    df_aggr = df_aggr.reset_index(drop=True)
    df_aggr.to_csv(path + "css_monthly_tickets_last_3yr.tsv",
                   sep='\t', index=True, index_label="id")
    return df_aggr


def css_device_type(path):
    """
    Aggregate tickets by Device Type, the last year
    @param path: Directory to write to
    @return: dataframe
    """
    df = pd.read_csv(path + 'cssDeviceType.tsv', delimiter="\t")

    # tickets last available year
    # get last year
    df["year_number"] = df.apply(lambda row: int(row["FY"][2:4]), axis=1)
    last_FY = df["year_number"].unique().max()

    # filter last year
    df_aggr = df[df["year_number"] == last_FY]

    # Transpose data frame
    # make sure column will be named '0'
    df_aggr = df_aggr.reset_index(drop=True)
    df_aggr = df_aggr.drop(["FY", "year_number"], axis=1)
    df_aggr = df_aggr.T

    # rename column, sort and add Year to column
    df_aggr = df_aggr.rename(columns={0: "count"})
    df_aggr = df_aggr.sort_values("count", ascending=False)
    df_aggr["year"] = f"FY{last_FY}"

    # save dataframe
    df_aggr.to_csv(path + "css_device_type_last_year.tsv",
                   sep='\t', index=True, index_label="device")

    return df_aggr


def css_patron_community(path):
    """
    Aggregate tickets by Patron community, last years ticket. Summarizes smaller items.
    @param path: Directory to write to
    @return: dataframe
    """
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
    df_aggr2 = combine_lower_n_percent(
        df_aggr2, "count", threshold=3, decimals=0)

    # clean up the index so we can keep the order in the index
    df_aggr2 = df_aggr2.reset_index()
    df_aggr2 = df_aggr2.rename(columns={"index": "patron"})

    df_aggr2.to_csv(path + "css_patron_community_last_year.tsv",
                    sep='\t', index=True, index_label="id")
    return df_aggr2


def css_mac_pc(path):
    """
    Aggregate Mac vs PC tickets of the last year
    @param path: Directory to write to
    @return: nothing
    """
    df = pd.read_csv(path + 'cssTypeOfRequestPCMac.tsv', delimiter="\t")

    # last FY, Mac and PC
    last_year = last_FY(df, "Year")
    df = df[df["Year"] == last_year]
    df = df.drop("Year", axis=1)

    df = df.set_index("Type")
    df = df.T
    df["Sum"] = df.apply(lambda row: row.PC + row.Mac, axis=1)
    df = df.sort_values("Sum", ascending=False)
    df["Year"] = last_year
    df.to_csv(path + "css_pc_mac_last_year.tsv",
              sep='\t', index=True, index_label="id")

    # last FY, Mac and PC, total
    df_aggr = pd.DataFrame(df[["PC", "Mac"]].sum(axis=0), columns=["count"])
    df_aggr["year"] = last_year
    df_aggr.reset_index()
    df_aggr.to_csv(path + "css_pc_mac_last_year_total.tsv",
                   sep='\t', index=True, index_label="id")

    # totals PC and MAC over the years
    df = pd.read_csv(path + 'cssTypeOfRequestPCMac.tsv', delimiter="\t")
    df["sum"] = df.sum(axis=1)
    df2 = df[["Year", "Type", "sum"]]

    df_total = df2[df2["Type"] == "PC"][["Year", "sum"]]
    df_mac = df2[df2["Type"] == "Mac"][["Year", "sum"]]

    df_total["PC"] = df_total["sum"]
    df_total = df_total.drop("sum", axis=1)
    df_total.set_index("Year", inplace=True)
    df_mac["Mac"] = df_mac["sum"]
    df_mac = df_mac.drop("sum", axis=1)
    df_mac.set_index("Year", inplace=True)
    df_total["Mac"] = df_mac["Mac"]
    df_total.to_csv(path + "css_pc_mac.tsv", sep='\t',
                    index=True, index_label="year")


def aggregate_lab(path):
    """
    Multiple aggregations of the lab tickets from CSV in ./lab sub directory
    @param path: Directory to write to
    @return: nothing
    """

    # read data
    df = pd.read_csv(path + 'lab_report_master_data.tsv',
                     delimiter='\t', encoding="latin_1", parse_dates=True)

    # convert timestamp
    df["timestamp"] = df["Transaction Created"].apply(
        lambda d: pd.Timestamp(d))

    # drop columns
    df = df.drop(["Transaction Created", "Transaction Time Worked", "Ticket ID", "Queue Name", "Ticket Requestor",
                  "Ticket Owner", "Ticket Subject", "Ticket Parents IDs", "Ticket Children IDs", "Audio & Video",
                  "Power Adapters", "Input Devices", "Cables & Adapters", "Laptops", "Misc"], axis=1)

    # create columns
    df["year"] = df["timestamp"].apply(lambda d: d.year)
    df["month"] = df["timestamp"].apply(lambda d: d.month)
    df["month_name"] = df["timestamp"].apply(lambda d: d.month_name())
    df["quarter"] = df["timestamp"].apply(lambda d: f"Q{d.quarter}")
    df["year_quarter"] = df["timestamp"].apply(
        lambda d: f"{d.year}-Q{d.quarter}")
    df["year_month"] = df["timestamp"].apply(
        lambda d: f"{d.year}-{d.month:02}")
    df["year_month_name"] = df["timestamp"].apply(
        lambda d: f"{d.month_name()} {d.year}")

    # create period value
    end = list(df["year_month_name"].value_counts()[-1:].index)[0]
    begin = list(df["year_month_name"].value_counts()[0:1].index)[0]
    period = f"{begin} - {end}"

    requests_per_month_year = df_value_counts(df, "year_month")
    requests_per_month_year = requests_per_month_year.sort_values(
        "year_month", ascending=True)
    requests_per_month_year.to_csv(
        f"{path}lab_request_per_month.tsv", sep='\t', index=True, index_label="id")

    requests_per_quarter = df_value_counts(df, "year_quarter")
    requests_per_quarter.to_csv(
        f"{path}lab_request_per_quarter.tsv", sep='\t', index=True, index_label="id")

    # total request by school"
    df_schools = df_value_counts(df, "School", limit=1)
    df_schools["period"] = period
    df_schools.to_csv(f"{path}lab_request_school.tsv",
                      sep='\t', index=True, index_label="id")

    # requests by departement
    df_dc = df_value_counts(df, "Department/Concentration", limit=1)

    # there is already on 'other' category, so we need to combine these.
    sum_other = df_dc[df_dc["Department/Concentration"] == "Other"].sum(axis=0)
    count = sum_other["count"]
    percentage = sum_other["percentage"]

    df_dc = df_dc[df_dc["Department/Concentration"] != "Other"]
    df_dc = df_dc.append(
        pd.DataFrame({"Department/Concentration": "Other", "count": count, "percentage": percentage}, index=[100]))

    df_dc["period"] = period
    df_dc.to_csv(f"{path}lab_request_department.tsv",
                 sep='\t', index=True, index_label="id")

    # Request by Status
    df_status = df_value_counts(df, "Status", limit=2)
    df_status["period"] = period
    df_status.to_csv(f"{path}lab_request_status.tsv",
                     sep='\t', index=True, index_label="id")

    # Request Sponsored?
    df_sponsored = df_value_counts(df, "Sponsored?")
    df_sponsored["period"] = period
    df_sponsored.to_csv(f"{path}lab_request_sponsored.tsv",
                        sep='\t', index=True, index_label="id")

    # what is the reason for access
    # the columns can contain multiple values separated by ;
    df_reasons = df["Reason for Lab Access:"].dropna()
    reasons = []
    for i in df_reasons:
        record = i.split(';')
        for j in record:
            reasons.append(j)

    df_reasons = pd.DataFrame(reasons)
    df_reasons.columns = ["Reason for Lab Access"]
    df_reasons = df_value_counts(df_reasons, "Reason for Lab Access")
    df_reasons["period"] = period
    df_reasons.to_csv(f"{path}lab_request_reason.tsv",
                      sep='\t', index=True, index_label="id")

    # How did you hear about us?
    df_discovery = df_value_counts(df, "Lab Discovery")
    df_discovery["period"] = period
    df_discovery.to_csv(f"{path}lab_request_discovery.tsv",
                        sep='\t', index=True, index_label="id")
