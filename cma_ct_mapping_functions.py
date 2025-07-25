import re


## Step 0: Define functions to find CTUID, CMA Name and CMA Code ##
def extract_cma_code(geo_string):

    geo_string = geo_string.replace(',', ' ')
    geo_string = geo_string.replace('(', ' (')

    geo_string_split = geo_string.split(' ')

    cma_index = 0

    for idx, val in enumerate(geo_string_split):

        if len(val) == 3 and bool(re.fullmatch(r'\d+', val)):

            cma_index = idx

    return geo_string_split[cma_index]

def extract_cma_string(geo_string):

    ## Handle commas and brackets for CAs ##
    geo_string = geo_string.replace(',', ' ')
    geo_string = geo_string.replace('(', ' (')

    ## Set up list for geo string to be manipulated ##
    geo_string_split = geo_string.split(' ')

    cma_index = 0

    for idx, val in enumerate(geo_string_split):

        if len(val) == 3 and bool(re.fullmatch(r'\d+', val)):

            cma_index = idx

    return ' '.join(geo_string_split[:cma_index - 1]).strip()

def extract_ct_string(geo_string):

    geo_string = geo_string.replace(',', ' ')
    geo_string = geo_string.replace('(', ' (')

    ## Set up list for geo string to be manipulated ##
    geo_string_split = geo_string.split(' ')

    return ' '.join(geo_string_split[2:]).strip()

def extract_ct_uid_code(geo_string):

    geo_string_split = geo_string.split(' ')

    return geo_string_split[0]