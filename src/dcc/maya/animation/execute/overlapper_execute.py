# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import TOS_Pipeline.src.dcc.maya.animation.ui.windows.overlapper_window as ol
import importlib
import sys

# -------------------------------------
#
#       Execution
#
# -------------------------------------

def execute():

    sys.path.append('P:/The Other Side/Production/Assets/Scripts/')
    importlib.reload(ol)
    ol.run()