import os, logging
import unittest
import requests
from enum import Enum
from typing import List, Dict

COVID_BSV = os.path.join(os.pardir, 'covid.bsv')
COVID_SYMPTOMS_BSV = os.path.join(os.getcwd(), 'covid_symptoms.bsv')

class SemType(Enum):
    DiseaseDisorder = 'DiseaseDisorderMention'
    SignSymptom = 'SignSymptomMention'
    AnatomicSite = 'AnatomicalSiteMention'
    Medication = 'MedicationMention'
    Procedure = 'ProcedureMention'
    Identified = 'IdentifiedAnnotation'

class BSV(object):
    def __init__(self, code=None, cui=None, text=None):
        """
        :param code: CODE or "identified annotation" code
        :param cui: CUI from UMLS or NA for "identified annotation"
        :param text: string representation to send to ctakes
        """
        self.code = code
        self.cui = cui
        self.text = text

def list_bsv(filename=COVID_BSV) -> List[BSV]:
    """
    :param filename: BSV filename to parse
    :return: list of BSV entries
    """
    entries = list()

    with open(filename) as f:
        for line in f.read().splitlines():
            cols = line.split('|')
            entries.append(BSV(code= cols[0], cui=cols[1], text=cols[2]))

    return entries

def get_url_ctakes() -> str:
    """
    :return: CTAKES_URL_REST env variable or default using localhost
    """
    return os.environ.get('CTAKES_URL_REST', 'http://localhost:8080/ctakes-web-rest/service/analyze')

def call_ctakes(sentence:str, url=get_url_ctakes()) -> dict:
    """
    :param sentence: clinical text to send to cTAKES
    :param url: cTAKES REST server fully qualified path
    :return:
    """
    return requests.post(url, data=sentence).json()


def parse_response_bsv(response:dict, sem_type:SemType)-> List[BSV]:
    """
    :param response: cTAKES response
    :param sem_type: Semantic Type (Group)
    :return: List of BSV entries from cTAKES
    """
    bsv_res = list()

    for atts in response.get(sem_type.value, []):
        for concept in atts['conceptAttributes']:
            bsv_res.append(BSV(concept['code'], concept['cui'], atts['text']))
    return bsv_res

class TestSimpleExtractCUI(unittest.TestCase):

    def test_bsv_entries_exist_in_response(self):

        for bsv in list_bsv():

            if 'NA' == bsv.cui:
                logging.debug(bsv.text)

                response = call_ctakes(bsv.text)
                logging.debug(response)

                entries = parse_response_bsv(response, SemType.Identified)

                for e in entries:
                    logging.debug(e.__dict__)

                cuis = [e.cui for e in entries]

                self.assertTrue(bsv.code in cuis, f'{bsv.__dict__} not found in response')


if __name__ == '__main__':
    unittest.main()
