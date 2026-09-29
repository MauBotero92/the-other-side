# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import TOS_Pipeline.pipeline.dcc.maya.ui.windows.scene_manager.scene_manager_window as sm
import importlib

# -------------------------------------
#
#       Execution
#
# -------------------------------------

importlib.reload(sm)
sm.run()