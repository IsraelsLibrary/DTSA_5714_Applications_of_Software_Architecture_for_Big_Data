import unittest
import pandas as pd
import sqlite3

import sys
import os
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../main')))

import app


class UnitTestCases(unittest.TestCase):
    def test_exhibitions(self):
        mock_exhibition_results = app.get_exhibition_news("Caravaggio", "New York")
        self.assertEqual(type(mock_exhibition_results), list,
                         "Test result failed. Did not return a list of exhibitions for Caravaggio artwork.")

    def test_no_exhibitions(self):
        mock_exhibition_results = app.get_exhibition_news("Easter Bunny", "Texas")
        self.assertEqual(type(mock_exhibition_results), list,
                         "Test result failed. Returned exhibition results where there should not be any.")

    def test_art_museums(self):
        mock_museum_results = app.find_state_art_museums("Virginia")
        self.assertEqual(type(mock_museum_results),list, "Failed to return art museum results")


    def test_ml_model(self):
        mock_exhibition_results = app.get_exhibition_news("Caravaggio", "New York")
        mock_regression_results = app.apply_ml_model(mock_exhibition_results)

        self.assertEqual(type(mock_regression_results), pd.DataFrame, "Failed to return machine learning results")

    def test_database(self):
        mock_test_data = [{"Key1": "Value1"}, {"Key2", "Value2"}]
        self.assertIsNone(app.save_to_database(mock_test_data, "Picasso", "California", "TEST_TABLE"),
                        "FAILED: Database was not created.")


if __name__ == '__main__':
    unittest.main()
