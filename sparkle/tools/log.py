import logging
import logging.config
import os

import yaml


def init_logging():
    """Initialize a logger from a configuration file to use throughout the project"""
    with open(os.path.join(os.path.dirname(__file__),'logging.conf'), 'r') as yf:
        config = yaml.load(yf)
    logging.config.dictConfig(config)
