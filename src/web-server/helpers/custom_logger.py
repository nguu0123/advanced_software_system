import logging

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)


class CustomLogger:
    def get_logger(self):
        log_formatter = logging.Formatter(
            "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)

        return root_logger
