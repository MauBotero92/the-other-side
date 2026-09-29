from TOS_Pipeline.pipeline.dcc.maya.functions.utils.qt_compat import wrapInstance as wrap
from TOS_Pipeline.pipeline.dcc.maya.functions.utils.qt_compat import wdg
import maya.OpenMayaUI as omui

'''
PURPOSE:        Get Maya Main Window and return it
PROCEDURE:      > Save Maya Main Window on a variable
                > Use wrapInstance to make the Maya Main Window usable in a Qt Window
ASSUMPTIONS:    None
'''
def mbr_util_get_maya_window():

    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    maya_main_window = wrap(int(maya_main_window_ptr), wdg.QWidget)
    return maya_main_window


