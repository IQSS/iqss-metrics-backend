# CGA
from __future__ import print_function
from metrics import *
from myfunctions import *

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

def aggregate_cga(path):
    # contact (A)
    df = pd.read_csv(path + 'cgaContact.tsv', delimiter="\t")
    df["date"] = df.Timestamp.transform(lambda x: convert_timestamp_str(x)[:7])
    df_aggr = pd.DataFrame({'count': df["date"].value_counts()}).sort_index()
    df_previous_12_months(df_aggr).to_csv(path + 'cga_contact.tsv', sep="\t", index=True, index_label="date")

    # contact: status/appointment (B)
    df_aggr = filter_last_12_months(df, 'Timestamp')
    df_aggr2 = pd.DataFrame({'count': df_aggr["Your Harvard status/appointment"].value_counts()})
    df_aggr2.to_csv(path + 'cga_contact_status.tsv', sep="\t", index=True, index_label="Harvard status/Appointment")

    # Training (C) --------------------------------
    df = pd.read_csv(path + 'cgaTrainingRegistration.tsv', delimiter="\t")
    df = filter_last_12_months(df, 'Date of the training workshop')

    df["month"] = df.datetime.transform(lambda x: x.strftime("%b") + " " + str(x.year))
    df["name"] = df["Name of the training workshop"] + "#(" + df["month"] + ")"  # we name the column 'count'
    df = df.sort_values("datetime")

    # create a list with unique courses in time order
    df2 = df[["Name of the training workshop", "month", "name"]].drop_duplicates()
    df2.reset_index(drop=True)  # save the order

    # count the number or registrations and save ones  wiht more than 5
    df3 = df[["name", "datetime"]].groupby(['name']).count()
    df3 = df3[df3["datetime"] > 5]

    # join with the table with the correct order and rename columns
    df3 = df2.merge(df3, how="inner", on="name").drop_duplicates()[["name", "datetime"]]
    df_aggr = df3.rename(columns={'name': 'course', 'datetime': 'registration_count'})

    # save
    df_aggr.to_csv(path + 'cga_training.tsv', sep="\t", index=True, index_label="id")

    # Training evaluations (C) ----------------------------------
    df = pd.read_csv(path + 'cgaWorkshopEvaluation.tsv', delimiter="\t")
    df_aggr = df.describe()[1:2].transpose()
    df_aggr = df_aggr.transform(lambda x: round(x, 2))
    df_aggr.to_csv(path + 'cga_workshop_evaluations.tsv', sep="\t", index=True, index_label="metric")

    # Registration for CGA conference
    df = pd.read_csv(path + 'cgaEventRegistration.tsv', delimiter="\t")
    df["count"] = df["Your primary affiliated school at Harvard"].apply(
        lambda x: 'Non-Harvard' if x == "Non-Harvard" else 'Harvard')
    unique_conferences = df["The event name"].value_counts()
    last = unique_conferences[len(unique_conferences) - 1:]
    value = last[0]
    unit = last.index[0]

    # School affiliation: Harvard/ Non Harvard (E)
    df_schools = df[df["The event name"] == unit]["count"].value_counts()
    df_schools.to_csv(path + "cga_conference_schools.tsv", sep='\t', index=True, index_label="School Affiliation")

    # Number of registrations (G2)
    write_metric(path=path, group="CGA", metric="Number of Registrations for CGA Conference",
                 title="CGA Events",
                 value=value, unit="Registrations for " + unit, icon="fa fa-calendar-alt", color="blue",
                 url="")

    # Applications GIS Institute (G1)
    df = pd.read_csv(path + 'cgaGISApplication.tsv', delimiter="\t")
    applications_YTD = len(get_records_YTD(df, drop_datetime=True))
    write_metric(path=path, group="CGA", metric="GIS Institute Applications",
                 title="CGA Applications",
                 value=applications_YTD, unit="Applications for GIS institute " + get_current_year_str() + " YTD",
                 icon="fa fa-university", color="blue",
                 url="")

    # Access Requests (G3)
    df = pd.read_csv(path + 'cgaAccessReq.tsv', delimiter="\t")
    requests_this_year = len(get_records_YTD(df, drop_datetime=True))
    write_metric(path=path, group="CGA", metric="Number of Access requests",
                 title="CGA Requests",
                 value=requests_this_year, unit="Access Requests in " + get_current_year_str() + " YTD",
                 icon="fa fa-key", color="blue",
                 url="")


    # license requests ()
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
