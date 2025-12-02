import logging
import os


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # create formatter
        msg_format = '%(asctime)s - %(levelname)s - %(message)s'
        self.formatter = logging.Formatter(msg_format)

    def start(self):
        fh = self.create_file_logger()
        sh = self.create_stream_logger()

        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(sh)

        return self.logger

    def create_file_logger(self):
        cur_dir = os.path.dirname(__file__)
        parent = os.path.abspath(os.path.join(cur_dir, os.pardir))
        file_name = os.path.join(parent, 'log_file.log')

        # create file handler
        fh = logging.FileHandler(file_name)
        fh.setLevel(logging.DEBUG)

        fh.setFormatter(self.formatter)

        return fh

    def create_stream_logger(self):
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)

        sh.setFormatter(self.formatter)

        return sh


log = Logger().start()
