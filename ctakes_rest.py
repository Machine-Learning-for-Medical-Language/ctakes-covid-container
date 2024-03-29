#!/usr/bin/env python3.6
from typing import List, Dict, Tuple
import requests

CTAKES_URL = 'http://localhost:8080/ctakes-web-rest/service/analyze'

def add_cuis(json:dict, sem_type:str, cui_list: list) -> List:
    """
    :param json: response from CTAKES REST
    :param sem_type: Semantic Type, for example "DiseaseDisorderMention"
    :param cui_list: list of CUI (Note: this function changes the result passed)
    :return: list of CUI from ctakes JSON response containing the mention type like "DiseaseDisorderMention"
    """
    for atts in json.get(sem_type, []):
        begin = atts['begin']
        end = atts['end']
        polarity = atts['polarity']
        for cuiAtts in atts['conceptAttributes']:
            cui_list.append( (cuiAtts['cui'], begin, end) )
   
    return cui_list

def get_cuis(json) -> List:
    """
    :param json: response from CTAKES REST
    :return: list of CUI for disease, signssymptoms, anotomicsites, procedures, and identifed (from covid.bsv)
    """
    cuis = []

    cuis = add_cuis(json, 'DiseaseDisorderMention', cuis)
    cuis = add_cuis(json, 'SignSymptomMention', cuis)
    cuis = add_cuis(json, 'AnatomicalSiteMention', cuis)
    cuis = add_cuis(json, 'MedicationMention', cuis)
    cuis = add_cuis(json, 'ProcedureMention', cuis)
    cuis = add_cuis(json, 'IdentifiedAnnotation', cuis)

    return cuis

def process_sentence(sent, url=CTAKES_URL) -> List:
    """
    :param sent: sentence of clinical text to send to cTAKES
    :param url: CATKES default http://localhost:8080/ctakes-web-rest/service/analyze
    :return: list of CUIs
    """
    url = 'http://localhost:8080/ctakes-web-rest/service/analyze'
    r = requests.post(url, data=sent)
    return get_cuis(r.json())

def get_cui_maps(sent) -> Tuple:
    """
    :param sent: sentence of clinical text to send to cTAKES
    :return: two dictionaries as Tuple, containing "start" and "end" maps of CUI
    """
    cuis = process_sentence(sent)
    cui_start_map = {}
    cui_end_map = {}
    for cui,begin,end in cuis:
        if begin in cui_start_map:
            # Collision: if existing cui with this begin ends later (is longer), skip this cui
            collision_end = cui_start_map[begin][1]
            if collision_end > end:
                continue 
            else:
                # new cui is longer span than old one, so remove the old end from the end map
                cui_end_map.pop(collision_end, None)

        if end in cui_end_map:
            # Collision: if existing cui with this end begins earlier (is longer), skip this cui
            collision_begin = cui_end_map[end][1]
            if collision_begin < begin:
                continue 
            else:
                # new cui is longer span than old one, so remove the old begin from the start map
                cui_start_map.pop(collision_begin, None)
        
        # If we get this far then our cui has no collision or is longer than existing spans it collides with.
        cui_start_map[begin] = (cui, end)
        cui_end_map[end] = (cui, begin)

    return cui_start_map, cui_end_map

def get_mixed_sent(sent:str) -> str:
    """
    :param sent: sentence of clinical text to send to cTAKES
    :return: CUI list, reversed order (???)
    """
    import numpy as np
    # get cuis for this entity:
    _, cui_end_map = get_cui_maps(sent)
    cui_ends_reversed = list(np.sort(list(cui_end_map.keys())))
    cui_ends_reversed.reverse()
    last_start = len(sent) + 1

    # Replace text with cuis
    for cui_end in cui_ends_reversed:
        if cui_end > last_start:
            continue
        (cui, cui_start) = cui_end_map[cui_end]
        sent = sent[:cui_start] + cui + sent[cui_end:]
        last_start = cui_start
    
    return sent
