# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import os
import maya.cmds as cmds

from TOS_Pipeline.src.core.fs_utils import *
from TOS_Pipeline.src.dcc.maya.utils.maya_utils import mbr_util_reopen_cur_file

# -------------------------------------
#
#       Export Config
#
# -------------------------------------

__all__ = [
    'mbr_egn_refresh_textures',
]

# -------------------------------------
#
#       Functions
#
# -------------------------------------

'''
PURPOSE:        Clean up .tex files on given path
PROCEDURE:      > Declare path, list of .tex files, and empty list for the .tex files
                > Append to the empty list the files on file_list that ends on .tex
                > Remove every item on the tex_files list
                > Regenerate UV Tile Previews and pop up a confirm dialog window
ASSUMPTIONS:
'''
def mbr_egn_clean_texture_files(tex_path, char):

    path = tex_path
    file_list = mbr_util_list_directory_contents(path, content_type='files')
    tex_files = []

    for item in file_list:
        if item.endswith('.tex'):
            tex_files.append(item)

    for item in tex_files:
        os.remove(f"{path}/{item}")

    mbr_util_reopen_cur_file()
    cmds.confirmDialog(m=f"{char} textures cleaned up!")

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_refresh_textures():

    response = cmds.confirmDialog(t='John Textures Reload', m='Variation', b=[
        'John Healthy',
        'John Sick',
        'Danni Pregnant'
    ])

    if response == 'John Healthy':
        mbr_egn_clean_texture_files(
            'P:/The Other Side/Production/Assets/Chars/John_Healthy/Textures/v006',
            'John Healthy')

    elif response == 'John Sick':
        mbr_egn_clean_texture_files(
            'P:/The Other Side/Production/Assets/Chars/John_Sick/Textures/v1',
            'John Sick')

    elif response == 'Danni Pregnant':

        mbr_egn_clean_texture_files(
            'P:/The Other Side/Production/Assets/Chars/Danni_Pregnant/Textures/v01',
            'Danni Pregnant')