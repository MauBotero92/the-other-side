# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import TOS_Pipeline.pipeline.dcc.maya.engine.procedures.version_control_engine as vc
import importlib
import sys

# -------------------------------------
#
#       Execution
#
# -------------------------------------

def execute():

    sys.path.append('P:/The Other Side/Production/Assets/Scripts/')
    importlib.reload(vc)
    vc.mbr_egn_version_up_scene()