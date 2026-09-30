# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import TOS_Pipeline.pipeline.dcc.maya.ui.windows.scene_manager.scene_manager_window as sm
import importlib
import sys

# -------------------------------------
#
#       Execution
#
# -------------------------------------

def execute():
    sys.path.append('P:/The Other Side/Production/Assets/Scripts/')
    importlib.reload(sm)
    sm.run()