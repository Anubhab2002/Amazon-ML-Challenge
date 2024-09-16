import re
import constants
import os
import requests
import pandas as pd
import multiprocessing
import time
from time import time as timer
from tqdm import tqdm
import numpy as np
from pathlib import Path
from functools import partial
import requests
import urllib
from PIL import Image
import ast

def common_mistake(unit):
    if unit in constants.allowed_units:
        return unit
    if unit.replace('ter', 'tre') in constants.allowed_units:
        return unit.replace('ter', 'tre')
    if unit.replace('feet', 'foot') in constants.allowed_units:
        return unit.replace('feet', 'foot')
    return unit

import re

def safe_eval_(x):
    try:
        # Try to evaluate the expression
        return eval(x)
    except (SyntaxError, NameError, TypeError):
        # If it's not valid Python syntax or raises a name error, skip it
        # print(f"Skipping invalid Python syntax: '{x}'")
        return None
    
def safe_eval(x):
    try:
        # Parse the string into a Python literal
        parsed = ast.literal_eval(x)
        if isinstance(parsed, (list, tuple)) and len(parsed) == 2:
            # Return the two elements combined as a string
            print(str(parsed[0]) + ' ' + str(parsed[1]))
            return f"{parsed[0]} {parsed[1]}"
        return x  # If it's not a list/tuple of length 2, return as is
    except (SyntaxError, ValueError, TypeError):
        # Catch invalid syntax or types and skip evaluation
        # print(f"Skipping invalid Python syntax: '{x}'")
        return None

import re

def clean_prediction(prediction):
    # Remove all square brackets
    prediction = prediction.replace('[', '').replace(']', '')
    prediction = prediction.replace('"', '')
    prediction = prediction.replace(",", "")
    prediction = prediction.split()
    if len(prediction)>2:
        prediction = prediction[0] + ' ' + prediction[2]
    else:
        prediction = prediction[0] + ' ' + prediction[1]
    return prediction

def is_number(s):
    try:
        float(s)  # Try converting the string to a float
        return True
    except ValueError:
        return False
    

def correct_prediction(prediction, error_type=1):
    if error_type==None:
        return prediction
    if error_type == 1:
        prediction = clean_prediction(prediction)
        unit = prediction.split()[1]
        value = prediction.split()[0]
        
        # check if value is a legit floating point
        if not is_number(value):
            return ""
        
        if unit not in constants.allowed_units:
                print(f"Invalid unit '{unit}'\n")
                return ""
            
        return prediction
    elif error_type == 2:
        return ""

def parse_string(s, index=None):
    s_stripped = "" if s == None or str(s) == 'nan' else s.strip()
    if s_stripped == "":
        return None, None, None
    
    pattern = re.compile(r'^-?\d+(\.\d+)?\s+[a-zA-Z\s]+$')
    
    if not pattern.match(s_stripped):
        if index is not None:
            print(f"Invalid format at index {index}: '{s}'\n")
        else:
            print(f"Invalid format: '{s}'\n")
        # s_stripped = correct_prediction(s_stripped, error_type=1)
        return None, None, 1
    
    parts = s_stripped.split(maxsplit=1)
    number = float(parts[0])
    unit = common_mistake(parts[1])

    if unit not in constants.allowed_units:
        if index is not None:
            print(f"Invalid unit '{unit}' at index {index}\n")
        else:
            print(f"Invalid unit '{unit}'\n")
        # s_stripped = correct_prediction(s_stripped, error_type=2)
        return None, None, 2
    
    return number, unit, None


def create_placeholder_image(image_save_path):
    try:
        placeholder_image = Image.new('RGB', (100, 100), color='black')
        placeholder_image.save(image_save_path)
    except Exception as e:
        return

def download_image(image_link, save_folder, retries=3, delay=3):
    if not isinstance(image_link, str):
        return

    filename = Path(image_link).name
    image_save_path = os.path.join(save_folder, filename)

    if os.path.exists(image_save_path):
        return

    for _ in range(retries):
        try:
            urllib.request.urlretrieve(image_link, image_save_path)
            return
        except:
            time.sleep(delay)
    
    create_placeholder_image(image_save_path) #Create a black placeholder image for invalid links/images

def download_images(image_links, download_folder, allow_multiprocessing=True):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    if allow_multiprocessing:
        download_image_partial = partial(
            download_image, save_folder=download_folder, retries=3, delay=3)

        with multiprocessing.Pool(64) as pool:
            list(tqdm(pool.imap(download_image_partial, image_links), total=len(image_links)))
            pool.close()
            pool.join()
    else:
        for image_link in tqdm(image_links, total=len(image_links)):
            download_image(image_link, save_folder=download_folder, retries=3, delay=3)