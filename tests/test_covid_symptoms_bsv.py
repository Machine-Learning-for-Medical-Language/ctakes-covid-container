import unittest
import logging
import requests
from enum import Enum
from typing import List, Dict
from test_covid_bsv import COVID_SYMPTOMS_BSV
from test_covid_bsv import SemType
from test_covid_bsv import list_bsv, call_ctakes, parse_response_bsv

class TestCovidSymptomsBSV(unittest.TestCase):
    """
    Symptoms of COVID-19
    https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html
    """
    def test_covid_symptoms_exist_in_response(self):

        for bsv in list_bsv(COVID_SYMPTOMS_BSV):

            response = call_ctakes(bsv.text)
            logging.debug(response)

            entries = parse_response_bsv(response, SemType.Identified)

            for e in entries:
                logging.debug(e.__dict__)

            cuis = [e.cui for e in entries]

            self.assertTrue(bsv.code in cuis, f'{bsv.__dict__} not found in response')


if __name__ == '__main__':
    unittest.main()
