import unittest
import pandas as pd
import sqlite3
from flask import jsonify

import sys
import os
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../main')))

import app

class IntegrationTestCases(unittest.TestCase):
    def test_exhibitions_and_ml_model(self):
        mock_exhibition_results = app.get_exhibition_news("Caravaggio", "New York")
        mock_regression_results = app.apply_ml_model(mock_exhibition_results)
        self.assertEqual(type(mock_regression_results), pd.DataFrame,
                         "Failed to return machine learning results")

    def test_exhibitions_and_database(self):
        mock_exhibition_results = app.get_exhibition_news("Caravaggio", "New York")
        self.assertIsNone(app.save_to_database(mock_exhibition_results, "Caravaggio", "New York", "TEST_TABLE"),
                        "FAILED: Exhibitions Database was not created.")

    def test_art_museums_and_database(self):
        mock_museum_results = app.find_state_art_museums("New York")
        self.assertIsNone(app.save_to_database(mock_museum_results, "Caravaggio", "New York", "TEST_TABLE"),
                        "FAILED: Museum Database was not created.")

    def test_application_health(self):
        mock_museum_results = app.find_state_art_museums("New York")
        app.save_to_database(mock_museum_results, "Caravaggio", "New York", "TEST_TABLE")
        mock_name = app.database_name("Caravaggio", "New York")
        expected = "Health Status: Application is healthy", 200
        self.assertTrue(app.check_app_health(mock_name)==expected, "Test Failed: Application is NOT healthy.")

    def test_application_metrics(self):
        self.assertTrue(app.app_metrics["Number of Requests"]==0, "Test Failed: There are a certain number of requests.")
        self.assertTrue(app.app_metrics["Total Response Time"]==0.0, "Test Failed: Total Response Time should be 0.0.")
        app.app_metrics["Requests Per Second"] = 22.0
        self.assertTrue(app.app_metrics["Requests Per Second"]==22.0, "Test Failed: Requests Per Second should be 22.0.")


if __name__ == '__main__':
    unittest.main()
