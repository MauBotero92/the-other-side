# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_compat import wdg, core, gui
from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_utils import mbr_util_get_maya_window
from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_helpers import *

from TOS_Pipeline.pipeline.dcc.maya.engine.procedures.shot_creator.shot_creator_engine import *
from TOS_Pipeline.pipeline.dcc.maya.engine.utils.maya_utils import *

from TOS_Pipeline.pipeline.core.fs_utils import *
from TOS_Pipeline.pipeline.core.naming import *

import maya.cmds as cmds
import os

# -------------------------------------

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

class tos_shot_creator_window(wdg.QMainWindow):

    def __init__(self, parent=None):
        super(tos_shot_creator_window, self).__init__(parent)

        # -------------------------------------
        #
        #       Window Title and Size
        #
        # -------------------------------------

        self.setWindowTitle(f"TOS Shot Creator {__VERSION__}")
        self.setFocusPolicy(core.Qt.ClickFocus)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = 600 # 720

        self.resize(460, initial_height)
        self.setMinimumSize(460, min(initial_height, int(screen_height * 0.5)))

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

        self.wks_read_le = None
        self.set_project_btn = None
        self.new_shot_check = None

        self.from_current_radial_btn = None
        self.from_file_radial_btn = None
        self.from_published_radial_btn = None

        self.sequence_combo = None
        self.shot_number_combo = None
        self.shot_number_le = None
        self.stage_combo = None

        self.file_le = None
        self.from_file_le = None
        self.from_file_browse_btn = None

        self.create_shot_btn = None

        self.published_scene_grp = None
        self.from_file_grp = None

        # -------------------------------------
        #
        #       Variable Helpers
        #
        # -------------------------------------

        self.project_path = mbr_util_get_tos_path()

        if self.project_path:
            self.sequences_path = f"{self.project_path}Sequences"
        else:
            self.sequences_path = None

        if self.sequences_path:
            self.current_wks = cmds.workspace(q=True, rd=True)
        else:
            self.current_wks = 'Project is not set'

        # Combos first click variables
        self.sequence_first_click = True
        self.shot_number_first_click = True
        self.stage_first_click = True

        self.sequences_list = [
            ['T100', 'Seq1'],
            ['T200', 'Seq2'],
            ['T300', 'Seq3'],
            ['T400', 'Seq4'],
            ['T500', 'Seq5'],
            ['T600', 'Seq6'],
            ['T700', 'Seq7']
        ]

        self.stages_list = [
            ['Layout', 'layout'],
            ['Animation', 'anim'],
            ['Lighting', 'shading']
        ]

        self.cur_sequence = None
        self.cur_shot_number = None
        self.cur_stage = None

        # -------------------------------------
        #
        #       Styles and Widget Variables
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
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #1c0029;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
            """

        self.btn_style_disabled = """
            QPushButton {
                background-color: #3b3b3b;
                color: #737373;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px 10px;

                font-style: italic;
                font-weight: bold;
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #1c0029;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
            """

        self.combo_width = 220
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
        self.title_label = wdg.QLabel('Shot Creator')
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
        self.wks_read_le.setStyleSheet(self.workspace_read_style)
        self.wks_read_le.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.wks_read_le.setFixedHeight(self.wks_height)
        self.wks_read_le.setEnabled(False)

        # Set Project Button
        self.set_project_btn = wdg.QPushButton('Set')
        self.set_project_btn.setFixedWidth(35)
        self.set_project_btn.setFixedHeight(self.wks_height)

        # New Shot Checkbox
        self.new_shot_check = wdg.QCheckBox('New Shot?')
        self.new_shot_check.setChecked(False)

        # From Current Scene Radial Button
        self.from_current_radial_btn = wdg.QRadioButton('From Current')
        self.from_current_radial_btn.setChecked(True)

        # From File Radial Button
        self.from_file_radial_btn = wdg.QRadioButton('From File')

        # From Published Scene
        self.from_published_radial_btn = wdg.QRadioButton('From Published')

        # Sequence Combo Box
        self.sequence_combo = wdg.QComboBox()
        self.sequence_combo.setFixedWidth(self.combo_width)
        for item in self.sequences_list:
            self.sequence_combo.addItem(item[0], item[1])
        self.sequence_combo.insertItem(0, '-')
        self.sequence_combo.setCurrentIndex(0)

        # Shot Number Combo Box
        self.shot_number_combo = wdg.QComboBox()
        self.shot_number_combo.setFixedWidth(self.combo_width)
        self.shot_number_combo.setEnabled(False)

        # Shot Number LineEdit
        self.shot_number_le = wdg.QLineEdit()
        self.shot_number_le.setFixedWidth(self.combo_width)

        # Stage Combo Box
        self.stage_combo = wdg.QComboBox()
        self.stage_combo.setFixedWidth(self.combo_width)
        self.stage_combo.setEnabled(False)

        # -------------------------------------
        #
        #       Middle Widgets
        #
        # -------------------------------------

        # File Combo Box
        self.file_le = wdg.QLineEdit()
        self.file_le.setStyleSheet(self.workspace_read_style)
        self.file_le.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.file_le.setFixedHeight(self.wks_height)
        self.file_le.setEnabled(False)

        # From File Line Edit
        self.from_file_le = wdg.QLineEdit()
        self.from_file_le.setStyleSheet(self.workspace_read_style)
        self.from_file_le.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.from_file_le.setFixedHeight(self.wks_height)
        self.from_file_le.setEnabled(False)

        # From File Browse Button
        self.from_file_browse_btn = wdg.QPushButton('...')
        self.from_file_browse_btn.setFixedWidth(35)
        self.from_file_browse_btn.setFixedHeight(self.wks_height)

        # -------------------------------------
        #
        #       Bottom Widgets
        #
        # -------------------------------------

        # Load Button
        self.create_shot_btn = wdg.QPushButton('CREATE\nSHOT')
        self.create_shot_btn.setStyleSheet(self.btn_style)
        self.create_shot_btn.setFixedWidth(180)
        self.create_shot_btn.setFixedHeight(100)

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

        # -------------------------------------
        #
        #       Main Layout Sections
        #
        # -------------------------------------

        title_frame_lyt = wdg.QVBoxLayout()

        title_lyt = wdg.QVBoxLayout(self.title_frame)
        title_lyt.setAlignment(core.Qt.AlignCenter)

        project_frame_lyt = wdg.QVBoxLayout()

        project_lyt = wdg.QVBoxLayout(self.project_frame)
        project_lyt.setAlignment(core.Qt.AlignCenter)

        # Upper Layout
        upper_lyt = wdg.QVBoxLayout()
        upper_lyt.setContentsMargins(0, 20, 0, 0)

        # Middle Layout
        middle_lyt = wdg.QVBoxLayout()
        middle_lyt.setContentsMargins(0, 0, 0, 20)

        # Bottom Layout
        bottom_lyt = wdg.QVBoxLayout()

        # -------------------------------------
        #
        #       Upper Layout Sections
        #
        # -------------------------------------

        # Set Project Group Box
        set_project_grp = wdg.QGroupBox('Workspace')
        set_project_lyt = wdg.QHBoxLayout()
        set_project_lyt.setContentsMargins(10, 15, 10, 15)
        set_project_lyt.setAlignment(core.Qt.AlignLeft)
        set_project_grp.setLayout(set_project_lyt)

        set_project_grp.setStyleSheet(self.group_boxes_style)

        # Create Options
        create_options_lyt = wdg.QHBoxLayout()
        create_options_lyt.setAlignment(core.Qt.AlignLeft)
        create_options_lyt.setContentsMargins(0, 5, 0, 5)

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

        # File Layout
        file_lyt = wdg.QHBoxLayout()

        # File Selection Group
        self.published_scene_grp = wdg.QGroupBox('Published Scene')
        published_scene_lyt = wdg.QFormLayout()
        published_scene_lyt.setContentsMargins(10,15,10,15)
        self.published_scene_grp.setLayout(published_scene_lyt)

        self.published_scene_grp.setStyleSheet(self.group_boxes_style)

        # File Selection Group Rows
        published_scene_lyt.addRow(file_lyt)


        # From File Layout
        from_file_lyt = wdg.QHBoxLayout()

        # From File Group
        self.from_file_grp = wdg.QGroupBox('From File Selection')
        from_file_selection_lyt = wdg.QFormLayout()
        from_file_selection_lyt.setContentsMargins(10,15,10,15)
        self.from_file_grp.setLayout(from_file_selection_lyt)

        self.from_file_grp.setStyleSheet(self.group_boxes_style)

        # From File Group Roes
        from_file_selection_lyt.addRow(from_file_lyt)

        # -------------------------------------
        #
        #       Lower Layout Sections
        #
        # -------------------------------------

        # Create Shot Button
        create_shot_lyt = wdg.QHBoxLayout()
        create_shot_lyt.setAlignment(core.Qt.AlignCenter)


        # -------------------------------------
        #
        #       Layout Arrangement
        #
        # -------------------------------------

        # Main Layout
        main_lyt.addLayout(title_frame_lyt)
        main_lyt.addLayout(project_frame_lyt)
        main_lyt.addLayout(upper_lyt)
        main_lyt.addLayout(middle_lyt)
        main_lyt.addLayout(bottom_lyt)

        # Upper Layout
        upper_lyt.addWidget(set_project_grp)
        upper_lyt.addLayout(create_options_lyt)
        upper_lyt.addWidget(scene_selection_grp)

        # Middle Layout
        middle_lyt.addWidget(self.published_scene_grp)
        middle_lyt.addWidget(self.from_file_grp)

        # Bottom Layout
        bottom_lyt.addLayout(create_shot_lyt)

        # -------------------------------------
        #
        #       Widgets Arrangement
        #
        # -------------------------------------

        # Title Widgets
        title_frame_lyt.addWidget(self.title_frame)
        title_lyt.addWidget(self.title_label)
        project_frame_lyt.addWidget(self.project_frame)
        project_lyt.addWidget(self.project_label)

        # Set Project Widgets
        set_project_lyt.addWidget(self.wks_read_le)
        set_project_lyt.addWidget(self.set_project_btn)

        # Create Options Widgets
        create_options_lyt.addWidget(self.new_shot_check)
        create_options_lyt.addWidget(self.from_current_radial_btn)
        create_options_lyt.addWidget(self.from_file_radial_btn)
        create_options_lyt.addWidget(self.from_published_radial_btn)

        # Sequence Widgets
        sequence_lyt.addWidget(self.sequence_combo)

        # Shot Number Widgets
        shot_number_lyt.addWidget(self.shot_number_combo)
        shot_number_lyt.addWidget(self.shot_number_le)

        # Stage Widgets
        stage_lyt.addWidget(self.stage_combo)

        # File Widgets
        file_lyt.addWidget(self.file_le)

        # From File Layout
        from_file_lyt.addWidget(self.from_file_le)
        from_file_lyt.addWidget(self.from_file_browse_btn)

        # Create Shot Widgets
        create_shot_lyt.addWidget(self.create_shot_btn)

    # -------------------------------------
    #
    #       Create Connections
    #
    # -------------------------------------

    def create_connections(self):

        self.set_project_btn.clicked.connect(self.set_project_btn_clicked)

        self.new_shot_check.toggled.connect(self.new_shot_check_toggled)
        self.from_current_radial_btn.clicked.connect(self.from_current_radial_btn_clicked)
        self.from_file_radial_btn.clicked.connect(self.from_file_radial_btn_clicked)
        self.from_file_browse_btn.clicked.connect(self.from_file_browse_btn_clicked)
        self.from_published_radial_btn.clicked.connect(self.from_published_radial_btn_clicked)

        self.sequence_combo.currentIndexChanged.connect(self.sequence_combo_changed)
        self.shot_number_combo.currentIndexChanged.connect(self.shot_number_combo_changed)
        self.shot_number_le.editingFinished.connect(self.shot_number_le_edited)
        self.stage_combo.currentIndexChanged.connect(self.stage_combo_changed)

        self.create_shot_btn.clicked.connect(self.create_shot_btn_clicked)

    # -------------------------------------
    #
    #       Set Defaults
    #
    # -------------------------------------

    def set_defaults(self):

        if not self.sequences_path:

            self.sequence_combo.setEnabled(False)
            self.shot_number_combo.setEnabled(False)
            self.stage_combo.setEnabled(False)
            self.file_le.setEnabled(False)

        self.published_scene_grp.setVisible(False)
        self.from_file_grp.setVisible(False)

        if self.sequences_path:
            self.set_project_btn.setEnabled(False)
        else:
            self.set_project_btn.setEnabled(True)

        self.shot_number_combo.setVisible(True)
        self.shot_number_le.setVisible(False)

        self.shot_number_le.setEnabled(False)

        self.create_shot_btn.setEnabled(False)
        self.create_shot_btn.setStyleSheet(self.btn_style_disabled)

    # -------------------------------------
    #
    #       Widget Signals
    #
    # -------------------------------------

    def set_project_btn_clicked(self):

        # Block combos signals
        mbr_helper_block_signals([self.sequence_combo, self.shot_number_combo, self.stage_combo])

        tos_root = mbr_util_get_tos_root()
        project_path = f"{tos_root}/Production"

        cmds.workspace(project_path, openWorkspace=True)

        # Sets the read button text to current workspace
        self.wks_read_le.setText(project_path)

        # Set Project Button clean up
        self.set_project_btn.setDown(False)
        self.set_project_btn.clearFocus()

        # Sequences Path
        self.sequences_path = f"{project_path}/Sequences"

        self.sequence_combo.setEnabled(True)
        self.sequence_combo.clear()

        for item in self.sequences_list:
            self.sequence_combo.addItem(item[0], item[1])
        self.sequence_combo.insertItem(0, '-')
        self.sequence_combo.setCurrentIndex(0)

        # Disables Set Project Button
        self.set_project_btn.setEnabled(False)

        mbr_helper_unlock_signals([self.sequence_combo, self.shot_number_combo, self.stage_combo])

    def new_shot_check_toggled(self, checked):

        if checked:
            self.shot_number_le.clear()
            self.shot_number_combo.setVisible(False)
            self.shot_number_le.setVisible(True)
        else:
            self.shot_number_combo.setCurrentIndex(0)
            self.shot_number_combo.setVisible(True)
            self.shot_number_le.setVisible(False)

        self.create_shot_btn.setEnabled(False)
        self.create_shot_btn.setStyleSheet(self.btn_style_disabled)

    def from_current_radial_btn_clicked(self):

        self.published_scene_grp.setVisible(False)
        self.from_file_grp.setVisible(False)
        self.new_shot_check.setEnabled(True)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = 600

        self.setMinimumSize(460, min(initial_height, int(screen_height * 0.5)))
        self.resize(460, initial_height)

    def from_file_radial_btn_clicked(self):

        if self.from_file_le.text() == '':
            self.create_shot_btn.setEnabled(False)
            self.create_shot_btn.setStyleSheet(self.btn_style_disabled)

        self.from_file_grp.setVisible(True)
        self.published_scene_grp.setVisible(False)
        self.new_shot_check.setEnabled(True)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = 680

        self.setMinimumSize(460, min(initial_height, int(screen_height * 0.5)))
        self.resize(460, initial_height)

    def from_file_browse_btn_clicked(self):

        dialog = wdg.QFileDialog(parent=None, caption='Select File')
        dialog.setNameFilters(['Maya ASCII (*.ma)', 'Maya Binary (*.mb)'])
        dialog.setAcceptMode(wdg.QFileDialog.AcceptSave)
        dialog.setLabelText(wdg.QFileDialog.Accept, 'Select File')
        dialog.setOption(wdg.QFileDialog.DontConfirmOverwrite, True)

        if dialog.exec_():
            self.path = dialog.selectedFiles()[0]
            self.from_file_le.setText(self.path)

        self.create_shot_btn.setEnabled(True)
        self.create_shot_btn.setStyleSheet(self.btn_style)

    def from_published_radial_btn_clicked(self):

        self.published_scene_grp.setVisible(True)
        self.from_file_grp.setVisible(False)
        self.new_shot_check.setChecked(False)
        self.new_shot_check.setEnabled(False)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = 680

        self.setMinimumSize(460, min(initial_height, int(screen_height * 0.5)))
        self.resize(460, initial_height)

    def sequence_combo_changed(self):

        # Initial variables and state
        self.current_sequence = self.sequence_combo.currentData()
        self.shot_number_combo.setEnabled(True)
        self.shot_number_le.setEnabled(True)

        # Blocks signals to prevent unwanted behavior in the other combo boxes
        mbr_helper_block_signals([self.shot_number_combo, self.stage_combo])

        # Adding the shot number folders into the shot combo box
        shot_number_folder_path_list = [
            self.sequences_path, '/',
            self.current_sequence
        ]

        shot_number_folder_path = ''.join(shot_number_folder_path_list)
        self.shot_number_list_initial = mbr_util_list_directory_contents(shot_number_folder_path, content_type='folders')

        self.shot_number_list_sorted = sorted(self.shot_number_list_initial, key=mbr_util_natural_key)
        self.shot_number_list_sorted_trimmed = []
        for item in self.shot_number_list_sorted:
            self.shot_number_list_sorted_trimmed.append(item[-3:])

        self.shot_number_list = ['-'] + self.shot_number_list_sorted_trimmed

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
        self.current_stage = self.stage_combo.currentData()

        if self.stage_combo.count() == 0:
            # Block signals
            mbr_helper_block_signals([self.stage_combo])

            # Combo Boxes clean up
            self.stage_combo.setEnabled(True)
            self.stage_combo.clear()

            for item in self.stages_list:
                self.stage_combo.addItem(item[0], item[1])

            # Unlock signals
            mbr_helper_unlock_signals([self.stage_combo])

        self.create_shot_btn.setEnabled(True)
        self.create_shot_btn.setStyleSheet(self.btn_style)

        if self.from_published_radial_btn.isChecked():
            # Sequence Variables
            self.current_sequence_txt = self.sequence_combo.currentText()
            self.current_sequence = self.sequence_combo.currentData()

            # Shot Number Variables
            if self.new_shot_check.isChecked():
                self.current_shot_number = f"{self.current_sequence_txt.lower()}_{self.shot_number_le.text()}"
                self.current_shot_number_txt = self.shot_number_le.text()
            elif not self.new_shot_check.isChecked():
                self.current_shot_number = f"{self.current_sequence_txt.lower()}_{self.shot_number_combo.currentText()}"
                self.current_shot_number_txt = self.shot_number_combo.currentText()

            # Stage Variables
            self.current_stage_txt = self.stage_combo.currentText()
            self.current_stage = self.stage_combo.currentData()

            shot_number_path = f"{self.sequences_path}/{self.current_sequence}/{self.current_shot_number}"
            shot_number_files = mbr_util_list_directory_contents(shot_number_path, content_type='files')
            published_shot = f"{self.current_sequence_txt}_{self.current_shot_number_txt}.ma"
            self.published_shot_path = f"{shot_number_path}/{published_shot}"

            if published_shot in shot_number_files:
                published_shot = f"{self.current_sequence_txt}_{self.current_shot_number_txt}.ma"
                self.published_shot_path = f"{shot_number_path}/{published_shot}"

                self.file_le.setStyleSheet("background-color: #026700")
                self.file_le.setText(published_shot)
            else:
                self.file_le.setStyleSheet("background-color: #a70000")
                self.file_le.setText('No Published File Detected')

    def shot_number_le_edited(self):

        if not self.stage_combo.isEnabled():
            self.stage_combo.setEnabled(True)
            for item in self.stages_list:
                self.stage_combo.addItem(item[0], item[1])


        self.create_shot_btn.setEnabled(True)
        self.create_shot_btn.setStyleSheet(self.btn_style)

    def stage_combo_changed(self):

        # Initial variables
        self.current_stage = self.stage_combo.currentData()

    def create_shot_btn_clicked(self):

        # Sequence Variables
        self.current_sequence_txt = self.sequence_combo.currentText()
        self.current_sequence = self.sequence_combo.currentData()

        # Shot Number Variables
        if self.new_shot_check.isChecked():
            self.current_shot_number = f"{self.current_sequence_txt.lower()}_{self.shot_number_le.text()}"
            self.current_shot_number_txt = self.shot_number_le.text()
        elif not self.new_shot_check.isChecked():
            self.current_shot_number = f"{self.current_sequence_txt.lower()}_{self.shot_number_combo.currentText()}"
            self.current_shot_number_txt = self.shot_number_combo.currentText()

        # Stage Variables
        self.current_stage_txt = self.stage_combo.currentText()
        self.current_stage = self.stage_combo.currentData()

        # Path and Version Variables if New Shot
        if not self.new_shot_check.isChecked():
            if not self.from_published_radial_btn.isChecked():
                shot_path = f"{self.sequences_path}/{self.current_sequence}/{self.current_shot_number}"
                save_path = f"{shot_path}/{self.current_stage}"
                save_path_files = sorted(mbr_util_list_directory_contents(save_path, content_type='files'), key=mbr_util_natural_key)
                if len(save_path_files) > 0:
                    last_version = save_path_files[-1][-9:-6]
                    last_version_first_str = last_version[0]
                    last_version_second_str = last_version[1]
                    last_version_third_str = last_version[2]

                    # Versions up logic
                    if last_version_third_str != '9':
                        last_version_third_int = int(last_version_third_str)
                        last_version_third_int += 1
                        last_version_new = f"{last_version_first_str}{last_version_second_str}{str(last_version_third_int)}"

                    elif last_version_third_str == '9' and last_version_second_str != '9':
                        last_version_second_int = int(last_version_second_str)
                        last_version_second_int += 1
                        last_version_new = f"{last_version_first_str}{str(last_version_second_int)}0"

                    elif last_version_third_str == '9' and last_version_second_str == '9':
                        last_version_first_int = int(last_version_first_str)
                        last_version_first_int += 1
                        last_version_new = f"{str(last_version_first_int)}00"

                    new_version = last_version_new
                else:
                    new_version = '001'

        # Path and Version Variables if Old Shot
        else:
            shot_path = f"{self.sequences_path}/{self.current_sequence}/{self.current_shot_number}"
            save_path = f"{shot_path}/{self.current_stage}"
            new_version = '001'

        # File Variable
        if not self.from_published_radial_btn.isChecked():
            file_name = f"{self.current_sequence_txt}_{self.current_shot_number_txt}_{self.current_stage_txt}_v{new_version}_00.ma"

        # From Current Scene
        if self.from_current_radial_btn.isChecked():
            # If New Shot
            if self.new_shot_check.isChecked():
                # Guard check if the shot already exists
                if os.path.exists(shot_path):
                    from_current_warning_msg = wdg.QMessageBox()
                    from_current_warning_msg.critical(
                        None,
                        'Error',
                        'Shot already exists',
                        )
                    return

                # Create folder structure
                os.mkdir(shot_path)
                os.mkdir(f"{shot_path}/anim")
                os.mkdir(f"{shot_path}/fx")
                os.mkdir(f"{shot_path}/layout")
                os.mkdir(f"{shot_path}/shading")
                os.mkdir(f"{shot_path}/transfer")

                # Rename current file
                cmds.file(rename=f"{save_path}/{file_name}")

                # Save current file
                cmds.file(save=True, force=True, type='mayaAscii')

                # Confirm Message
                from_current_new_shot_msg = wdg.QMessageBox()
                from_current_new_shot_msg.information(
                    None,
                    'Confirm Message',
                    'New Shot created from scene'
                    )

            # If Existing Shot
            elif not self.new_shot_check.isChecked():

                # Rename current file
                cmds.file(rename=f"{save_path}/{file_name}")

                # Save current file
                cmds.file(save=True, force=True, type='mayaAscii')

                # Confirm Message
                from_current_existing_shot_msg = wdg.QMessageBox()
                from_current_existing_shot_msg.information(
                    None,
                    'Confirm Message',
                    'New Version created from scene'
                    )

        elif self.from_file_radial_btn.isChecked():
            # If New Shot
            if self.new_shot_check.isChecked():
                # Guard check if the shot already exists
                if os.path.exists(shot_path):
                    from_current_warning_msg = wdg.QMessageBox()
                    from_current_warning_msg.critical(
                        None,
                        'Error',
                        'Shot already exists',
                        )
                    return

                # Create folder structure
                os.mkdir(shot_path)
                os.mkdir(f"{shot_path}/anim")
                os.mkdir(f"{shot_path}/fx")
                os.mkdir(f"{shot_path}/layout")
                os.mkdir(f"{shot_path}/shading")
                os.mkdir(f"{shot_path}/transfer")

                # Rename current file
                cmds.file(rename=f"{save_path}/{file_name}")

                # Save current file
                cmds.file(save=True, force=True, type='mayaAscii')

                # Confirm Message
                from_file_new_shot_msg = wdg.QMessageBox()
                from_file_new_shot_msg.information(
                    None,
                    'Confirm Message',
                    'New Shot created from file'
                    )

            # If Existing Shot
            elif not self.new_shot_check.isChecked():
                # Rename current file
                mbr_util_open_file(self.from_file_le.text())

                # Rename current file
                cmds.file(rename=f"{save_path}/{file_name}")

                # Save current file
                cmds.file(save=True, force=True, type='mayaAscii')

                # Confirm Message
                from_file_existing_shot_msg = wdg.QMessageBox()
                from_file_existing_shot_msg.information(
                    None,
                    'Confirm Message',
                    'New Version created from file'
                    )

        elif self.from_published_radial_btn.isChecked():
            # Open the published file
            mbr_util_open_file(self.published_shot_path)

            # Renames the published file to the working file
            if self.current_stage == 'anim':
                current_file_anim = f"{self.current_sequence_txt}_{self.current_shot_number_txt}_Animation_v001_00.ma"

                cmds.file(rename=f"{self.sequences_path}/{self.current_sequence}/{self.current_shot_number}/anim/{current_file_anim}")
                cmds.file(save=True)

            if self.current_stage == 'shading':
                current_file_shading = f"{self.current_sequence_txt}_{self.current_shot_number_txt}_Shading_v001_00.ma"

                cmds.file(rename=f"{shot_number_path}/{self.current_stage}/{current_file_shading}")
                cmds.file(save=True)

            # Confirm Message for Published Shot
            published_shot_msg = wdg.QMessageBox()
            published_shot_msg.information(
                None,
                'Confirm Message',
                'Shot Created from Published Scene'
                )

# -------------------------------------
#
#       Run Function
#
# -------------------------------------

def run():

    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = tos_shot_creator_window(parent=mbr_util_get_maya_window())
    MAIN_WINDOW.show()