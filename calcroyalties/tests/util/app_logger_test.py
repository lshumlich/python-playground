#!/bin/env python3

import unittest
import logging

from src.util.app_logger import AppLogger


class TestLoader(unittest.TestCase):
    def test_run(self):
        msg = "info This is a token message"

        log = AppLogger()
        logger = logging.getLogger()
        logger.level = logging.DEBUG

        logging.info(msg)

        m = log.stop_capture()

        self.assertTrue(m.startswith(msg))
