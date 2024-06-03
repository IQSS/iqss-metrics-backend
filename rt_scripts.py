# Import modules
import csv
import os
import re
from rt.rest1 import Rt
# import time
import datetime
import logging
from pathlib import Path


def rt_harvard_dataverse(path):
    """
    Gets data from RT for Harvard dataverse tickets.
    @param path: path to write TSV to
    @return: nothing
    """
    user_login = os.getenv("RT_USER")
    user_pass = os.getenv("RT_PASSWORD")

    # Enter the timeframe for the ticket search, e.g. to get tickets created in
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year

    if current_month <= 7:  # FY not ended
        start_date = f'{current_year - 2}-07-01'
        end_date = f'{current_year - 1}-06-30'
        fy = f"FY{current_year - 1}"
    else:
        start_date = f'{current_year - 1}-07-01'
        end_date = f'{current_year}-06-30'
        fy = f"FY{current_year}"

    # Logging into RT
    logging.info('Logging into RT')

    tracker = Rt('https://help.hmdc.harvard.edu/REST/1.0/', user_login, user_pass)

    tracker.login()

    # Save filename
    csv_file = Path(path, "rt_dataverse_support").with_suffix(".tsv")

    # Create CSV with column headers
    with open(csv_file, mode='w') as f1:
        f1 = csv.writer(f1, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        f1.writerow(['custom_field', 'value', 'ticket_url', "period"])

    # Create list containing values for all custom fields to search
    custom_fields = [
        '"CF.{Dev or Curation Interaction}"="Assigned to Client Support Services Team"',
        '"CF.{Dev or Curation Interaction}"="Assigned to Curation Team"',
        '"CF.{Dev or Curation Interaction}"="Assigned to Developer"',
        '"CF.{Dev or Curation Interaction}"="Assigned to Murray Archive"',
        '"CF.{Harvard Dataverse Owner}"="Yes"',
        '"CF.{Harvard Dataverse Owner}"="No"',
        '"CF.{Ticket Type}"="Account update"',
        '"CF.{Ticket Type}"="Bug"',
        '"CF.{Ticket Type}"="Data Deletion request"',
        '"CF.{Ticket Type}"="Data request"',
        '"CF.{Ticket Type}"="Demo request"',
        '"CF.{Ticket Type}"="Download Metrics"',
        '"CF.{Ticket Type}"="Feature Support"',
        '"CF.{Ticket Type}"="General Dataverse inquiry"',
        '"CF.{Ticket Type}"="Harvesting"',
        '"CF.{Ticket Type}"="Installation inquiry"',
        '"CF.{Ticket Type}"="Journal"',
        '"CF.{Ticket Type}"="Large File Upload"',
        '"CF.{Ticket Type}"="Repository Maintenance"',
        '"CF.{Ticket Type}"="Sensitive Data"',
        '"CF.{Ticket Type}"="Software Suggestions"',
        '"CF.{Delete}"="Article"',
        '"CF.{Delete}"="Spam"',
        '"CF.{Delete}"="Other"',
        '"CF.{Delete}"="Test Dataset"',
        '"CF.{Integrations}"="Not related to integration"',
        '"CF.{Integrations}"="Data Exploration Integrations (File Previewers,World Map,etc)"',
        '"CF.{Integrations}"="Journal System Integrations (OJS)"',
        '"CF.{Integrations}"="Replication Verification (ODUM,Code Ocean)"',
        '"CF.{Integrations}"="Repository Integrations (Open Science Framework,ResearchSPace)"',
        '"CF.{Integrations}"="Sensitive Data (Data Tags)"',
        '"CF.{Integrations}"="Rsync (Large data upload)"',
        '"CF.{Harvard Affiliate}"="Yes"',
        '"CF.{Harvard Affiliate}"="No"',
        '"CF.{Features}"="APIs"',
        '"CF.{Features}"="Authentication"',
        '"CF.{Features}"="Citation"',
        '"CF.{Features}"="Data Explorer"',
        '"CF.{Features}"="Dataverse Creation"',
        '"CF.{Features}"="Dataverse editing"',
        '"CF.{Features}"="Dataset creation"',
        '"CF.{Features}"="Dataset editing"',
        '"CF.{Features}"="Dataset publishing"',
        '"CF.{Features}"="Deaccessioning"',
        '"CF.{Features}"="File download"',
        '"CF.{Features}"="File upload"',
        '"CF.{Features}"="File Hierarchy"',
        '"CF.{Features}"="File Level DOI"',
        '"CF.{Features}"="Geospatial Data Exploration"',
        '"CF.{Features}"="Guestbook"',
        '"CF.{Features}"="Metadata Inquiry"',
        '"CF.{Features}"="Notifications"',
        '"CF.{Features}"="Permissions"',
        '"CF.{Features}"="Provenance"',
        '"CF.{Features}"="Return to Author"',
        '"CF.{Features}"="Submit for Review"',
        '"CF.{Features}"="Tabular data file"',
        '"CF.{Features}"="Versioning"',
        '"CF.{Features}"="Other"',
        '"CF.{Installation}"="Harvard Dataverse"',
        '"CF.{Installation}"="Other"']

    # For each custom field, create a query for tickets within the time frame,
    # search RT using that query, and save the JSON data containing the search 
    # results
    logging.info(f'Getting ticket information for group dataverse_support from {start_date} - {end_date}')
    for custom_field in custom_fields:
        raw_query = "%s+and+Created>'%s'+and+Created<'%s'" % (custom_field, start_date, end_date)
        tickets = tracker.search(Queue='dataverse_support', raw_query=raw_query)

        # Use regex to get the custom field category, e.g. "Features", and save to
        # category variable
        get_category = re.search(r'(?<=\{).+?(?=\})', custom_field)
        category = get_category[0]

        # Use regex to get the custom field value, e.g. "APIs", and save to field
        # variable
        get_field = re.search(r'.*\"([^\"]*)\"', custom_field)
        field = get_field[1]

        # Create list to store ticket URLs in each search result
        ticket_urls = []

        # For each search result, get the URLs of tickets owned by a curation team
        # member and write the ticket URL, custom field category and field to a CSV
        # file
        for ticket in tickets:
            ticket_url = 'https://help.hmdc.harvard.edu/Ticket/Display.html?id=%s' % (ticket['numerical_id'])
            ticket_urls.append(ticket_url)

            with open(csv_file, mode='a') as f:
                f = csv.writer(f, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                f.writerow([category, field, ticket_url, fy])

            # # For each row written, print a dot to show the script's progress
            # sys.stdout.write('.')
            # sys.stdout.flush()
    logging.info('Finished!')
