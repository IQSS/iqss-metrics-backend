import settings
from business_operations import *
from cga import *
from css import *
from rc import *
from dataverse import *
from psr import *
from metrics import *

# Main -----------------------------
def main():
    """
    Starting point of the backend process
    Args: none
    Returns: nothing
    """

    # configure logger
    config = settings.config
    output_dir = config['output_dir']

    # Harvest Data -----------------------------------
    #harvest_main_metrics(output_dir)
    harvest_business_operations(output_dir)
    harvest_cga(output_dir)
    harvest_harvard_dataverse(output_dir)
    harvest_dataverse(output_dir)
    harvest_css(output_dir)
    #harvest_rc(output_dir)
    #harvest_psr(output_dir)

    # aggregate and transform the data -------------------
    #aggregate_main_metrics(output_dir)
    aggregate_cga(output_dir)
    aggregate_bo(output_dir, "business_operations")
    aggregate_css(output_dir)
    aggregate_harvard_dataverse(output_dir)

    logging.info("Finished ETL cycle")

if __name__ == '__main__':
    main()
