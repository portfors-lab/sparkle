import os
import logging
import logging.config
import yaml

def init_logging():

    with open(os.path.join(os.path.dirname(__file__),'logging.conf'), 'r') as yf:
        config = yaml.load(yf)
    logging.config.dictConfig(config)