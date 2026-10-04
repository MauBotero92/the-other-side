# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import TOS_Pipeline.pipeline.dcc.maya.ui.windows.shot_creator.shot_creator_window as sc
import importlib
import sys

# -------------------------------------
#
#       Execution
#
# -------------------------------------

def execute():

    sys.path.append('P:/The Other Side/Production/Assets/Scripts/')
    importlib.reload(sc)
    sc.run()