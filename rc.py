# research computing
from google_sheets import *
import os
sheet = os.getenv("SHEET_URL_MAIN_AND_RESEARCH_COMPUTING")
sheets = [
    ["rc-interactive-by-department", 1520439358, sheet, "A:D", []],
    ["rc-interactive-by-school", 1746116154, sheet, "A:D", []],
    ["rc-batch-by-school", 1414161867, sheet, "A2:D50", []],
    ["rc-batch-by-department", 1414161867, sheet, "F2:I50", []]
]


def harvest_rc(path):
    """
    Harvest a range of google spreadsheet of Research computing
    @param path: directory to write to
    @return: (nothing)
    """

    logging.info("Harvesting RC Spreadsheets")
    for s in sheets:
        collection = s[0]
        gid = s[1]
        url = s[2]
        range_name = s[3]
        columns = s[4]
        harvest_sheet_tsv_http(path, collection, url, range_name, columns, gid=gid)

    return
