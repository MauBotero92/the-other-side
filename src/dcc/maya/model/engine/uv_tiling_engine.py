# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import maya.mel as mel

# -------------------------------------
#
#       Export Config
#
# -------------------------------------

__all__ = [
    'mbr_egn_uv_tiling',
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
def mbr_egn_uv_tiling():
    mel.eval('generateAllUvTilePreviews')