from time import ctime

from business_operations import *
from cga import *
from css import *
from dataverse import *
from google_sheets import *
import json
import os
from metrics import *

def push_to_github(config):
    logging.info("Pushing TSV to Github Dashboard")
    dashboard_dir = config['dashboard_dir']
    git_command = config['git_command']
    os.chdir(dashboard_dir)
    os.system('./' + git_command)


# Main -----------------------------
def main():
    # configure logger
    logging.basicConfig(
        filename="app.log",
        level=logging.DEBUG,
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("Running daily jobs for IQSS Dashboard %s" % str(ctime()))

    with open('config.json') as config_file:
        config = json.load(config_file)

    output_dir = config['output_dir']

    # Harvest Data
    # harvest_main_metrics(output_dir)
    # harvest_business_operations(output_dir)
    # harvest_cga(output_dir)
    # harvest_dataverse(output_dir)
    # harvest_css(output_dir)

    # aggregate and transform the data -------------------
    # aggregate_main_metrics(output_dir)
    aggregate_cga(output_dir)
    # aggregate_bo(output_dir, "business_operations")

    # Add and commit changes to the dashboard on Github
    # push_to_github(config)

    logging.info("Finished ETL cycle")


if __name__ == '__main__':
    main()
