# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import os
import maya.mel as mel
import maya.cmds as cmds

from TOS_Pipeline.src.core.fs_utils import *

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

def mbr_egn_john_healthy_refresh_textures():

    path = 'P:/The Other Side/Production/Assets/Chars/John_Healthy/Textures/v006'
    file_list = mbr_util_list_directory_contents(path, content_type='folders')
    # file_list = listFilesInDirectory(path)
    tex_files = []

    for item in file_list:
        if item.endswith('.tex'):
            tex_files.append(item)

    for item in tex_files:
        os.remove(f"{path}\\{item}")

    mel.eval('generateAllUvTilePreviews')
    cmds.confirmDialog(m='John Healthy texture files cleaned up!')


def mbr_egn_john_sick_refresh_textures():

    path = 'P:/The Other Side/Production/Assets/Chars/John_Sick/Textures/v1'
    file_list = mbr_util_list_directory_contents(path, content_type='folders')
    # file_list = listFilesInDirectory(path)
    tex_files = []

    for item in file_list:
        if item.endswith('.tex'):
            tex_files.append(item)

    for item in tex_files:
        os.remove(f"{path}\\{item}")

    mel.eval('generateAllUvTilePreviews')
    cmds.confirmDialog(m='John Healthy texture files cleaned up!')


def mbr_egn_refresh_textures():

    response = cmds.confirmDialog(t='John Textures Reload', m='Variation', b=['John Healthy', 'John Sick'])

    if response == 'John Healthy':
        mbr_egn_john_healthy_refresh_textures()

    elif response == 'John Sick':
        mbr_egn_john_sick_refresh_textures()