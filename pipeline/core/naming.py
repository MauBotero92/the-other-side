import re

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_natural_key(text):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', text)]