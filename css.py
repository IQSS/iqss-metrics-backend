import logging
from google_sheets import *

sheets = [
    ["cssQuarterlyTickets", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Q1234 Tickets Resolved!A:E", []],
    ["cssMonthlyTickets", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Monthly Resolved Tickets!A:E", []],
    ["cssDeviceType", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Device Type!A:K", []],
    ["cssPatronCommunity", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Patron Community!A:W", []],
    ["cssTypeOfRequest", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Type of Request!A:U", []],
    ["cssTypeOfRequestPCMac", "13SiPRDxzf4xEj7_6VrJ8CtvWvnL42gVSO4VAsNHNgqY", "Type of Request  PC & MAC!A:U", []],
]

def harvest_css(path):
    """Harvest a range of google spreadsheet of CSS
    """

    logging.info("Harvesting CSS Spreadsheets")
    for s in sheets:
        collection = s[0]
        sheet_id = s[1]
        range_name = s[2]
        columns = s[3]
        harvest_sheet_tsv(path, collection, sheet_id, range_name, columns)

    return