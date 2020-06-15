import os.path
from google_sheets import *
import pandas as pd


def write_metric(path, group, metric, title, value, unit, icon="fa fa-chart", color="orange", url=""):
    # logging.info("Writing main metric %s" % metric)

    d = {'group': [group],
         'metric': [metric],
         'title': [title],
         'value': [value],
         'unit': [unit],
         'icon': [icon],
         'color': [color],
         'url': [url]
         }
    df = pd.DataFrame(data=d)

    file_name = path + "main_metrics.tsv"
    if os.path.isfile(file_name):

        df_file = pd.read_csv(file_name, delimiter="\t")

        row = df_file.loc[(df_file['metric'] == metric) & (df_file['group'] == group)]
        if len(row) == 0:
            logging.info('Adding main metric %s' % metric)
        else:
            logging.info('Updating main metric %s' % metric)
            df_file = df_file.drop(df_file[(df_file['metric'] == metric) & (df_file['group'] == group)].index)
        df_file = df_file.append(df)
        df_file.to_csv(file_name, sep="\t", index=False)
    else:
        logging.info("%s not found. Creating new file." % file_name)
        df.to_csv(file_name, sep="\t", index=False)


def harvest_main_metrics(path):
    logging.info("Harvesting main metrics")
    harvest_sheet_tsv(path, 'main_metrics', sheet_id="1ai07kTO89huzTGCxMPHUExrT5M0_izqPtrYcK5uuO1s",
                      range_name="Main!A:H", columns=[])

def aggregate_main_metrics(path):
    # aggregate into main metrics
    logging.info("Aggregating main metrics")
    df = pd.read_csv(path + 'main_metrics.tsv', delimiter="\t")
    for index, row in df.iterrows():
        write_metric(path, group=row["group"], metric=row["metric"], title=row["title"], unit=row["unit"],
                     value=row["value"], icon=row["icon"], url=row["url"])

