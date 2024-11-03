import os
import logging
import datetime
from typing import Optional

from PySide6.QtWidgets import QStatusBar


class Log:
    def __init__(self, level=logging.INFO):
        self.time = datetime.datetime.now()
        self.path = ''

        self.level = level
        self.file_handler = None
        self.status_bar: Optional[QStatusBar] = None

        logging.basicConfig(level=logging.INFO)
        self.enable_file_record()

    def enable_file_record(self):
        os.makedirs('log', exist_ok=True)
        self.path = os.path.join('log', f'{self.format_time()}.log')
        self.file_handler = logging.FileHandler(self.path)
        self.file_handler.setLevel(self.level)
        self.file_handler.setFormatter(
            fmt=logging.Formatter(
                fmt="%(asctime)s [%(levelname)-7s] -> %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logging.getLogger().addHandler(self.file_handler)

    def remove_file_record(self):
        logging.getLogger().removeHandler(self.file_handler)

    def format_time(self, fmt: str = '%y%m%d%H%M%S'):
        return self.time.strftime(fmt)

    def register_status_bar(self, status_bar: QStatusBar):
        if self.status_bar is not None:
            self.status_bar = status_bar

    def sync_status(self, msg):
        if msg is None or self.status_bar is None:
            return
        self.status_bar.showMessage(text=msg, timeout=10)

    @staticmethod
    def info(msg):
        logging.log(logging.INFO, msg)

    def error(self, msg):
        logging.error(msg)
        self.sync_status(msg)

    def warn(self, msg):
        logging.warning(msg)
        self.sync_status(msg)

    def debug(self, msg):
        logging.debug(msg)
        self.sync_status(msg)

    @staticmethod
    def line(sep=''):
        logging.info(f'---------------------------{sep}------------------------------')


LOG = Log()
