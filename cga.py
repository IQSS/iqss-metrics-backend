# CGA
from __future__ import print_function
from datetime import *
from google_sheets import *
import logging
import pandas as pd

sheets = [
    ["cgaContact", "1bd7VPF2fLKfcnjjlZU4PxfaS75x3d_C7P0a_rb4FP1M", "Form Responses 1!A:H", [0, 5, 6, 7]],  # OK
    ["cgaWorkshopEvaluation", "1j495c7dZ5blPjwwzXsn_vl21lg9CHKJWT-5sUZWLnvk", "Form Responses 1!A:P",
     [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]],
    # OK
    ["cgaGISApplication", "1dZFh4Zyws9pwND992_NpZGfJ9IlFQwHW-f6FiQ_M1cA", "Form Responses 1!A:N", [0, 1, 5, 6, 7]],
    # OK
    ["cgaEventRegistration", "1UiOKlYcum5s3Vlyj4f4zzlxJ7UMiqeY_yu1JXgylxMI", "Form Responses 1!A:L", [0, 1, 5, 6, 7]],
    # OK
    ["cgaTrainingRegistration", "15b3O2wkUoq4TqJ-_T4qB-Jypqe2_zemupHo_s-QCZm4", "Form Responses 1!A:M",
     [0, 1, 2, 6, 7, 8, 11, 12]],
    ["cgaLicenseRequest", "1e40rmc55hErUSIlOHLHGm40bzAya00FzRrI3oAx-kcs", "Form Responses 1!A:L", [0, 5, 6, 7, 10, 11]],
    # OK
    ["cgaSULicenses", "1kJCQkbPCDQeLTNR1Jjnpox8i9QgTULc1Nywxi9KWJsI", "Tracking!A:H", [0, 1, 2, 4, 5, 7]],  # OK
    ["cgaAccessReq", "1_hD3ME9877rmHkyBK-PNlsiLRarqlio0A4cAy84luhw", "Form Responses 1!A:L", [0, 5, 6, 7, 10]]  # OK
]


def harvest_cga(path):
    """Harvest a range of google spreadsheet of CGA
    """

    logging.info("Harvesting CGA Spreadsheets")
    for s in sheets:
        collection = s[0]
        sheet_id = s[1]
        range_name = s[2]
        columns = s[3]
        harvest_sheet_tsv(path, collection, sheet_id, range_name, columns)

    return

def convertTimestamp(timestamp_string):
     return str(datetime.datetime.strptime(timestamp_string, "%m/%d/%Y %H:%M:%S").date())

def convertTimestamp_dt(timestamp_string):
    return datetime.datetime.strptime(timestamp_string, "%m/%d/%Y %H:%M:%S").date()


# return the last 12 rows, not including last one
def df_previous_12_months(df):
    if len(df)<12:
        return df
    else:
        return df.head(len(df)-1).tail(12)

def get_last_month():
    t = datetime.datetime.now()
    return pd.Timestamp(datetime.datetime(t.year, t.month, 1, 0, 0, 0, 0))

def get_last_year():
    t = datetime.datetime.now()
    return pd.Timestamp(datetime.datetime(t.year - 1, t.month, 1, 0, 0, 0, 0))

def filter_last_12_months(df, field):
    df["datetime"] = df[field].transform(lambda x: pd.Timestamp(x))
    return df[(df['datetime'] >= get_last_year()) & (df['datetime'] < get_last_month())]

def aggregate_cga(path):

    # contact
    df = pd.read_csv(path + 'cgaContact.tsv', delimiter="\t")
    df["date"] = df.Timestamp.transform(lambda x: convertTimestamp(x)[:7])
    df_aggr = pd.DataFrame({'count': df["date"].value_counts()}).sort_index()
    df_previous_12_months(df_aggr).to_csv(path + 'cga_contact.tsv', sep="\t", index=True, index_label="date")


    # contact: status
    df_aggr = filter_last_12_months(df, 'Timestamp')
    df_aggr2 = pd.DataFrame({'count': df_aggr["Your Harvard status/appointment"].value_counts()})
    df_aggr2.to_csv(path + 'cga_contact_status.tsv', sep="\t", index=True, index_label="Harvard status/Appointment")

    # Training
    df = pd.read_csv(path + 'cgaTrainingRegistration.tsv', delimiter="\t")
    df = filter_last_12_months(df, 'Date of the training workshop')

    df["month"] = df.datetime.transform(lambda x: x.month_name() + " " + str(x.year))
    df["count"] = df["Name of the training workshop"] + "\n(" + df["month"] + ")" # we name the column 'count'
    df.sort_values('datetime')

    df_aggr = df["count"].value_counts(sort= False)
    # TODO: needs sorting
    df_aggr.to_csv(path + 'cga_training.tsv', sep="\t", index=True, index_label="course")

    # Training evaluations
    df = pd.read_csv(path + 'cgaWorkshopEvaluation.tsv', delimiter="\t")
    df_aggr = df.describe()[1:2].transpose()
    df_aggr = df_aggr.transform(lambda x: round(x, 2))
    df_aggr.to_csv(path + 'cga_workshop_evaluations.tsv', sep="\t", index=True, index_label="metric")

    # Registration for CGA conference
    # School affiliation: Harvard/ Non Havard
    # Number of registrations
    #


    # metrics:
    # 1: Access 28 Access request in 2020
    # 2: CGA Events/114/Registrations for conference 2019

    # 3:Applications:    47: Applicatons for GIS     institute 2020

    # license requests
    # top 10 license requests (Software product vs.Number of license requests.
    # write_metric(path=path, group="Dataverse", metric="Dataverse TV", title="Dataverse TV",
    #              value=nrow, unit="Number of Videos", icon="fa fa-tv", color="red",
    #              url="https://iqss.github.io/dataverse-tv/")