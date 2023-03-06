########################################################
# File: issa.py
# Description: This file defines functions for ISSA
# (Integer Sequence Spiral Art), such as functions to
# download OEIS data and plot the resulting spirals.
# Author: Elan Segarra
########################################################

import numpy as np
from urllib import request
from urllib.error import HTTPError
import requests
import re

def get_oeis_sequence_integers(seq_id, debug = False):
    """ Returns the integer sequence associated with the passed OEIS id 
        args:
            seq_id: (str) The 6-digit OEIS sequence ID (not including the 'A')
        returns: (dict) containing the indices and integers in the sequence
    """
    # Query the url of the sequence
    oeis_list_url = f"https://oeis.org/A{seq_id}/b{seq_id}.txt"
    try:
        lines = request.urlopen(oeis_list_url)
#         r = requests.get(url = oeis_list_url)
#         lines = r.text.split("\n")
    except HTTPError:
        print(f"HTTP 404 Error, so its likely the sequence 'A{seq_id}' does not exist.")
        return None
    
    seq_dict = dict()
    line_number = 0
    # Parse each line looking for a 2 numbers (the index and the integer)
    for line in lines:
        nums_found = re.findall('-*\d+', str(line))
        if len(nums_found) == 2:
            seq_dict[int(nums_found[0])] = int(nums_found[1])
        else:
            if debug: print(f"Strange text found on line {line_number}: '{line}'")
        line_number += 1
        
    return seq_dict

def get_oeis_sequence(seq_id, debug = False):
    """ Returns all the meta-data associated with the passed OEIS id 
        args:
            seq_id: (str) The 6-digit OEIS sequence ID (not including the 'A')
        returns: (dict) containing the meta data and longer sequence
    """
    oeis_url = f"https://oeis.org/search?q=id:A{seq_id}&fmt=json"
    r = requests.get(url = oeis_url)

    # extracting data in json format
    data = r.json()

    # Check that exactlt one result was recieved
    if data['count'] == 0:
        print("Query turned up 0 results.")
        return None
    elif data['count'] > 1:
        print(f"There were {data['count']} results returned, when there should have been 1.")
        return None

    seq_dict = data['results'][0]
    
    # Checking the ID and Adding form (to the way I typically represent it)
    assert seq_dict['number'] == int(seq_id), f"The sequence ID, '{seq_id}', does not match the 'number', {seq_dict['number']}. Investigate"
    seq_dict['seq_id'] = "A"+seq_id
    
    # Get the longer sequence of integers from this id
    longer_data = get_oeis_sequence_integers(seq_id)

    # Checking that longer sequence matches what was found in meta data
    meta_seq_num = len(seq_dict['data'].split(','))
    long_seq_start = list(longer_data.values())[0:meta_seq_num] # Grab same number of numbers
    long_seq_start = ",".join([str(k) for k in long_seq_start]) # Convert to string
    assert long_seq_start == seq_dict['data'], f"Longer sequence does not match what was found in the meta data for A{seq_id}"

    # Add the longer sequence to the meta data
    seq_dict['data_longer'] = list(longer_data.values())

    # Checking if negative numbers are included (at least among those found)
    seq_dict['is_positive'] = (np.array(seq_dict['data_longer'])>=0).all()
    
    return seq_dict

def test_oeis_functions():
    # Test where indices go from 0 to ...
    huh = get_oeis_sequence_integers('000055')
    huh10 = {k: huh[k] for k in list(huh.keys())[:10]}
    print(f"A000055: {huh10}")

    # Test where indices go from 1 to ...
    huh = get_oeis_sequence_integers('006968')
    huh10 = {k: huh[k] for k in list(huh.keys())[:10]}
    print(f"A006968: {huh10}")

    # Test with negatives
    huh = get_oeis_sequence_integers('001057')
    huh10 = {k: huh[k] for k in list(huh.keys())[:10]}
    print(f"A001057: {huh10}")

    # Test with non-existent sequence id
    huh = get_oeis_sequence_integers('000000')
    print(f"A000000: {huh}")

    # Test with strange start (ie offset)
    huh = get_oeis_sequence_integers('000109')
    huh10 = {k: huh[k] for k in list(huh.keys())[:10]}
    print(f"000109: {huh10}")