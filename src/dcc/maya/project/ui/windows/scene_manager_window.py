# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_compat import wdg, core, gui
from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_utils import mbr_util_get_maya_window
from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_helpers import *

from TOS_Pipeline.pipeline.dcc.maya.engine.procedures.scene_manager_engine import *
from TOS_Pipeline.pipeline.dcc.maya.engine.utils.maya_utils import *

from TOS_Pipeline.pipeline.core.fs_utils import *
from TOS_Pipeline.pipeline.core.naming import *

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

class tos_scene_manager_window(wdg.QMainWindow):

    def __init__(self, parent=None):
        super(tos_scene_manager_window, self).__init__(parent)

        # -------------------------------------
        #
        #       Window Title and Size
        #
        # -------------------------------------

        self.setWindowTitle(f"TOS Scene Manager {__VERSION__}")
        self.setFocusPolicy(core.Qt.ClickFocus)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = 820

        self.resize(700, initial_height)
        self.setMinimumSize(700, min(initial_height, int(screen_height * 0.5)))

        # -------------------------------------
        #
        #       Menu Bar
        #
        # -------------------------------------

        menubar = self.menuBar()

        help_menu = menubar.addMenu('Help')

        help_action = gui.QAction('Go to pipeline-help channel in Slack', self)
        help_menu.addAction(help_action)

        # -------------------------------------
        #
        #       Widget Variables
        #
        # -------------------------------------

        self.title_frame = None
        self.title_label = None
        self.project_frame = None
        self.project_label = None

        self.workspace_read_le = None
        self.set_project_btn = None

        self.sequence_combo = None
        self.stage_combo = None
        self.shot_number_combo = None

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
            self.init_sequences_list = ['-']
            self.init_sequences_list.append(mbr_util_list_directory_contents(self.sequences_path, content_type='folders'))
            self.sequences_list = [self.init_sequences_list[0]] + self.init_sequences_list[1]
        else:
            self.sequences_list = []

        # Combos first click variables
        self.sequence_first_click = True
        self.shot_number_first_click = True
        self.stage_first_click = True

        # Current workspace variable
        self.current_wks = cmds.workspace(q=True, rd=True)

        # Init Variables
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
        self.current_file = None

        # -------------------------------------
        #
        #       Styles
        #
        # -------------------------------------

        self.group_boxes_style = """
            QGroupBox {
                background-color: #3b3b3b;
                border: 1px solid #444444;
                border-radius: 6px;
                margin-top: 20px
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 4px 6px;
                background-color: #2a2a2a2a;
                color: #dddddd
            }
            """

        self.title_frame_style = "background-color: #1c0029"
        self.title_label_style = "font-size: 25px; color: #ffffff; font-weight: bold; font-style: italic"
        self.project_frame_style = "background-color: #ffffff"
        self.project_label_style = "font-size: 20px; color: #1c0029; font-weight: bold"
        self.workspace_read_style = "text-align: left; padding-left: 6px;"

        self.btn_style = """
            QPushButton {
                background-color: #5d5d5d;
                color: #dddddd;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px 10px;

                font-style: italic;
                font-weight: bold;
                font-size: 38px;
            }
            QPushButton:hover {
                background-color: #1c0029;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
            """

        self.wks_height = 25

        # -------------------------------------
        #
        #       Initialization
        #
        # -------------------------------------

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.set_defaults()

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
        self.workspace_read_le = wdg.QLineEdit(self.current_wks)
        self.workspace_read_le.setStyleSheet(self.workspace_read_style)
        self.workspace_read_le.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.workspace_read_le.setFixedHeight(self.wks_height)
        self.workspace_read_le.setEnabled(False)

        # Set Project Button
        self.set_project_btn = wdg.QPushButton('Set')
        self.set_project_btn.setFixedWidth(35)
        self.set_project_btn.setFixedHeight(self.wks_height)

        # Sequence Combo Box
        self.sequence_combo = wdg.QComboBox()
        self.sequence_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.sequence_combo.addItems(self.sequences_list)

        # Shot Number Combo Box
        self.shot_number_combo = wdg.QComboBox()
        self.shot_number_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.shot_number_combo.setEnabled(False)

        # Stage Combo Box
        self.stage_combo = wdg.QComboBox()
        self.stage_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.stage_combo.setEnabled(False)

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
        self.load_btn.setStyleSheet(self.btn_style)
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
        set_project_grp = wdg.QGroupBox('Workspace')
        set_project_lyt = wdg.QHBoxLayout()
        set_project_lyt.setContentsMargins(10, 15, 10, 15)
        set_project_lyt.setAlignment(core.Qt.AlignLeft)
        set_project_grp.setLayout(set_project_lyt)

        set_project_grp.setStyleSheet(self.group_boxes_style)

        # Sequence Layout
        sequence_lyt = wdg.QHBoxLayout()

        # Shot Number Layout
        shot_number_lyt = wdg.QHBoxLayout()

        # Stage Layout
        stage_lyt = wdg.QHBoxLayout()

        # Scene Selection Group Box
        scene_selection_grp = wdg.QGroupBox('Scene Selection')
        scene_selection_lyt = wdg.QFormLayout()
        scene_selection_lyt.setLabelAlignment(core.Qt.AlignLeft)
        scene_selection_lyt.setContentsMargins(10, 15, 10, 15)
        scene_selection_grp.setLayout(scene_selection_lyt)

        scene_selection_grp.setStyleSheet(self.group_boxes_style)

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
        file_selection_grp = wdg.QGroupBox('File Selection')
        file_selection_grp.setFixedHeight(370)
        file_selection_lyt = wdg.QFormLayout()
        file_selection_lyt.setContentsMargins(10,15,10,15)
        file_selection_grp.setLayout(file_selection_lyt)

        file_selection_grp.setStyleSheet(self.group_boxes_style)

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
        metadata_grp = wdg.QGroupBox('Metadata')
        metadata_lyt = wdg.QFormLayout()
        metadata_lyt.setContentsMargins(10,15,10,15)
        metadata_grp.setLayout(metadata_lyt)

        metadata_grp.setStyleSheet(self.group_boxes_style)

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
        set_project_lyt.addWidget(self.workspace_read_le)
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

        if self.project_path:
            self.sequence_combo.setEnabled(True)
        else:
            self.sequence_combo.setEnabled(False)

    # -------------------------------------
    #
    #       Widget Signals
    #
    # -------------------------------------

    def set_project_btn_pressed(self):

        # Block combos signals
        mbr_helper_block_signals([self.sequence_combo, self.shot_number_combo, self.stage_combo])

        tos_root = mbr_util_get_tos_root()
        project_path = f"{tos_root}/Production/"

        cmds.workspace(project_path, openWorkspace=True)

        # Sets the read button text to current workspace
        self.workspace_read_le.setText(project_path)

        # Set Project Button clean up
        self.set_project_btn.setDown(False)
        self.set_project_btn.clearFocus()

        # Sequences Path
        self.sequences_path = f"{project_path}/Sequences"

        # Enables the UI and fills up the fields if the workspace is set correctly
        self.sequences_list_initial = mbr_util_list_directory_contents(self.sequences_path, content_type='folders')
        self.sequences_list = ['-'] + self.sequences_list_initial

        self.sequence_combo.setEnabled(True)
        self.sequence_combo.clear()
        self.sequence_combo.addItems(self.sequences_list)

        # Disables Set Project Button
        self.set_project_btn.setEnabled(False)

        # Unlock combos signals
        mbr_helper_unlock_signals([self.sequence_combo, self.shot_number_combo, self.stage_combo])

    def sequence_combo_changed(self):

        # Initial variables and state
        self.current_sequence = self.sequence_combo.currentText()
        self.shot_number_combo.setEnabled(True)

        # Cleans up sequence combo box if trying to use it after the first time
        mbr_egn_clean_initial_idx(self, 'sequence_first_click', self.sequence_combo, self.sequences_list)

        # Blocks signals to prevent unwanted behavior in the other combo boxes
        mbr_helper_block_signals([self.shot_number_combo, self.stage_combo])

        # Combo Boxes clean up
        self.shot_number_combo.setEnabled(True)
        self.shot_number_combo.clear()

        self.stage_combo.setEnabled(False)
        self.stage_combo.clear()

        self.file_list.setEnabled(False)
        self.file_list.clear()

        # Adding the shot number folders into the shot combo box
        shot_number_folder_path_list = [
            self.sequences_path, '/',
            self.current_sequence
        ]

        shot_number_folder_path = ''.join(shot_number_folder_path_list)
        self.shot_number_list_initial = mbr_util_list_directory_contents(shot_number_folder_path, content_type='folders')

        self.shot_number_list_sorted = sorted(self.shot_number_list_initial, key=mbr_util_natural_key)
        self.shot_number_list = ['-'] + self.shot_number_list_sorted

        if self.shot_number_combo.count() == 0:
            self.shot_number_combo.addItems(self.shot_number_list)
        else:
            self.shot_number_combo.clear()
            self.shot_number_combo.addItems(self.shot_number_list)

        # Enables signals to allow normal behavior in the other combo boxes
        mbr_helper_unlock_signals([self.shot_number_combo, self.stage_combo])

    def shot_number_combo_changed(self):

        # Initial variables
        self.current_shot_number = self.shot_number_combo.currentText()
        self.current_stage = self.stage_combo.currentText()

        # Cleans up shot number combo box if trying to use it after the first time
        mbr_egn_clean_initial_idx(self, 'shot_number_first_click', self.shot_number_combo, self.shot_number_list)

        if self.stage_combo.count() == 0:
            # Block signals
            mbr_helper_block_signals([self.stage_combo])

            # Combo Boxes clean up
            self.stage_combo.setEnabled(True)
            self.stage_combo.clear()

            self.file_list.setEnabled(False)
            self.file_list.clear()

            # Adding stages folders into the stages combo box
            stages_folders_path_list = [
                self.sequences_path, '/',
                self.current_sequence, '/',
                self.current_shot_number
                ]

            stages_folders_path = ''.join(stages_folders_path_list)
            self.stages_list_initial = mbr_util_list_directory_contents(stages_folders_path, content_type='folders')

            self.stages_list_filtered = [x for x in self.stages_list_initial if not x.startswith('.')]
            self.stages_list = ['-'] + self.stages_list_filtered

            if self.stage_combo.count() == 0:
                self.stage_combo.addItems(self.stages_list)
            else:
                self.stage_combo.clear()
                self.stage_combo.addItems(self.stages_list)

            # Unlock signals
            mbr_helper_unlock_signals([self.stage_combo])

        else:
            # Block signals
            mbr_helper_block_signals([self.stage_combo])

            # Save current stage selection
            current_stage_text = self.stage_combo.currentText()

            # Clear file combo and leave it as-is
            self.file_list.clear()

            # Guards against '-' stage
            if current_stage_text == '-' or not current_stage_text:
                mbr_helper_unlock_signals([self.stage_combo])
                return

            # Rebuild stage combo for the new shot number
            stage_files_path_list = [
                self.sequences_path, '/',
                self.current_sequence, '/',
                self.current_shot_number, '/',
                self.current_stage
                ]

            stage_files_path = ''.join(stage_files_path_list)
            stage_folder_files = sorted(mbr_util_list_directory_contents(stage_files_path, content_type='files'))

            self.stages_list_filtered = [x for x in self.stages_list_initial if not x.startswith('.')]
            self.stages_list = ['-'] + self.stages_list_filtered

            if len(stage_folder_files) == 0:
                self.file_list.setEnabled(False)
            else:
                self.file_list.setEnabled(True)
                self.file_list.addItems(stage_folder_files)

            # Restore stage selection if it exists in the new shot
            if current_stage_text in self.stages_list:
                self.stage_combo.setCurrentText(current_stage_text)

            self.file_list.setCurrentRow(self.file_list.count() - 1)

            mbr_helper_unlock_signals([self.stage_combo])

    def stage_combo_changed(self):

        # Initial variables
        self.current_stage = self.stage_combo.currentText()

        # Cleans up stage combo box if trying to use it after the first time
        mbr_egn_clean_initial_idx(self, 'stage_first_click', self.stage_combo, self.stages_list)

        # Stage lists
        stage_files_path_list = [
            self.sequences_path, '/',
            self.current_sequence, '/',
            self.current_shot_number, '/',
            self.current_stage
            ]

        stage_files_path = ''.join(stage_files_path_list)
        stage_folder_files = sorted(mbr_util_list_directory_contents(stage_files_path, content_type='files'))

        # Combo Boxes clean up
        if len(stage_folder_files) == 0:
            self.file_list.setEnabled(False)
            self.file_list.clear()
        else:
            self.file_list.setEnabled(True)
            self.file_list.clear()

        # Adding files in the file combo box
        if self.current_stage != '-':
            self.file_list.clear()
            self.file_list.addItems(stage_folder_files)

        self.file_list.setCurrentRow(self.file_list.count() - 1)

    def file_list_changed(self):

        if not self.file_list.currentItem():
            return

        # Initial Variables
        self.current_file = self.file_list.currentItem().text()
        self.get_thumbnail()

        # File path
        file_path_list = [
            self.sequences_path, '/',
            self.current_sequence, '/',
            self.current_shot_number, '/',
            self.current_stage, '/',
            self.current_file
        ]
        file_path = ''.join(file_path_list)

        # Thumbnail path
        thumb_path_list = [
            self.sequences_path, '/',
            self.current_sequence, '/',
            self.current_shot_number, '/',
            self.current_stage, '/',
            '_thumbnail']
        thumb_path = ''.join(thumb_path_list)

        # Date
        last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
        self.metadata_date_label.setText(f"{last_modified.strftime('%Y-%m-%d %H:%M:%S')}")

        # Artist and Time Range
        self.metadata_artist_label.clear()
        self.metadata_framerange_label.clear()

        txt_path = Path(f"{thumb_path}/{self.current_file[:-3]}.txt")

        if txt_path.exists():
            with open(txt_path, 'r') as file:
                content_artist = file.readline().strip()
                content_frame_range = file.readline().strip()
            if content_artist:
                self.metadata_artist_label.setText(content_artist)
            else:
                self.metadata_artist_label.setText('no data')
            if content_frame_range:
                self.metadata_framerange_label.setText(content_frame_range)
            else:
                self.metadata_framerange_label.setText('no data')
        else:
            self.metadata_artist_label.setText('unknown')
            self.metadata_framerange_label.setText('unknown')

        # File Size
        self.metadata_size_label.clear()
        file_size_raw = os.path.getsize(file_path) / (1024 ** 2)
        file_size_round = round(file_size_raw, 2)
        self.metadata_size_label.setText(f"{str(file_size_round)} Mb")


    def load_btn_clicked(self):

        # Initial Variables
        self.current_file = self.file_list.currentItem().text()

        # Sets the path that the Load button is pointing depending on if the stage checkbox is checked
        file_path_list = [
            self.sequences_path, '/',
            self.current_sequence, '/',
            self.current_shot_number, '/',
            self.current_stage, '/',
            self.current_file
        ]
        file_path = ''.join(file_path_list)

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
                                delete_unknown_nodes()

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
                                create_thumbnail()
                            else:
                                save_layout_error_msg = wdg.QMessageBox()
                                save_layout_error_msg.critical(
                                    None,
                                    'Naming Convention Error',
                                    'File should follow these naming conventions:\nT000_000_Layout_v001_00')
                                return

                    # Delete unknown nodes
                    delete_unknown_nodes()

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
                    # Delete unknown nodes
                    delete_unknown_nodes()

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
                    create_thumbnail()
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