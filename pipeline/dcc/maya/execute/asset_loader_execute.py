# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import TOS_Pipeline.pipeline.dcc.maya.ui.windows.asset_loader.asset_loader_window as al
import importlib
import sys

# -------------------------------------
#
#       Execution
#
# -------------------------------------

def execute():

    sys.path.append('P:/The Other Side/Production/Assets/Scripts/')
    importlib.reload(al)
    al.run()