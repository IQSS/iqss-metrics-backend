from time import ctime

from business_operations import *
from cga import *
from css import *
from rc import *
from dataverse import *
from psr import *
import json
import os
from metrics import *
import time
from rt_scripts import rt_harvard_dataverse

# Google sheets has limits on the number of calls per 100 seconds
SLEEP_TIME = 100

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
        level=logging.INFO,
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("Running daily jobs for IQSS Dashboard %s" % str(ctime()))

    with open('config.json') as config_file:
        config = json.load(config_file)

    output_dir = config['output_dir']

    # Harvest Data -----------------------------------

    # make sure we start with a clean slate
    # time.sleep(SLEEP_TIME)
    harvest_main_metrics(output_dir)
    harvest_business_operations(output_dir)
    harvest_cga(output_dir)
    #
    # # wait for the next batch
    time.sleep(SLEEP_TIME)
    harvest_dataverse(output_dir)
    harvest_css(output_dir)
    harvest_rc(output_dir)


    rt_harvard_dataverse(output_dir)  #
    harvest_psr(output_dir)
    harvest_harvard_dataverse(output_dir)

    # aggregate and transform the data -------------------
    aggregate_main_metrics(output_dir)
    aggregate_cga(output_dir)
    aggregate_bo(output_dir, "business_operations")
    aggregate_css(output_dir)
    aggregate_harvard_dataverse(output_dir)
    #
    # # Add and commit changes to the dashboard on Github -------------------------
    push_to_github(config)
    #
    logging.info("Finished ETL cycle")

if __name__ == '__main__':
    main()
