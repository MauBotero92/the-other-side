# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_compat import wdg, core, gui
from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_utils import mbr_util_get_maya_window
from TOS_Pipeline.pipeline.core.fs_utils import *

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
            self.init_sequences_list = mbr_util_list_directory_contents(self.sequences_path, content_type='folders')
        else:
            self.init_sequences_list = None

        # Combos first click variables
        self.sequence_first_click = True
        self.shot_number_first_click = True
        self.stage_first_click = True

        # Current workspace variable
        self.current_wks = cmds.workspace(q=True, rd=True)

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
        self.sequence_combo.addItem('-')
        self.sequence_combo.addItems(self.init_sequences_list)

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
        sub_main_lyt.addLayout(sub_main_left_lyt)
        sub_main_lyt.addLayout(sub_main_right_lyt)
        sub_main_left_lyt.addLayout(top_lyt)
        sub_main_left_lyt.addLayout(upper_lyt)
        sub_main_left_lyt.addLayout(middle_lyt)
        sub_main_left_lyt.addStretch(1)
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

        title_frame_lyt.addWidget(self.title_frame)
        title_lyt.addWidget(self.title_label)
        project_frame_lyt.addWidget(self.project_frame)
        project_lyt.addWidget(self.project_label)
        set_project_lyt.addWidget(self.workspace_read_le)
        set_project_lyt.addWidget(self.set_project_btn)
        sequence_lyt.addWidget(self.sequence_combo)
        shot_number_lyt.addWidget(self.shot_number_combo)
        stage_lyt.addWidget(self.stage_combo)
        file_lyt.addWidget(self.file_list)
        thumbnail_lyt.addWidget(self.thumbnail_label)
        metadata_date_lyt.addWidget(self.metadata_date_label)
        metadata_frame_range_lyt.addWidget(self.metadata_frame_range_label)
        metadata_artist_lyt.addWidget(self.metadata_artist_label)
        metadata_size_lyt.addWidget(self.metadata_size_label)
        load_lyt.addWidget(self.load_btn)

    # -------------------------------------
    #
    #       Create Connections
    #
    # -------------------------------------

    def create_connections(self):
        pass

    # -------------------------------------
    #
    #       Set Defaults
    #
    # -------------------------------------

    def set_defaults(self):
        pass

    # -------------------------------------
    #
    #       Widget Signals
    #
    # -------------------------------------

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