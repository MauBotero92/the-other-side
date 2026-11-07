# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import TOS_Pipeline.src.dcc.maya.layout.ui.windows.shot_mask_window as mask
import importlib
import sys

# -------------------------------------
#
#       Execution
#
# -------------------------------------

def execute():

    sys.path.append('P:/The Other Side/Production/Assets/Scripts/')
    importlib.reload(mask)
    mask.run()