import unittest

from src.settings import settings

class TestSettings(unittest.TestCase):
    def test_01_default_settings(self):
        self.assertEqual(settings["PROJECT_DB_API_KEY"],"")
        self.assertEqual(settings["LOG_LEVEL"],"ERROR")
        self.assertEqual(settings["DB_HOST"],"localhost:8080")

    def test_02_load_settings(self):
        settings.load(["defaults.json"])

        self.assertEqual(settings["PROJECT_DB_API_KEY"],"")
        self.assertEqual(settings["LOG_LEVEL"],"ERROR")
    
    def test_03_multiload_settings_rev(self):
        settings.load(["tests/config.json", "defaults.json"])

        self.assertEqual(settings["PROJECT_DB_API_KEY"],"")
        self.assertEqual(settings["LOG_LEVEL"],"ERROR")    
        self.assertEqual(settings["DB_HOST"],"localhost:8080")

        # self.assertEqual(settings["extra_option"],"extra_option")
        # self.assertEqual(settings["EXTRA_OPTION"],"extra_option")

    def test_04_multiload_settings(self):
        settings.load(["defaults.json", "tests/config.json"])

        self.assertEqual(settings["PROJECT_DB_API_KEY"],"123a")
        self.assertEqual(settings["LOG_LEVEL"],"INFO")    
        self.assertEqual(settings["DB_HOST"],"foobar:8081")
    
    def test_05_use_setting_attributes(self):
        self.assertEqual(settings.LOG_LEVEL,"INFO")
        self.assertEqual(settings.DB_HOST,"foobar:8081")
        self.assertEqual(settings.EXTRA_OPTION,"extra_option")
        self.assertEqual(settings.extra_option,"extra_option")

    
    def test_06_upper_lowercased_keys(self):
        settings.load(["defaults.json", "tests/lowercasekeys.json"])

        self.assertEqual(settings["LOG_LEVEL"],"INFO")
        self.assertEqual(settings["log_level"],"INFO")    
        self.assertEqual(settings.log_level,"INFO")
        self.assertEqual(settings["DB_HOST"],"localhost:8080")

    def test_07_loadmissing(self):
        settings.load(["defaults.json", "tests/lowercasekeys.json", "tests/missing.json"])
        
        self.assertEqual(settings["LOG_LEVEL"],"INFO")
        self.assertEqual(settings["log_level"],"INFO")    
        self.assertEqual(settings.log_level,"INFO")
        self.assertEqual(settings["DB_HOST"],"localhost:8080")

    def test_08_loadmissing_all(self):
        settings.load(["defaults.json"])

        settings.load(["defaults-missing.json", "tests/missing.json"])

        self.assertEqual(settings["PROJECT_DB_API_KEY"],"")
        self.assertEqual(settings["LOG_LEVEL"],"ERROR")
        self.assertEqual(settings["DB_HOST"],"localhost:8080")

if __name__ == '__main__':
    unittest.main()
