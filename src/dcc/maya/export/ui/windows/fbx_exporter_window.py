# -------------------------------------
#
#       IMPORT MODULES
#
# -------------------------------------

import maya.cmds as cmds

version = cmds.about(version=True)
if version == '2023' or version == '2024':
    from PySide2 import QtWidgets as wdg
    from PySide2 import QtCore as core
    from PySide2 import QtGui as gui
    from shiboken2 import wrapInstance
elif version == '2025' or version == '2026':
    from PySide6 import QtWidgets as wdg
    from PySide6 import QtCore as core
    from PySide6 import QtGui as gui
    from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui

# -------------------------------------
#
#       GLOBAL VARIABLES
#
# -------------------------------------

MAIN_WINDOW = None
__version__ = '1.0'


# -------------------------------------
#
#       UI FUNCTIONS
#
# ------------------------------------- 

def get_maya_window():
    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    maya_main_window = wrapInstance(int(maya_main_window_ptr), wdg.QWidget)
    return maya_main_window


# -------------------------------------
#
#       FBX EXPORTER CLASS
#
# -------------------------------------

class FBX_Exporter(wdg.QMainWindow):

    def __init__(self, parent=None):
        super(FBX_Exporter, self).__init__(parent)

        # -------------------------------------
        #
        #       WINDOW TITLE AND SIZE
        #
        # -------------------------------------

        self.setWindowTitle(f"FBX Exporter {__version__}")
        self.setFocusPolicy(core.Qt.ClickFocus)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = 530

        self.resize(1100, initial_height)
        self.setMinimumSize(1100, min(initial_height, int(screen_height * 0.5)))
        self.setFixedSize(1100, initial_height)

        # -------------------------------------
        #
        #       MENU BAR
        #
        # -------------------------------------

        menubar = self.menuBar()

        edit_menu = menubar.addMenu('Edit')

        help_menu = menubar.addMenu('Help')

        # -------------------------------------
        #
        #       VARIABLE HELPERS
        #
        # -------------------------------------

        # -------------------------------------
        #
        #       STYLES AND VARIABLES
        #
        # -------------------------------------

        self.record_anim_layers_style = "background-color: #dd2323"

        self.le_disabled_style = "background-color: #3e3e3e"
        self.le_enabled_style = "background-color: #2a2a2a"

        # -------------------------------------
        #
        #       INITIALIZATION
        #
        # -------------------------------------

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.set_defaults()

    # -------------------------------------
    #
    #       CREATE WIDGETS
    #
    # -------------------------------------

    def create_widgets(self):

        # -------------------------------------
        #
        #       Anim Tab Left Widgets
        #
        # -------------------------------------

        # Actors Label
        self.anim_actors_label = wdg.QLabel('Actors')

        # Actors List
        self.anim_actors_list = wdg.QListWidget()
        self.anim_actors_list.setFixedWidth(250)
        self.anim_actors_list.setFixedHeight(410)

        # Export Nodes Label
        self.anim_export_nodes_label = wdg.QLabel('Export Nodes')

        # Export Nodes List
        self.anim_export_nodes_list = wdg.QListWidget()
        self.anim_export_nodes_list.setFixedWidth(250)
        self.anim_export_nodes_list.setFixedHeight(350)

        # New Export Node Button
        self.anim_new_export_node_btn = wdg.QPushButton('New Export Node')
        self.anim_new_export_node_btn.setFixedHeight(50)

        # -------------------------------------
        #
        #       Anim Tab Right Widgets
        #
        # -------------------------------------

        # Export Checkbox
        self.anim_export_check = wdg.QCheckBox('Export')

        # Move to Origin Checkbox
        self.anim_move_to_origin_check = wdg.QCheckBox('Move to Origin')

        # Zero Motion to Origin Checkbox
        self.anim_zero_motion_to_origim_check = wdg.QCheckBox('Zero Motion to Origin')

        # Use Sub Range Checkbox
        self.anim_use_sub_range_check = wdg.QCheckBox('Use Sub Range')

        # Start Frame LineEdit
        self.anim_start_frame_le = wdg.QLineEdit()
        self.anim_start_frame_le.setFixedWidth(70)

        # End Frame LineEdit
        self.anim_end_frame_le = wdg.QLineEdit()
        self.anim_end_frame_le.setFixedWidth(70)
        self.anim_end_frame_le.setAlignment(core.Qt.AlignLeft)

        # Export File Name Label
        self.anim_export_file_name_label = wdg.QLabel('Export File Name')

        # Export File Name LineEdit
        self.anim_export_file_name_le = wdg.QLineEdit()
        self.anim_export_file_name_le.setFixedWidth(350)

        # Browse Button
        self.anim_browse_btn = wdg.QPushButton('...')
        self.anim_browse_btn.setFixedWidth(30)

        # Record AnimLayers Button
        self.anim_record_anim_layers_btn = wdg.QPushButton('Record AnimLayers')
        self.anim_record_anim_layers_btn.setStyleSheet(self.record_anim_layers_style)
        self.anim_record_anim_layers_btn.setFixedWidth(150)
        self.anim_record_anim_layers_btn.setFixedHeight(50)

        # Preview AnimLayers Button
        self.anim_preview_anim_layers_btn = wdg.QPushButton('Preview AnimLayers')
        self.anim_preview_anim_layers_btn.setFixedWidth(150)
        self.anim_preview_anim_layers_btn.setFixedHeight(50)

        # Clear AnimLayers Button
        self.anim_clear_anim_layers_btn = wdg.QPushButton('Clear AnimLayers')
        self.anim_clear_anim_layers_btn.setFixedWidth(150)
        self.anim_clear_anim_layers_btn.setFixedHeight(50)

        # Export Selected Animation Button
        self.anim_export_selected_btn = wdg.QPushButton('Export Selected Animation')
        self.anim_export_selected_btn.setFixedWidth(210)
        self.anim_export_selected_btn.setFixedHeight(50)

        # Export All Animation for Selected Character Button
        self.anim_export_all_for_selected_char_btn = wdg.QPushButton('Export All For Selection Character')
        self.anim_export_all_for_selected_char_btn.setFixedWidth(210)
        self.anim_export_all_for_selected_char_btn.setFixedHeight(50)

        # Export All Animations Button
        self.anim_export_all_btn = wdg.QPushButton('Export All Animations')
        self.anim_export_all_btn.setFixedWidth(210)
        self.anim_export_all_btn.setFixedHeight(50)

        # -------------------------------------
        #
        #       Model Tab Left Widgets
        #
        # -------------------------------------

        # Root Joints Label
        self.model_root_joints_label = wdg.QLabel('Root Joints')

        # Root Joints List
        self.model_root_joints_list = wdg.QListWidget()
        self.model_root_joints_list.setFixedWidth(250)
        self.model_root_joints_list.setFixedHeight(350)

        # Tag as Origin Button
        self.model_tag_as_origin_btn = wdg.QPushButton('Tag as Origin')
        self.model_tag_as_origin_btn.setFixedHeight(50)

        # Export Nodes Label
        self.model_export_nodes_label = wdg.QLabel('Export Nodes')

        # Export Nodes List
        self.model_export_nodes_list = wdg.QListWidget()
        self.model_export_nodes_list.setFixedWidth(250)
        self.model_export_nodes_list.setFixedHeight(350)

        # New Export Node Button
        self.model_new_export_node_btn = wdg.QPushButton('New Export Node')
        self.model_new_export_node_btn.setFixedHeight(50)

        # Meshes Label
        self.model_meshes_label = wdg.QLabel('Meshes')

        # Meshes List
        self.model_meshes_list = wdg.QListWidget()
        self.model_meshes_list.setFixedWidth(250)
        self.model_meshes_list.setFixedHeight(350)

        # Add/Remove Meshes Button
        self.model_add_remove_meshes_btn = wdg.QPushButton('Add/Remove Meshes')
        self.model_add_remove_meshes_btn.setFixedHeight(50)

        # -------------------------------------
        #
        #       Model Tab Right Widgets
        #
        # -------------------------------------

        # Export Checkbox
        self.model_export_check = wdg.QCheckBox('Export')

        # Export File Name Label
        self.model_export_file_name_label = wdg.QLabel('Export File Name')

        # Export File Name LineEdit
        self.model_export_file_name_le = wdg.QLineEdit()
        self.model_export_file_name_le.setFixedWidth(350)

        # Browse Button
        self.model_browse_btn = wdg.QPushButton('...')
        self.model_browse_btn.setFixedWidth(30)

        # Export Selected Character Button
        self.model_export_selected_char_btn = wdg.QPushButton('Export Selected Character')
        self.model_export_selected_char_btn.setFixedWidth(210)
        self.model_export_selected_char_btn.setFixedHeight(50)

        # Export All Characters Button
        self.model_export_all_char_btn = wdg.QPushButton('Export All Characters')
        self.model_export_all_char_btn.setFixedWidth(210)
        self.model_export_all_char_btn.setFixedHeight(50)

    # -------------------------------------
    #
    #       CREATE LAYOUT
    #
    # -------------------------------------

    def create_layout(self):

        # -------------------------------------
        #
        #       Central Widget
        #
        # -------------------------------------

        central_wdg = wdg.QWidget()
        self.setCentralWidget(central_wdg)

        # -------------------------------------
        #
        #       Main Layout
        #
        # -------------------------------------

        main_lyt = wdg.QVBoxLayout(central_wdg)

        main_tab_lyt = wdg.QVBoxLayout()

        # -------------------------------------
        #
        #       Tab Widget and Layouts
        #
        # -------------------------------------

        self.tab_wdg = wdg.QTabWidget()

        # Animation Tab
        anim_tab_wdg = wdg.QWidget()
        anim_tab_lyt = wdg.QVBoxLayout(anim_tab_wdg)
        anim_tab_lyt.setContentsMargins(15, 15, 0, 0)

        # Model Tab
        model_tab_wdg = wdg.QWidget()
        model_tab_lyt = wdg.QVBoxLayout(model_tab_wdg)
        model_tab_lyt.setContentsMargins(15, 15, 0, 0)

        # Add Tabs
        self.tab_wdg.addTab(anim_tab_wdg, 'Animation')
        self.tab_wdg.addTab(model_tab_wdg, 'Model')

        # -------------------------------------
        #
        #       Animation Tab Layouts
        #
        # -------------------------------------

        # Anim Main Layout
        anim_main_lyt = wdg.QHBoxLayout()

        # Anim Actors Layout
        anim_actors_lyt = wdg.QVBoxLayout()

        # Anim Export Nodes Layout
        anim_export_nodes_lyt = wdg.QVBoxLayout()

        # Anim Settings Main Layout
        anim_settings_main_lyt = wdg.QVBoxLayout()
        anim_settings_main_lyt.setAlignment(core.Qt.AlignTop)
        anim_settings_main_lyt.setContentsMargins(20, 20, 0, 0)

        # Anim Settings Origin Layout
        anim_settings_origin_lyt = wdg.QHBoxLayout()
        anim_settings_origin_lyt.setAlignment(core.Qt.AlignCenter)
        anim_settings_origin_lyt.setContentsMargins(0, 0, 0, 0)

        # Anim Settings Sub Range Layout
        anim_settings_sub_range_lyt = wdg.QHBoxLayout()
        anim_settings_sub_range_lyt.setAlignment(core.Qt.AlignLeft)
        anim_settings_sub_range_lyt.setContentsMargins(0, 15, 0, 0)

        # Anim Settings Start Layout
        anim_settings_start_lyt = wdg.QHBoxLayout()

        # Anim Settings End Layout
        anim_settings_end_lyt = wdg.QHBoxLayout()

        # Anim Settings Start/End Layout
        anim_settings_start_end_lyt = wdg.QFormLayout()
        anim_settings_start_end_lyt.setAlignment(core.Qt.AlignLeft)
        anim_settings_start_end_lyt.addRow('Start Frame  ', anim_settings_start_lyt)
        anim_settings_start_end_lyt.addRow('End Frame  ', anim_settings_end_lyt)
        anim_settings_start_end_lyt.setLabelAlignment(core.Qt.AlignRight)

        self.anim_start_frame_label = anim_settings_start_end_lyt.labelForField(anim_settings_start_lyt)
        self.anim_end_frame_label = anim_settings_start_end_lyt.labelForField(anim_settings_end_lyt)

        # Anim Settings Export File Name Layout
        anim_settings_export_file_name_lyt = wdg.QHBoxLayout()
        anim_settings_export_file_name_lyt.setContentsMargins(0, 10, 0, 0)

        # Anim Settings AnimLayers Layout
        anim_settings_anim_layers_lyt = wdg.QHBoxLayout()
        anim_settings_anim_layers_lyt.setContentsMargins(0, 10, 0, 0)

        # Anim Settings Export Layout
        anim_settings_export_lyt = wdg.QVBoxLayout()
        anim_settings_export_lyt.setAlignment(core.Qt.AlignCenter)
        anim_settings_export_lyt.setContentsMargins(0, 10, 0, 0)

        # -------------------------------------
        #
        #       Model Tab Layouts
        #
        # -------------------------------------

        # Model Main Layout
        model_main_lyt = wdg.QHBoxLayout()

        # Model Root Joints Layout
        model_root_joints_lyt = wdg.QVBoxLayout()

        # Model Export Nodes Layout
        model_export_nodes_lyt = wdg.QVBoxLayout()

        # Model Meshes Layout
        model_meshes_lyt = wdg.QVBoxLayout()

        # Model Settings Main layout
        model_settings_main_lyt = wdg.QVBoxLayout()
        model_settings_main_lyt.setAlignment(core.Qt.AlignTop)
        model_settings_main_lyt.setContentsMargins(20, 20, 0, 0)

        # Model Settings Checkboxes Layout
        model_settings_checkboxes_lyt = wdg.QHBoxLayout()
        model_settings_checkboxes_lyt.setAlignment(core.Qt.AlignLeft)
        model_settings_checkboxes_lyt.setContentsMargins(0, 0, 0, 0)

        # Model Settings Export File Name Layout
        model_settings_export_file_name_lyt = wdg.QHBoxLayout()
        model_settings_export_file_name_lyt.setContentsMargins(0, 10, 0, 0)

        # Model Settings Export Layout
        model_settings_export_lyt = wdg.QVBoxLayout()
        model_settings_export_lyt.setAlignment(core.Qt.AlignCenter)
        model_settings_export_lyt.setContentsMargins(0, 10, 0, 0)

        # -------------------------------------
        #
        #       Layout Arrangement
        #
        # -------------------------------------

        # Main Layout
        main_lyt.addLayout(main_tab_lyt)

        # Main Tab Layout
        main_tab_lyt.addWidget(self.tab_wdg)

        # Anim Tab Layout
        anim_tab_lyt.addLayout(anim_main_lyt)

        # Anim Main Layout
        anim_main_lyt.addLayout(anim_actors_lyt)
        anim_main_lyt.addLayout(anim_export_nodes_lyt)
        anim_main_lyt.addLayout(anim_settings_main_lyt)
        anim_main_lyt.addStretch()

        # Anim Settings Main Layout
        anim_settings_main_lyt.addLayout(anim_settings_origin_lyt)
        anim_settings_main_lyt.addLayout(anim_settings_sub_range_lyt)
        anim_settings_main_lyt.addLayout(anim_settings_start_end_lyt)
        anim_settings_main_lyt.addLayout(anim_settings_export_file_name_lyt)
        anim_settings_main_lyt.addLayout(anim_settings_anim_layers_lyt)
        anim_settings_main_lyt.addLayout(anim_settings_export_lyt)

        # Model Tab Layout
        model_tab_lyt.addLayout(model_main_lyt)

        # Model Main Layout
        model_main_lyt.addLayout(model_root_joints_lyt)
        model_main_lyt.addLayout(model_export_nodes_lyt)
        model_main_lyt.addLayout(model_meshes_lyt)
        model_main_lyt.addLayout(model_settings_main_lyt)

        # Model Settings Main Layout
        model_settings_main_lyt.addLayout(model_settings_checkboxes_lyt)
        model_settings_main_lyt.addLayout(model_settings_export_file_name_lyt)
        model_settings_main_lyt.addLayout(model_settings_export_lyt)

        # -------------------------------------
        #
        #       Widgets Arrangement
        #
        # -------------------------------------

        # Anim Actors Widgets
        anim_actors_lyt.addWidget(self.anim_actors_label)
        anim_actors_lyt.addWidget(self.anim_actors_list)
        anim_actors_lyt.addStretch()

        # Anim Export Nodes Widgets
        anim_export_nodes_lyt.addWidget(self.anim_export_nodes_label)
        anim_export_nodes_lyt.addWidget(self.anim_export_nodes_list)
        anim_export_nodes_lyt.addWidget(self.anim_new_export_node_btn)
        anim_export_nodes_lyt.addStretch()

        # Anim Settings Origin Widgets
        anim_settings_origin_lyt.addWidget(self.anim_export_check)
        anim_settings_origin_lyt.addWidget(self.anim_move_to_origin_check)
        anim_settings_origin_lyt.addWidget(self.anim_zero_motion_to_origim_check)

        # Anim Settings Sub Range Widgets
        anim_settings_sub_range_lyt.addWidget(self.anim_use_sub_range_check)

        # Anim Settings Start/End Widgets
        anim_settings_start_lyt.addWidget(self.anim_start_frame_le)
        anim_settings_end_lyt.addWidget(self.anim_end_frame_le)

        # Anim Settings Export File Name Widgets
        anim_settings_export_file_name_lyt.addWidget(self.anim_export_file_name_label)
        anim_settings_export_file_name_lyt.addWidget(self.anim_export_file_name_le)
        anim_settings_export_file_name_lyt.addWidget(self.anim_browse_btn)
        anim_settings_export_file_name_lyt.addStretch()

        # Anim Settings Anim Layers Widgets
        anim_settings_anim_layers_lyt.addWidget(self.anim_record_anim_layers_btn)
        anim_settings_anim_layers_lyt.addWidget(self.anim_preview_anim_layers_btn)
        anim_settings_anim_layers_lyt.addWidget(self.anim_clear_anim_layers_btn)

        # Anim Settings Export Widgets
        anim_settings_export_lyt.addWidget(self.anim_export_selected_btn)
        anim_settings_export_lyt.addWidget(self.anim_export_all_for_selected_char_btn)
        anim_settings_export_lyt.addWidget(self.anim_export_all_btn)

        # Model Root Joints Widgets
        model_root_joints_lyt.addWidget(self.model_root_joints_label)
        model_root_joints_lyt.addWidget(self.model_root_joints_list)
        model_root_joints_lyt.addWidget(self.model_tag_as_origin_btn)
        model_root_joints_lyt.addStretch()

        # Model Export Nodes Widgets
        model_export_nodes_lyt.addWidget(self.model_export_nodes_label)
        model_export_nodes_lyt.addWidget(self.model_export_nodes_list)
        model_export_nodes_lyt.addWidget(self.model_new_export_node_btn)
        model_export_nodes_lyt.addStretch()

        # Model Meshes Widgets
        model_meshes_lyt.addWidget(self.model_meshes_label)
        model_meshes_lyt.addWidget(self.model_meshes_list)
        model_meshes_lyt.addWidget(self.model_add_remove_meshes_btn)
        model_meshes_lyt.addStretch()

        # Model Checkboxes Widgets
        model_settings_checkboxes_lyt.addWidget(self.model_export_check)

        # Model Export File Name Widgets
        model_settings_export_file_name_lyt.addWidget(self.model_export_file_name_label)
        model_settings_export_file_name_lyt.addWidget(self.model_export_file_name_le)
        model_settings_export_file_name_lyt.addWidget(self.model_browse_btn)
        model_settings_export_file_name_lyt.addStretch()

        # Model Export Widgets
        model_settings_export_lyt.addWidget(self.model_export_selected_char_btn)
        model_settings_export_lyt.addWidget(self.model_export_all_char_btn)

    # -------------------------------------
    #
    #       CREATE CONNECTIONS
    #
    # -------------------------------------

    def create_connections(self):

        self.tab_wdg.currentChanged.connect(self.tab_wdg_changed)

    # -------------------------------------
    #
    #       SET DEFAULTS
    #
    # -------------------------------------

    def set_defaults(self):

        # Animation Tab
        self.anim_export_check.setEnabled(False)
        self.anim_move_to_origin_check.setEnabled(False)
        self.anim_zero_motion_to_origim_check.setEnabled(False)

        self.anim_use_sub_range_check.setEnabled(False)
        self.anim_start_frame_le.setEnabled(False)
        self.anim_start_frame_le.setStyleSheet(self.le_disabled_style)
        self.anim_end_frame_le.setEnabled(False)
        self.anim_end_frame_le.setStyleSheet(self.le_disabled_style)

        self.anim_start_frame_label.setEnabled(False)
        self.anim_end_frame_label.setEnabled(False)

        self.anim_export_file_name_label.setEnabled(False)
        self.anim_export_file_name_le.setEnabled(False)
        self.anim_export_file_name_le.setStyleSheet(self.le_disabled_style)
        self.anim_browse_btn.setEnabled(False)
        self.anim_record_anim_layers_btn.setEnabled(False)
        self.anim_preview_anim_layers_btn.setEnabled(False)
        self.anim_clear_anim_layers_btn.setEnabled(False)

        # Model Tab
        self.model_export_check.setEnabled(False)

        self.model_export_file_name_label.setEnabled(False)
        self.model_export_file_name_le.setEnabled(False)
        self.model_export_file_name_le.setStyleSheet(self.le_disabled_style)
        self.model_browse_btn.setEnabled(False)

    # -------------------------------------
    #
    #       SIGNALS
    #
    # -------------------------------------

    def tab_wdg_changed(self, index):

        if index == 0:
            screen = wdg.QApplication.primaryScreen()
            screen_height = screen.availableGeometry().height()

            if screen_height < 720:
                initial_height = int(screen_height * 0.85)
            else:
                initial_height = 530

            self.setFixedSize(1100, initial_height)

        elif index == 1:
            screen = wdg.QApplication.primaryScreen()
            screen_height = screen.availableGeometry().height()

            if screen_height < 720:
                initial_height = int(screen_height * 0.85)
            else:
                initial_height = 530

            self.setFixedSize(1350, initial_height)

    # -------------------------------------
    #
    #       UTILITY METHODS
    #
    # -------------------------------------


# -------------------------------------
#
#       RUN FUNCTION
#
# -------------------------------------

def run():
    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = FBX_Exporter(parent=get_maya_window())
    MAIN_WINDOW.show()

run()