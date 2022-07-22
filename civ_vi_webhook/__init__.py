import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s- api - %(asctime)s - %(message)s')
api_logger = logging.getLogger("api server")
api_logger.setLevel(logging.DEBUG)
