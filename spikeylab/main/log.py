import logging
import logging.config
import yaml

def init_logging():

    with open('logging.conf', 'r') as yf:
        config = yaml.load(yf)
    logging.config.dictConfig(config)