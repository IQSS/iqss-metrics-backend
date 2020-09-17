# CGA
from __future__ import print_function
from metrics import *
from myfunctions import *
import os

sheets = [
    ["cgaContact", 279615175, os.getenv("SHEET_URL_CGA_CONTACT"), "A:H", [0, 5, 6, 7]],  # OK
    ["cgaWorkshopEvaluation", 1803423154, os.getenv("SHEET_URL_CGA_WORKSHOP_EVALUATIONS"), "A:P",
     [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]],
    # OK
    ["cgaGISApplication", 1021617292, os.getenv("SHEET_URL_CGA_GIS_APPLICATION"), "A:N", [0, 1, 5, 6, 7]],
    # OK
    ["cgaEventRegistration", 0, os.getenv("SHEET_URL_CGA_EVENT_REGISTRATION"), "A:L", [0, 1, 5, 6, 7]],
    # OK
    ["cgaTrainingRegistration", 2068274999, os.getenv("SHEET_URL_CGA_TRAINING_REGISTRATION"), "A:M",
     [0, 1, 2, 6, 7, 8, 11, 12]],
    ["cgaLicenseRequest", 842362239, os.getenv("SHEET_URL_CGA_LICENSE_REQUEST"), "A:L", [0, 5, 6, 7, 10, 11]]
]


def harvest_cga(path):
    """
    Harvest a range of google spreadsheet of CGA
    """

    logging.info("Harvesting CGA Spreadsheets")
    for s in sheets:
        collection = s[0]
        gid = s[1]
        sheet_url = s[2]
        range_name = s[3]
        columns = s[4]
        harvest_sheet_tsv_http(path, collection, sheet_url, range_name, columns, gid=gid)

    return


def aggregate_cga(path):
    cga_contact_time(path)
    cga_contact_status(path)
    cga_contact_school(path)
    cga_training_aggr(path)
    cga_training_evaluations(path)
    gis_institute(path)
    cga_lic_req_top10(path)
    cga_lic_req_status(path)


def cga_contact_school(path):
    # CGA contact by school last 12 months ----------------------------------------------
    df = pd.read_csv(path + 'cgaContact.tsv', delimiter="\t")
    df_contact_12mo = filter_last_12_months(df, 'Timestamp')
    c = "Your primary affiliated school at Harvard"
    df_contact_12mo_aggr = get_counts(df_contact_12mo, column=c)
    df_contact_12mo_aggr = df_contact_12mo_aggr[df_contact_12mo_aggr[c] != "Non-Harvard"]
    df_contact_12mo_aggr = create_percentage(df_contact_12mo_aggr, 'count')
    df_contact_12mo_aggr.to_csv(path + "cga_contact_last_12_months_by_school.tsv", sep='\t', index=True,
                                index_label="id")


def cga_lic_req_status(path):
    # CGA License Request last 12 months by status----------------------------------------------
    df = pd.read_csv(path + 'cgaLicenseRequest.tsv', delimiter="\t")
    df_lic_12mo = filter_last_12_months(df, 'Timestamp')
    c = "Your primary affiliated school at Harvard"
    df_aggr_status = get_counts(df_lic_12mo, c)
    df_aggr_status = df_aggr_status[df_aggr_status[c] != "Non-Harvard"]
    df_aggr_status = create_percentage(df_aggr_status, 'count')
    df_aggr_status.to_csv(path + "cga_license_request_last_12_months_by_status.tsv", sep='\t', index=True,
                          index_label="id")


def cga_lic_req_top10(path):
    # CGA License Request last 12 months Top 10 products --------------------------------------------
    df = pd.read_csv(path + 'cgaLicenseRequest.tsv', delimiter="\t")
    # smaller df of last 12 months
    df2 = df[["Software product which you need a license for", "Timestamp"]]
    df3 = filter_last_12_months(df2, "Timestamp", drop_datetime=True)
    # count number and select top 10
    df3 = df3.groupby("Software product which you need a license for").count()
    df3 = df3.sort_values(by="Timestamp", ascending=False).head(10)
    # clean up of output
    df3 = df3.reset_index()
    df3 = df3.rename(
        columns={'Software product which you need a license for': 'Software product', 'Timestamp': 'count'})
    df3.to_csv(path + "cga_license_req_last_12_months.tsv", sep='\t', index=True, index_label="id")


def gis_institute(path):
    # Applications GIS Institute (G1) ---------------------------
    df = pd.read_csv(path + 'cgaGISApplication.tsv', delimiter="\t")
    applications_ytd = len(get_records_YTD(df, drop_datetime=True))
    write_metric(path=path, group="CGA", metric="GIS Institute Applications",
                 title="GIS Institute",
                 value=applications_ytd, unit="Number of applications " + get_current_year_str() + " YTD",
                 icon="fa fa-university", color="blue",
                 url="")


def cga_training_evaluations(path):
    # Training evaluations (C) ----------------------------------
    df = pd.read_csv(path + 'cgaWorkshopEvaluation.tsv', delimiter="\t")
    df_aggr = df.describe()[1:2].transpose()
    df_aggr = df_aggr.transform(lambda x: round(x, 2))
    df_aggr.to_csv(path + 'cga_workshop_evaluations.tsv', sep="\t", index=True, index_label="metric")


def cga_training_aggr(path):
    # Training (C) --------------------------------
    df = pd.read_csv(path + 'cgaTrainingRegistration.tsv', delimiter="\t")
    df = filter_last_12_months(df, 'Date of the training workshop')
    df["month"] = df.datetime.transform(lambda x: x.strftime("%b") + " " + str(x.year))
    df["name"] = df["Name of the training workshop"] + "#(" + df["month"] + ")"  # we name the column 'count'
    df = df.sort_values("datetime")

    # create a list with unique courses in time order
    df2 = df[["Name of the training workshop", "month", "name"]].drop_duplicates()
    df2.reset_index(drop=True)  # save the order

    # count the number or registrations and save ones  with more than 5
    df3 = df[["name", "datetime"]].groupby(['name']).count()
    df3 = df3[df3["datetime"] > 5]

    # join with the table with the correct order and rename columns
    df3 = df2.merge(df3, how="inner", on="name").drop_duplicates()[["name", "datetime"]]
    df_aggr = df3.rename(columns={'name': 'course', 'datetime': 'registration_count'})
    # save
    df_aggr.to_csv(path + 'cga_training.tsv', sep="\t", index=True, index_label="id")


def cga_contact_time(path):
    # CGA Contact  (A)
    df = pd.read_csv(path + 'cgaContact.tsv', delimiter="\t")
    df["date"] = df.Timestamp.transform(lambda x: convert_timestamp_str(x)[:7])
    df_aggr = pd.DataFrame({'count': df["date"].value_counts()}).sort_index()
    df_previous_12_months(df_aggr).to_csv(path + 'cga_contact.tsv', sep="\t", index=True, index_label="date")


def cga_contact_status(path):
    # CGA Contact: virtual helpdesk req. by status/appointment (B)
    df = pd.read_csv(path + 'cgaContact.tsv', delimiter="\t")
    c = 'Your Harvard status/appointment'
    df_aggr = filter_last_12_months(df, 'Timestamp')
    df_aggr2 = get_counts(df_aggr, c)
    df_aggr2 = df_aggr2[df_aggr2["Your Harvard status/appointment"] != "Non-Harvard"]
    df_aggr2 = create_percentage(df_aggr2, 'count')
    df_aggr2.to_csv(path + 'cga_contact_status.tsv', sep="\t", index=True, index_label="id")
