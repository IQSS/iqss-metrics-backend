from time import ctime

from business_operations import *
from cga import *
from css import *
from dataverse import *
import json
import os


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

    # harvest the data
    harvest_business_operations(output_dir)
    harvest_cga(output_dir)
    harvest_dataverse(output_dir)
    harvest_css(output_dir)

    # aggregate and transform the data
    # aggregate_cga(output_dir)
    aggregate_bo(output_dir, "business_operations")


    # add and commit changes to the dashboard
    logging.info("Pushing TSV to Github Dashboard")
    dashboard_dir = config['dashboard_dir']
    print(dashboard_dir)
    git_command = config['git_command']
    os.chdir(dashboard_dir)
    os.system('./' + git_command)

    logging.info("Finished ETL cycle")

if __name__ == '__main__':
    main()
