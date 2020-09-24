import settings
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

# Google sheets has limits on the number of calls per 100 seconds
SLEEP_TIME = 100


# Main -----------------------------
def main():
    # configure logger
    config = settings.config
    output_dir = config['output_dir']

    # Harvest Data -----------------------------------

    # make sure we start with a clean slate
    # time.sleep(SLEEP_TIME)
    harvest_main_metrics(output_dir)
    harvest_business_operations(output_dir)
    harvest_cga(output_dir)
    #
    # # wait for the next batch
    # time.sleep(SLEEP_TIME)
    harvest_harvard_dataverse(output_dir, config)
    harvest_dataverse(output_dir)
    harvest_css(output_dir)
    harvest_rc(output_dir)
    harvest_psr(output_dir)

    # aggregate and transform the data -------------------
    aggregate_main_metrics(output_dir)
    aggregate_cga(output_dir)
    aggregate_bo(output_dir, "business_operations")
    aggregate_css(output_dir)
    aggregate_harvard_dataverse(output_dir)
    #
    logging.info("Finished ETL cycle")


if __name__ == '__main__':
    main()
