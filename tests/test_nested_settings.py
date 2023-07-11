import unittest

from src.settings import settings

import nester

class TestNestedSettings(unittest.TestCase):
    def setUp(self):
        settings.load(["tests/config.json"])

    def test_01_default_settings(self):
       self.assertEqual(settings["PROJECT_DB_API_KEY"],"123a")
       self.assertEqual(settings["LOG_LEVEL"],"INFO")
       self.assertEqual(settings["DB_HOST"],"foobar:8081") 

       tdata = nester.get_settings()
       self.assertEqual(tdata["PROJECT_DB_API_KEY"],"123a")
       self.assertEqual(tdata["LOG_LEVEL"],"INFO")
       self.assertEqual(tdata["DB_HOST"],"foobar:8081") 