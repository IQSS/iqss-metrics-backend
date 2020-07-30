# PSR
from __future__ import print_function
from metrics import *

sheets = [
    ["psrAdvisesBySchool", "1VFxX-PxfA4ykw0coyLzbV7oB2Ikt1VsHkN3x6diKwTo", "Number of Advisees by School!A:D", []],
    ["psrAdvisesByRole", "1VFxX-PxfA4ykw0coyLzbV7oB2Ikt1VsHkN3x6diKwTo", "Cumulative PSR Advisees by Primary Role!A:E", []]
]


def harvest_psr(path):
    """Harvest a range of google spreadsheet of PSR
    """

    logging.info("Harvesting PSR Spreadsheets")
    for s in sheets:
        collection = s[0]
        sheet_id = s[1]
        range_name = s[2]
        columns = s[3]
        harvest_sheet_tsv(path, collection, sheet_id, range_name, columns)

    return
