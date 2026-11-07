# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import TOS_Pipeline.src.dcc.maya.model.engine.uv_tiling_engine as uv
import importlib
import sys

# -------------------------------------
#
#       Execution
#
# -------------------------------------

def execute():

    sys.path.append('P:/The Other Side/Production/Assets/Scripts/')
    importlib.reload(uv)
    uv.mbr_egn_uv_tiling()