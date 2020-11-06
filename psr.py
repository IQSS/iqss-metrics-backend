# PSR
from __future__ import print_function
import os
from metrics import *
sheets = [
    ["psrAdvisesBySchool", 0, os.getenv("SHEET_URL_PSR"), "A:D", []],
    ["psrAdvisesByRole", 1079810459, os.getenv("SHEET_URL_PSR"), "A:E", []]
]


def harvest_psr(path):
    """
    Harvest a range of google spreadsheet of PSR
    @param path: directory to write to
    @return: (nothing)
    """
    logging.info("Harvesting PSR Spreadsheets")
    for s in sheets:
        collection = s[0]
        gid = s[1]
        url = s[2]
        range_name = s[3]
        columns = s[4]
        harvest_sheet_tsv_http(path, collection, url, range_name, columns, gid=gid)

    return
