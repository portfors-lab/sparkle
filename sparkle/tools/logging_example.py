import logging
import logging.config
import os
import sys

import yaml


def init_logging():
    """Initialize a logger from a configuration file to use throughout the project"""
    with open(os.path.join(os.path.dirname(__file__),'logging.conf'), 'r') as yf:
        config = yaml.load(yf)
    logging.config.dictConfig(config)

def throws():
    raise RuntimeError('this is the error message')

def main():
    init_logging()
    logger = logging.getLogger('main')
    try:
        throws()
        return 0
    except Exception, err:
        logger.exception('testing: Error from throws():')
        return 1

if __name__ == '__main__':
    sys.exit(main())
