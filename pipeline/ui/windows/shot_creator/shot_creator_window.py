from TOS_Pipeline.pipeline.dcc.maya.qt_compat import wdg, core, gui
from TOS_Pipeline.pipeline.dcc.maya.qt_utils import mbr_util_get_maya_window

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
        #       Variable Helpers
        #
        # -------------------------------------

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
        self.wks_read_btn = wdg.QLineEdit()
        self.wks_read_btn.setStyleSheet(self.workspace_read_style)
        self.wks_read_btn.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.wks_read_btn.setFixedHeight(self.wks_height)
        self.wks_read_btn.setEnabled(False)

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
        # for item in self.sequences_list:
        #     self.sequence_combo.addItem(item[0], item[1])
        # self.sequence_combo.insertItem(0, '-')
        # self.sequence_combo.setCurrentIndex(0)

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
        set_project_lyt.addWidget(self.wks_read_btn)
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

def shot_creator_run():

    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = tos_shot_creator_window(parent=mbr_util_get_maya_window())
    MAIN_WINDOW.show()