# DSS
from __future__ import print_function
from myfunctions import *
import pandas as pd


def aggregate_dss(path):
    """
    Aggregates DSS data. Right now this function is empty. data is delivered preaggregated/formatted sot
    these files can be uploaded directly to github repository
    @param path:
    @return: nothing
    """
    # aggr_dss_community(path)
    # aggr_dss_request_type(path)
    return


def aggr_dss_request_type(path):
    df = pd.read_csv(f"{path}dss/request_types.csv")
    df = combine_lower_n_percent_complete(df, "n", other_cols=["stringsReq", 'request_type'], sum_columns=["Freq"],
                                          threshold=1., decimals=0)
    df.to_csv(f"{path}dss/dss_request_types.tsv", sep='\t', index=True, index_label="id")


def aggr_dss_community(path):
    df = pd.read_csv(f"{path}dss/community.csv")
    df = combine_lower_n_percent_complete(df, "n", other_cols=["Group.2", 'patron_community'], sum_columns=["hours"],
                                          threshold=0.5, decimals=0)
    df.to_csv(f"{path}dss/dss_community.tsv", sep='\t', index=True, index_label="id")
