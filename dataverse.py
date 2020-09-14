import os
from myfunctions import get_counts
from metrics import *
from rt_scripts import rt_harvard_dataverse


# dataverse tv -----------------
def harvest_dataverse(path):
    # pre-aggregated data on servers of Odum institute
    # TODO: This is a Temporary solution
    download_files_from_odum(path)

    # dataverse tv
    harvest_sheet_tsv_http(path, "dataverse_tv", os.getenv("SHEET_URL_DATAVERSE"), "A:E", [1, 2, 3, 4, 5])

    # dataverse installations
    harvest_dataverse_installations(path)

    # dataverse aggregations
    aggregate_dataverse(path)

    # data verse github -----------------
    logging.info('Harvesting Dataverse GitHub')

    collection_name = "dataverse_github"
    now = date.today().strftime('%Y-%m-%d')

    url = "https://api.github.com/repos/IQSS/dataverse"
    resp = requests.get(url=url)
    data = resp.json()

    with open(path + collection_name + "_all.tsv", 'w') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')

        posts = [
            [now, 'Dataverse', 'GitHub Watchers', 'Dataverse on GitHub', data["watchers_count"], 'Watchers', '', '',
             ''],
            [now, 'Dataverse', 'GitHub Subscribers', 'Dataverse on GitHub', data["subscribers_count"], 'Subscribers',
             '', '',
             '']]

        for row in range(0, len(posts)):
            writer.writerow(posts[row])
            write_metric(path, group=posts[row][1], metric=posts[row][2], title=posts[row][3], value=posts[row][4],
                         unit=posts[row][5], icon="fab fa-github", color="orange", url="dataverse.html")


def download_files_from_odum(path):
    logging.info('Downloading files from ODUM servers')
    tables = ["dataverses-toMonth.tsv",
              "dataverses-byCategory.tsv",
              "datasets-toMonth.tsv",
              "datasets-bySubject.tsv",
              "files-toMonth.tsv",
              "downloads-toMonth.tsv"]

    odum_url = "https://dataversemetrics.odum.unc.edu/dataverse-metrics/"

    for t in tables:
        tsv = requests.get(odum_url + t)
        f = open(path + t, "w")
        f.write(tsv.text)
        f.close()


def harvest_dataverse_installations(path):
    logging.info('Dataverse installations')

    df = pd.read_json(
        "https://iqss.github.io/dataverse-installations/data/data.json")

    df2 = df['installations']

    countries = []
    for i in range(0, len(df2)):
        if df2[i]["country"] != "NA":
            countries.append(df2[i]["country"])

    c = pd.DataFrame({'count': pd.Series(countries)})
    df_c = c["count"].value_counts()

    df_c.to_csv(path + 'dataverse_installations.tsv', sep="\t", index=True, index_label="country")

    nrow = "%d" % len(df)
    write_metric(path=path, group="Dataverse", metric="Dataverse Installations", title="Dataverse Worldwide",
                 value=nrow, unit="Number of Installations", icon="fa fa-globe", color="blue",
                 url="dataverse.html")


def aggregate_dataverse(path):
    logging.info('Aggregate Dataverse info')

    df = pd.read_csv(path + 'dataverse_tv.tsv', delimiter="\t")
    nrow = "%d" % len(df)
    write_metric(path=path, group="Dataverse", metric="Dataverse TV", title="Dataverse TV",
                 value=nrow, unit="Number of Videos", icon="fa fa-tv", color="red",
                 url="https://iqss.github.io/dataverse-tv/")


# Harvard Dataverse ---------------------
def harvest_harvard_dataverse(path, config):
    rt_harvard_dataverse(path, config)


def aggregate_harvard_dataverse(path):
    logging.info('Aggregate Harvest Dataverse')

    df_dv_support_tickets = pd.read_csv(path + 'rt_dataverse_support.tsv', delimiter="\t")
    period = df_dv_support_tickets["period"][0]

    # total number of tickets
    count = len(df_dv_support_tickets["ticket_url"].unique())
    title = f"Total number of Tickets {period}"
    write_metric(path=path, group="Dataverse Support", metric="Dataverse  Support Tickets", title="Dataverse Support",
                 value=count, unit=title, icon="fa fa-ticket-alt", color="red",
                 url="")

    # Features -----------------
    df_features = get_counts(df_dv_support_tickets[df_dv_support_tickets["custom_field"] == "Features"], 'value')

    other = df_features[df_features["value"] == "Other"]
    not_other = df_features[df_features["value"] != "Other"].sort_values(by="count", ascending=False)
    df_features = not_other.append(other).reset_index(drop=True)
    df_features["period"] = period

    df_features.to_csv(f"{path}dvs-feature_aggr.tsv", sep='\t', index=True, index_label="id")

    # ticket types -----------------
    df_ticket_type = get_counts(df_dv_support_tickets[df_dv_support_tickets["custom_field"] == "Ticket Type"],
                                'value')  # ["value"].value_counts()
    df_ticket_type["period"] = period
    df_ticket_type.to_csv(f"{path}dvs-ticket-type_aggr.tsv", sep='\t', index=True, index_label="id")
