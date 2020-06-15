import json
from google_sheets import harvest_sheet_tsv
import requests
from datetime import date
import csv
from metrics import *


# dataverse tv -----------------
def harvest_dataverse(path):
    harvest_sheet_tsv(path, "dataverse_tv", "1uVk_57Ek_A49sLZ5OKdI6QASKloWNzykni3kcYNzpxA", "A:E", [1,2,3,4,5])
    harvest_dataverse_installations(path)
    aggregate_dataverse(path)

    # data verse github -----------------
    logging.info('Harvesting Dataverse GitHub')

    collection_name = "dataverse_github"
    now = date.today().strftime('%Y-%m-%d')

    # Write social_media_all once a day to prevent double records
    with open(path + collection_name + "_all.tsv", 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        for r in reader:
            if r[0] == now:
                logging.info('Harvesting Dataverse GitHub already harvested')
                return

    url = "https://api.github.com/repos/IQSS/dataverse"
    resp = requests.get(url=url)
    data = resp.json()

    with open(path + collection_name + "_all.tsv", 'w') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')

        posts = [
            [now, 'Dataverse', 'GitHub Watchers', 'Dataverse on GitHub', data["watchers_count"], 'Watchers', '', '', ''],
            [now, 'Dataverse', 'GitHub Open Issues', 'Dataverse on GitHub', data["open_issues_count"], 'Open Issues', '', '',
             ''],
            [now, 'Dataverse', 'GitHub Subscribers', 'Dataverse on GitHub', data["subscribers_count"], 'Subscribers', '', '',
             '']]

        for row in range(0, len(posts)):
            writer.writerow(posts[row])
            write_metric(path, group=posts[row][1], metric=posts[row][2], title=posts[row][3], value = posts[row][4],
                         unit=posts[row][5], icon="fab fa-github", color="orange", url="")
    # TODO: aggregate into main_metrics?



def harvest_dataverse_installations(path):
    logging.info('Dataverse installations')

    df = pd.read_json(
        "https://iqss.github.io/dataverse-installations/data/data.json")

    df2 = df['installations']
    # df_countries = pd.DataFrame()
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
                 url="")


def aggregate_dataverse(path):
    logging.info('Aggregate Dataverse info')

    df = pd.read_csv(path + 'dataverse_tv.tsv', delimiter="\t")
    nrow = "%d" % len(df)
    write_metric(path=path, group="Dataverse", metric="Dataverse TV", title="Dataverse TV",
                 value=nrow, unit="Number of Videos", icon="fa fa-tv", color="red",
                 url="https://iqss.github.io/dataverse-tv/")
