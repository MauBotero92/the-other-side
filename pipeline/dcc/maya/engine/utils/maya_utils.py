# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import maya.cmds as cmds

# -------------------------------------
#
#       Export Config
#
# -------------------------------------

__all__ = [
    'mbr_util_file_reference',
    'mbr_util_file_import',
    'mbr_util_open_file',
]

# -------------------------------------
#
#       Functions
#
# -------------------------------------

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_file_reference(path, maya_type, namespace):
    cmds.file(path, r=True, type=maya_type, ns=namespace, op='v=0')

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_file_import(path, maya_type):
    cmds.file(path, i=True, type=maya_type, ns=':', op='v=0')

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_open_file(path):
    cmds.file(path, open=True, ignoreVersion=True, force=True)