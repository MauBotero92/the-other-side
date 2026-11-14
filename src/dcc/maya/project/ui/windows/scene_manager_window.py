# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

from TOS_Pipeline.src.dcc.maya.utils.qt_compat import wdg, core, gui
from TOS_Pipeline.src.dcc.maya.utils.qt_utils import mbr_util_get_maya_window
from TOS_Pipeline.src.dcc.maya.utils.qt_classes import MBR_TOS_Base_Window
from TOS_Pipeline.src.dcc.maya.utils.qt_helpers import *
from TOS_Pipeline.src.dcc.maya.utils.maya_utils import *

from TOS_Pipeline.src.core.fs_utils import *
from TOS_Pipeline.src.core.naming import *

from TOS_Pipeline.src.dcc.maya.project.engine.scene_manager_engine import *

import maya.cmds as cmds

# -------------------------------------
#
#       Global Variables
#
# -------------------------------------

MAIN_WINDOW = None
__VERSION__ = '4.0'

# -------------------------------------
#
#       Main Class
#
# -------------------------------------

class tos_scene_manager_window(MBR_TOS_Base_Window):

    def __init__(self, parent=None):
        super(tos_scene_manager_window, self).__init__(parent,
                                                       title=f"TOS Scene Manager {__VERSION__}",
                                                       width=700,
                                                       height=820)

        # -------------------------------------
        #
        #       Widget Variables
        #
        # -------------------------------------

        self.title_frame = None
        self.title_label = None
        self.project_frame = None
        self.project_label = None

        self.wks_read_le = None
        self.set_project_btn = None

        self.sequence_combo = None
        self.stage_combo = None
        self.shot_number_combo = None
        self.lvl_combos = None

        self.file_list = None

        self.thumbnail_label = None
        self.metadata_date_label = None
        self.metadata_frame_range_label = None
        self.metadata_artist_label = None
        self.metadata_size_label = None

        self.load_btn = None

        # -------------------------------------
        #
        #       Initialization Variables
        #
        # -------------------------------------

        # Init Sequences List
        self.project_path = mbr_util_get_tos_path()

        if self.project_path:
            self.sequences_path = f"{self.project_path}Sequences"
        else:
            self.sequences_path = None

        # Current workspace variable
        if self.sequences_path:
            self.current_wks = cmds.workspace(q=True, rd=True)
        else:
            self.current_wks = 'Project is not set'

        # Combos first click variables
        self.sequence_first_click = True
        self.shot_number_first_click = True
        self.stage_first_click = True

        # Init Variables
        self.current_file = None

        self.sequence_text, self.shot_number_text, self.stage_text = None, None, None
        self.sequence_dir, self.shot_number_dir, self.stage_dir = None, None, None

        self.project_wks = None
        self.sequences_list_initial = None
        self.current_sequence = None
        self.shot_number_list_initial = None
        self.shot_number_list_sorted = None
        self.shot_number_list = None
        self.current_shot_number = None
        self.current_stage = None
        self.stages_list_initial = None
        self.stages_list_filtered = None
        self.stages_list = None
        # self.current_file = None

        # -------------------------------------
        #
        #       Initialization
        #
        # -------------------------------------

        self.build_ui()

    # -------------------------------------
    #
    #       Create Widgets
    #
    # -------------------------------------

    def create_widgets(self):

        # -------------------------------------
        #
        #       Title Widgets
        #
        # -------------------------------------

        # Title Frame
        self.title_frame = wdg.QFrame()
        self.title_frame.setStyleSheet(self.title_frame_style)

        # Title Label
        self.title_label = wdg.QLabel('Scene Manager')
        self.title_label.setStyleSheet(self.title_label_style)
        self.title_label.setAlignment(core.Qt.AlignCenter)

        # The Other Side Frame
        self.project_frame = wdg.QFrame()
        self.project_frame.setStyleSheet(self.project_frame_style)

        # The Other Side Label
        self.project_label = wdg.QLabel('The Other Side')
        self.project_label.setStyleSheet(self.project_label_style)
        self.project_label.setAlignment(core.Qt.AlignCenter)

        # -------------------------------------
        #
        #       Upper Widgets
        #
        # -------------------------------------

        # Workspace LineEdit
        self.wks_read_le = wdg.QLineEdit(self.current_wks)
        self.wks_read_le.setStyleSheet(self.wks_read_style)
        self.wks_read_le.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.wks_read_le.setFixedHeight(self.wks_height)
        self.wks_read_le.setEnabled(False)

        # Set Project Button
        self.set_project_btn = wdg.QPushButton('Set')
        self.set_project_btn.setFixedWidth(35)
        self.set_project_btn.setFixedHeight(self.wks_height)

        # Sequence Combo Box
        self.sequence_combo = wdg.QComboBox()
        self.sequence_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        # self.sequence_combo.addItems(self.sequences_list)

        # Shot Number Combo Box
        self.shot_number_combo = wdg.QComboBox()
        self.shot_number_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.shot_number_combo.setEnabled(False)

        # Stage Combo Box
        self.stage_combo = wdg.QComboBox()
        self.stage_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.stage_combo.setEnabled(False)

        # Combos List
        self.lvl_combos = [self.sequence_combo, self.shot_number_combo, self.stage_combo]

        # -------------------------------------
        #
        #       Middle Widgets
        #
        # -------------------------------------

        # File Combo Box
        self.file_list = wdg.QListWidget()
        self.file_list.setEnabled(False)

        # -------------------------------------
        #
        #       Right Widgets
        #
        # -------------------------------------

        # Thumbnail Label
        self.thumbnail_label = wdg.QLabel()
        self.thumbnail_label.setFixedSize(275, 275)
        self.thumbnail_label.setStyleSheet("background-color: black;")
        self.thumbnail_label.setAlignment(core.Qt.AlignCenter)
        self.thumbnail_label.setScaledContents(False)

        # -------------------------------------
        #
        #       Metadata Widgets
        #
        # -------------------------------------

        # Metadata Date Label
        self.metadata_date_label = wdg.QLabel('')

        # Metadata Frame Range Label
        self.metadata_frame_range_label = wdg.QLabel('')

        # Metadata Artist Label
        self.metadata_artist_label = wdg.QLabel('')

        # Metadata File Size Label
        self.metadata_size_label = wdg.QLabel('')

        # -------------------------------------
        #
        #       Bottom Widgets
        #
        # -------------------------------------

        # Load Button
        self.load_btn = wdg.QPushButton('LOAD SCENE')
        self.load_btn.setStyleSheet(self.btn_enabled_style)
        self.load_btn.setFixedWidth(270)
        self.load_btn.setFixedHeight(130)

    # -------------------------------------
    #
    #       Create Layout
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
        main_lyt.setAlignment(core.Qt.AlignTop)
        main_lyt.setContentsMargins(40,30,40,0)

        sub_main_lyt = wdg.QHBoxLayout()
        sub_main_lyt.setAlignment(core.Qt.AlignTop)

        sub_main_left_lyt = wdg.QVBoxLayout()
        sub_main_left_lyt.setAlignment(core.Qt.AlignTop)
        sub_main_left_lyt.setContentsMargins(0,0,0,0)

        sub_main_right_lyt = wdg.QVBoxLayout()
        sub_main_right_lyt.setAlignment(core.Qt.AlignTop)
        sub_main_right_lyt.setContentsMargins(20,40,0,0)

        # Thumbnail Layout
        thumbnail_lyt = wdg.QVBoxLayout()
        thumbnail_lyt.setAlignment(core.Qt.AlignTop)

        # -------------------------------------
        #
        #       Main Layout Sections
        #
        # -------------------------------------

        # Title Layout
        title_frame_lyt = wdg.QVBoxLayout()

        title_lyt = wdg.QVBoxLayout(self.title_frame)
        title_lyt.setAlignment(core.Qt.AlignCenter)

        project_frame_lyt = wdg.QVBoxLayout()

        project_lyt = wdg.QVBoxLayout(self.project_frame)
        project_lyt.setAlignment(core.Qt.AlignCenter)

        # Top Layout
        top_lyt = wdg.QVBoxLayout()
        top_lyt.setContentsMargins(0, 20, 0, 0)

        # Upper Layout
        upper_lyt = wdg.QVBoxLayout()

        # Middle Layout
        middle_lyt = wdg.QVBoxLayout()
        middle_lyt.setContentsMargins(0, 0, 0, 20)

        # Bottom Layout
        bottom_lyt = wdg.QVBoxLayout()
        bottom_lyt.setContentsMargins(0, 20, 0, 0)

        # -------------------------------------
        #
        #       Top Layout Sections
        #
        # -------------------------------------

        # Set Project Group Box
        set_project_grp, set_project_lyt = self.group_widget(
            title='Workspace',
            layout=wdg.QHBoxLayout,
            margins=(10,15,10,15),
            alignment=core.Qt.AlignLeft
        )

        # Sequence Layout
        sequence_lyt = wdg.QHBoxLayout()

        # Shot Number Layout
        shot_number_lyt = wdg.QHBoxLayout()

        # Stage Layout
        stage_lyt = wdg.QHBoxLayout()

        # Scene Selection Group Box
        scene_selection_grp, scene_selection_lyt = self.group_widget(
            title='Scene Selection',
            layout=wdg.QFormLayout,
            margins=(10,15,10,15),
            alignment=core.Qt.AlignLeft
        )

        # Scene Selection Group Rows
        scene_selection_lyt.addRow('Sequence     ', sequence_lyt)
        scene_selection_lyt.addRow('Shot Number     ', shot_number_lyt)
        scene_selection_lyt.addRow('Stage     ', stage_lyt)

        # -------------------------------------
        #
        #       Middle Layout Sections
        #
        # -------------------------------------

        # File Selection Layout
        file_lyt = wdg.QHBoxLayout()

        # File Selection Group
        file_selection_grp, file_selection_lyt = self.group_widget(
            title='File Selection',
            layout=wdg.QFormLayout,
            margins=(10,15,10,15),
            height=370
        )

        # File Selection Group Rows
        file_selection_lyt.addRow(file_lyt)

        # -------------------------------------
        #
        #       Bottom Layout Sections
        #
        # -------------------------------------

        # Load Button
        load_lyt = wdg.QHBoxLayout()
        load_lyt.setAlignment(core.Qt.AlignCenter)
        load_lyt.setContentsMargins(0,0,0,0)

        # -------------------------------------
        #
        #       Metadata Group Box
        #
        # -------------------------------------

        # Metadata Layout Rows
        metadata_date_lyt = wdg.QHBoxLayout()
        metadata_frame_range_lyt = wdg.QHBoxLayout()
        metadata_artist_lyt = wdg.QHBoxLayout()
        metadata_size_lyt = wdg.QHBoxLayout()

        # Metadata Group
        metadata_grp, metadata_lyt = self.group_widget(
            title='Metadata',
            layout=wdg.QFormLayout,
            margins=(10,15,10,15)
        )

        # Metadata Group Rows
        metadata_lyt.addRow('Last Saved:   ', metadata_date_lyt)
        metadata_lyt.addRow('Frame Range:   ', metadata_frame_range_lyt)
        metadata_lyt.addRow('Artist:     ', metadata_artist_lyt)
        metadata_lyt.addRow('File Size:     ', metadata_size_lyt)

        # -------------------------------------
        #
        #       Layout Arrangement
        #
        # -------------------------------------

        # Main Layout
        main_lyt.addLayout(title_frame_lyt)
        main_lyt.addLayout(project_frame_lyt)
        main_lyt.addLayout(sub_main_lyt)

        # Sub Main Layout
        sub_main_lyt.addLayout(sub_main_left_lyt)
        sub_main_lyt.addLayout(sub_main_right_lyt)

        # Sub Main Left Layout
        sub_main_left_lyt.addLayout(top_lyt)
        sub_main_left_lyt.addLayout(upper_lyt)
        sub_main_left_lyt.addLayout(middle_lyt)
        sub_main_left_lyt.addStretch(1)

        # Sub Main Right Layout
        sub_main_right_lyt.addLayout(thumbnail_lyt)
        sub_main_right_lyt.addWidget(metadata_grp)
        sub_main_right_lyt.addLayout(bottom_lyt)

        # Upper Layout
        top_lyt.addWidget(set_project_grp)
        upper_lyt.addWidget(scene_selection_grp)

        # Middle Layout
        middle_lyt.addWidget(file_selection_grp)

        # Bottom Layout
        bottom_lyt.addLayout(load_lyt)

        # -------------------------------------
        #
        #       Widgets Arrangement
        #
        # -------------------------------------

        # Title Widgets
        title_frame_lyt.addWidget(self.title_frame)
        title_lyt.addWidget(self.title_label)

        # Project Widgets
        project_frame_lyt.addWidget(self.project_frame)
        project_lyt.addWidget(self.project_label)

        # Set Project Widgets
        set_project_lyt.addWidget(self.wks_read_le)
        set_project_lyt.addWidget(self.set_project_btn)
        sequence_lyt.addWidget(self.sequence_combo)

        # Shot Selection Widgets
        shot_number_lyt.addWidget(self.shot_number_combo)
        stage_lyt.addWidget(self.stage_combo)
        file_lyt.addWidget(self.file_list)

        # Thumbnail Widgets
        thumbnail_lyt.addWidget(self.thumbnail_label)

        # Metadata Widgets
        metadata_date_lyt.addWidget(self.metadata_date_label)
        metadata_frame_range_lyt.addWidget(self.metadata_frame_range_label)
        metadata_artist_lyt.addWidget(self.metadata_artist_label)
        metadata_size_lyt.addWidget(self.metadata_size_label)

        # Load Widgets
        load_lyt.addWidget(self.load_btn)

    # -------------------------------------
    #
    #       Create Connections
    #
    # -------------------------------------

    def create_connections(self):

        self.set_project_btn.pressed.connect(self.set_project_btn_pressed)

        self.sequence_combo.currentIndexChanged.connect(self.sequence_combo_changed)
        self.shot_number_combo.currentIndexChanged.connect(self.shot_number_combo_changed)
        self.stage_combo.currentIndexChanged.connect(self.stage_combo_changed)
        self.file_list.currentRowChanged.connect(self.file_list_changed)

        self.load_btn.clicked.connect(self.load_btn_clicked)

    # -------------------------------------
    #
    #       Set Defaults
    #
    # -------------------------------------

    def set_defaults(self):

        tos_root = mbr_util_get_tos_root() + '/Production/'

        if tos_root == cmds.workspace(q=True, rootDirectory=True):

            # Checks if the assets path is valid or not
            if self.sequences_path:

                self.set_project_btn.setEnabled(False)

                # Enables combo boxes if the assets path is valid
                mbr_helper_set_enabled(self.lvl_combos[:1])
                mbr_helper_set_disabled(self.lvl_combos[1:])

                # # Fills first combo box
                mbr_egn_fill_first_combo(self.sequences_path, self.sequence_combo)

        else:

            self.set_project_btn.setEnabled(True)
            mbr_helper_set_disabled(self.lvl_combos)

    # -------------------------------------
    #
    #       Widget Signals
    #
    # -------------------------------------

    def set_project_btn_pressed(self):

        tos_root = mbr_util_get_tos_root() + '/Production/'

        if tos_root:

            # Block combos signals
            mbr_helper_block_signals(self.lvl_combos)

            # Set project to project path
            cmds.workspace(tos_root, openWorkspace=True)

            # Sets the read button text to current workspace
            self.wks_read_le.setText(tos_root)

            # Sets Sequences Path
            self.sequences_path = f"{tos_root}Sequences"

            # Enables combo boxes if the sequences path is valid
            mbr_helper_set_enabled(self.lvl_combos[:1])
            mbr_helper_set_disabled(self.lvl_combos[1:])

            # Fills first combo box
            mbr_egn_fill_first_combo(self.sequences_path, self.sequence_combo)

            # Disables Set Project Button
            self.set_project_btn.setEnabled(False)

            # Unlock combos signals
            mbr_helper_unlock_signals(self.lvl_combos)

        else:
            return

    def sequence_combo_changed(self):

        # Function Variables
        self.sequence_text = self.sequence_combo.currentText()
        self.sequence_dir = f"{self.wks_read_le.text()}Sequences/{self.sequence_text}"
        self.shot_number_text = self.stage_text = None

        mbr_egn_combo_changed(self.lvl_combos, self.sequence_text, self.sequence_dir, 1, self.file_list)

    def shot_number_combo_changed(self):

        # Function Variables
        self.shot_number_text = self.shot_number_combo.currentText()
        self.shot_number_dir = f"{self.sequence_dir}/{self.shot_number_text}"
        self.stage_text = None

        mbr_egn_combo_changed(self.lvl_combos, self.shot_number_text, self.shot_number_dir, 2, self.file_list)

    def stage_combo_changed(self):

        # Function Variables
        self.stage_text = self.stage_combo.currentText()
        self.stage_dir = f"{self.shot_number_dir}/{self.stage_text}"

        mbr_egn_combo_changed(self.lvl_combos, self.stage_text, self.stage_dir, 3, self.file_list)

    def file_list_changed(self):

        if not self.file_list.currentItem():
            return

        # Initial Variables
        self.current_file = self.file_list.currentItem().text()

    def load_btn_clicked(self):

        # Initial Variables
        self.current_file = self.file_list.currentItem().text()

        # Sets the path that the Load button is pointing depending on if the stage checkbox is checked
        file_path = f"{self.stage_dir}/{self.current_file}"

        # Variables to check if the file is modified or if it already has a path
        is_modified = cmds.file(q=True, modified=True)
        scene_name = cmds.file(q=True, sceneName=True)

        # Raises message box when the current scene is not saved
        if is_modified:
            # Message box setup
            is_modified_msg = wdg.QMessageBox()
            is_modified_msg.setWindowTitle('Warning')
            is_modified_msg.setText('Your scene is not saved. Do you want to save your file?')
            is_modified_msg.setIcon(wdg.QMessageBox.Question)

            # Message box buttons
            is_modified_accept_btn = is_modified_msg.addButton('Yes', wdg.QMessageBox.AcceptRole)
            is_modified_decline_btn = is_modified_msg.addButton('No', wdg.QMessageBox.RejectRole)

            # Message box execution and clicked variable
            is_modified_msg.exec()
            is_modified_clicked = is_modified_msg.clickedButton()

            # Save scene logic when user selects 'Yes'
            if is_modified_clicked == is_modified_accept_btn:
                if not scene_name:
                    # File Dialog asking user where does he want the file to be saved
                    path, selected_filter = wdg.QFileDialog.getSaveFileName(
                        parent=None,
                        caption='Save Maya File',
                        filter='Maya ASCII (*.ma);;Maya Binary (*.mb)')

                    # Variables to get the base name of the new saved file
                    path_base_name = os.path.basename(path)[:-3]

                    naming_layout_sample = 'T400_000_Layout_v001_00'
                    naming_layout_length = len(naming_layout_sample)

                    # If the saved file is on the sequences path, save file and create a thumbnail
                    # If new file doesn't follow the naming conventions, the tool doesn't allow to save
                    if self.sequences_path in path:
                        if 'layout' in path:
                            if len(path_base_name) == naming_layout_length:
                                # Delete unknown nodes
                                # delete_unknown_nodes()

                                # Saves file
                                cmds.file(rename=path)
                                cmds.file(save=True, force=True, type='mayaAscii')

                                # Message Box confirming the scene is saved
                                untitled_scene_confirm_msg = wdg.QMessageBox()
                                untitled_scene_confirm_msg.information(
                                    None,
                                    'Scene Saved',
                                    f"Scene successfully saved on {path}"
                                )

                                # Creates thumbnail
                                # create_thumbnail()
                            else:
                                save_layout_error_msg = wdg.QMessageBox()
                                save_layout_error_msg.critical(
                                    None,
                                    'Naming Convention Error',
                                    'File should follow these naming conventions:\nT000_000_Layout_v001_00')
                                return

                    # Renames to file dialog path and saves the file
                    cmds.file(rename=path)
                    cmds.file(save=True, force=True, type='mayaAscii')

                    # Message Box confirming the scene is saved
                    untitled_scene_confirm_msg = wdg.QMessageBox()
                    untitled_scene_confirm_msg.information(
                        None,
                        'Scene Saved',
                        f"Scene successfully saved on {path}"
                    )

                    mbr_util_open_file(file_path)
                else:

                    # Saves current file
                    cmds.file(save=True, force=True, type='mayaAscii')

                    # Message box confirming the scene is saved
                    modified_scene_confirm_msg = wdg.QMessageBox()
                    modified_scene_confirm_msg.information(
                        None,
                        'Scene Saved',
                        f"Scene successfully saved on {scene_name}"
                    )

                    # Creates thumbnail and opens the file
                    mbr_util_open_file(file_path)

            # Open file when user selects 'No'
            elif is_modified_clicked == is_modified_decline_btn:
                mbr_util_open_file(file_path)

        # Opens file normally when the current scene is already saved
        else:
            mbr_util_open_file(file_path)

# -------------------------------------
#
#       Run Function
#
# -------------------------------------

def run():

    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = tos_scene_manager_window(parent=mbr_util_get_maya_window())
    MAIN_WINDOW.show()