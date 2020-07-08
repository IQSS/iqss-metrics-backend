# research computing
from google_sheets import *

sheets = [
    ["rc-interactive-by-department", "1ai07kTO89huzTGCxMPHUExrT5M0_izqPtrYcK5uuO1s", "RCE Interactive Tier FAS Users by Department!A:D", []],
    ["rc-interactive-by-school", "1ai07kTO89huzTGCxMPHUExrT5M0_izqPtrYcK5uuO1s", "RCE Interactive Tier Users by School!A:D", []],
    ["rc-batch-by-school", "1ai07kTO89huzTGCxMPHUExrT5M0_izqPtrYcK5uuO1s", "RC Batch!A2:D50", []],
    ["rc-batch-by-department", "1ai07kTO89huzTGCxMPHUExrT5M0_izqPtrYcK5uuO1s", "RC Batch!F2:I50", []]

]


def harvest_rc(path):
    """
    Harvest a range of google spreadsheet of CSS
    """

    logging.info("Harvesting RC Spreadsheets")
    for s in sheets:
        collection = s[0]
        sheet_id = s[1]
        range_name = s[2]
        columns = s[3]
        harvest_sheet_tsv(path, collection, sheet_id, range_name, columns)
    return
