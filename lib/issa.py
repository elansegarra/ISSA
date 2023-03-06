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


def gen_square_spiral(height, width, num_points, num_spirals, 
                      equi_type='revolution', spiral_type='linear'):
    """ Generates a list of coordinates in the defined spiral
    
        Args:
            height, weight, num_points, num_spirals: (int) self-explanatory
            equi_type: (str) Either 'distant' (meaning points are equally 
                spaced) or 'revolution' (meaning same number of points
                in each revolution)
            spiral_type: (str) Either 'linear' (revolutions shrinks by
                same distance) or 'multiplicative' (revolutions shrink
                by percentage).
        returns: (list, list) = (x-coords, y-coords)
    """
    # Define the bounding box
    bound_t =  height/2
    bound_b = -height/2
    bound_l = -width/2
    bound_r =  width/2
    
    if equi_type == 'revolution':
        spacing = 2*(height+width)*num_spirals/num_points
    elif equi_type == 'distant':
        raise NotImplementedError
    else:
        raiseNotImplementedError(f"Equi_type must be 'distant' or 'revolution', not '{requi_type}'")

    # Calculating spiral step size so the spiral scale happens with one cirle
    steps_in_revolution = 2*(height+width)/spacing

    # Defining maps to dictate moves and direction changes
    dir_map = {'u':np.array([0,  spacing]), 'd':np.array([0, -spacing]),
               'l':np.array([-spacing, 0]), 'r':np.array([ spacing, 0])}
    new_dir_map = {'u':'r','r':'d','d':'l','l':'u'}

    # Create the vertices by adding step and changing direction when needed
    curr_vert = np.array([bound_l,bound_b])
    curr_dir = 'u'
    vert_list = [curr_vert]
    for i in range(num_points-1):
        next_vert = curr_vert + dir_map[curr_dir]
        in_bounds = ((next_vert[0] >= bound_l) & (next_vert[0] <= bound_r) & 
                     (next_vert[1] >= bound_b) & (next_vert[1] <= bound_t))
        if not in_bounds:
            if curr_dir == 'u':
                next_vert[0] = next_vert[0] + (next_vert[1]-bound_t)
                next_vert[1] = bound_t
            elif curr_dir == 'r':
                next_vert[1] = next_vert[1] - (next_vert[0]-bound_r)
                next_vert[0] = bound_r
            elif curr_dir == 'd':
                next_vert[0] = next_vert[0] - (bound_b-next_vert[1])
                next_vert[1] = bound_b
            elif curr_dir == 'l':
                next_vert[1] = next_vert[1] + (bound_l-next_vert[0])
                next_vert[0] = bound_l
            curr_dir = new_dir_map[curr_dir]
        vert_list.append(next_vert)
        curr_vert = next_vert

    # Handling the scaling to spiral inward
    if spiral_type == "linear":
        scale = np.linspace(1,0,num_points)
    elif spiral_type == "multiplicative":
        spiral_scale_step = 0.01**(1/num_points)
        scale = spiral_scale_step**(np.linspace(0,num_points, num_points))
    else:
        raiseNotImplementedError(f"Equi_type must be 'linear' or 'multiplicative', not '{spiral_type}'")
    # Applying the scaling to the points to create spiral
    print(len(scale))
    x_vals = list(zip(*vert_list))[0]*scale
    y_vals = list(zip(*vert_list))[1]*scale

    return x_vals, y_vals