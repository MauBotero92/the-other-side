# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import TOS_Pipeline.pipeline.dcc.maya.engine.procedures.refresh_textures_engine as rtex
import importlib
import sys

# -------------------------------------
#
#       Execution
#
# -------------------------------------

def execute():

    sys.path.append('P:/The Other Side/Production/Assets/Scripts/')
    importlib.reload(rtex)
    rtex.mbr_egn_refresh_textures()