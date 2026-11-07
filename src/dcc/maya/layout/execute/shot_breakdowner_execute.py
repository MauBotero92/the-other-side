# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import TOS_Pipeline.src.dcc.maya.layout.ui.windows.shot_breakdowner_window as sb
import importlib
import sys

# -------------------------------------
#
#       Execution
#
# -------------------------------------

def execute():

    sys.path.append('P:/The Other Side/Production/Assets/Scripts/')
    importlib.reload(sb)
    sb.run()