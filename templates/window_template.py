# from TOS_Pipeline.dcc.maya.qt_compat import wdg, core, gui
# from TOS_Pipeline.dcc.maya.qt_utils import mbr_util_get_maya_window
#
# # -------------------------------------
#
# #       Global Variables
# #
# # -------------------------------------
#
# MAIN_WINDOW = None
# __VERSION__ = '4.0'
#
# # -------------------------------------
# #
# #       Main Class
# #
# # -------------------------------------
#
# class tos_scene_manager_window(wdg.QMainWindow):
#
#     def __init__(self, parent=None):
#         super(tos_scene_manager_window, self).__init__(parent)
#
#         # -------------------------------------
#         #
#         #       Window Title and Size
#         #
#         # -------------------------------------
#
#         # -------------------------------------
#         #
#         #       Menu Bar
#         #
#         # -------------------------------------
#
#         # -------------------------------------
#         #
#         #       Variable Helpers
#         #
#         # -------------------------------------
#
#         # -------------------------------------
#         #
#         #       Styles and Widget Variables
#         #
#         # -------------------------------------
#
#         # -------------------------------------
#         #
#         #       Initialization
#         #
#         # -------------------------------------
#
#         self.create_widgets()
#         self.create_layout()
#         self.create_connections()
#         self.set_defaults()
#
#     # -------------------------------------
#     #
#     #       Create Widgets
#     #
#     # -------------------------------------
#
#     def create_widgets(self):
#         pass
#
#     # -------------------------------------
#     #
#     #       Create Layout
#     #
#     # -------------------------------------
#
#     def create_layout(self):
#         pass
#
#         # -------------------------------------
#         #
#         #       Central Widget
#         #
#         # -------------------------------------
#
#         # -------------------------------------
#         #
#         #       Main Layout
#         #
#         # -------------------------------------
#
#         # -------------------------------------
#         #
#         #       Layout Arrangement
#         #
#         # -------------------------------------
#
#         # -------------------------------------
#         #
#         #       Widgets Arrangement
#         #
#         # -------------------------------------
#
#     # -------------------------------------
#     #
#     #       Create Connections
#     #
#     # -------------------------------------
#
#     def create_connections(self):
#         pass
#
#     # -------------------------------------
#     #
#     #       Set Defaults
#     #
#     # -------------------------------------
#
#     def set_defaults(self):
#         pass
#
#     # -------------------------------------
#     #
#     #       Widget Signals
#     #
#     # -------------------------------------
#
# # -------------------------------------
# #
# #       Run Function
# #
# # -------------------------------------
#
# def run():
#
#     global MAIN_WINDOW
#     if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
#         MAIN_WINDOW = tos_scene_manager_window(parent=mbr_util_get_maya_window())
#     MAIN_WINDOW.show()