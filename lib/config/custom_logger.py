import logging

def get_logger(name):
    """
    @summary: Custom logger which logs according to the needs of this application.
    The formatter, log level and handler settings can be changed here.
    @return: logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('/logs/email_app.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)s: %(lineno)s :  %(funcName)s() -> %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

