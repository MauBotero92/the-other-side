# -------------------------------------------
#
#       Import modules
#
# -------------------------------------------

from TOS_Pipeline.src.dcc.maya.utils.qt_compat import wdg, core, gui
from TOS_Pipeline.src.dcc.maya.utils.qt_utils import mbr_util_get_maya_window

from TOS_Pipeline.src.dcc.maya.layout.engine.sequencer_manager_engine import *

import maya.cmds as cmds
import os

# -------------------------------------
#
#       Global Variables
#
# -------------------------------------

MAIN_WINDOW = None
__VERSION__ = '1.0'


# -------------------------------------
#
#       Sequencer Shot Mng Class
#
# -------------------------------------

class Sequencer_Shot_Manager(wdg.QMainWindow):

    def __init__(self, parent=None):
        super(Sequencer_Shot_Manager, self).__init__(parent)

        # -------------------------------------
        #
        #       Window Title and Size
        #
        # -------------------------------------

        self.setWindowTitle(f"MBR Sequencer Shot Manager {__VERSION__}")
        self.setFocusPolicy(core.Qt.ClickFocus)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = 360

        self.resize(400, initial_height)
        self.setMinimumSize(400, min(initial_height, int(screen_height * 0.5)))
        self.setFixedSize(400, initial_height)

        # -------------------------------------
        #
        #       Menu Bar
        #
        # -------------------------------------

        menubar = self.menuBar()
        menubar.addMenu('Edit')
        menubar.addMenu('Help')

        # -------------------------------------
        #
        #       Widgets Variables
        #
        # -------------------------------------

        # Shot Setup - Setup Widgets
        self.referenced_cams_radio_btn = None
        self.imported_cams_radio_btn = None
        self.create_locs_setup_btn = None
        self.create_camera_handles_btn = None

        # Shot Setup - Shot Creation Widgets
        self.use_loc_handles_radio_btn = None
        self.use_cam_handles_radio_btn = None
        self.use_custom_range_radio_btn = None
        self.range_start_le = None
        self.range_end_le = None
        self.create_sequencer_shot_btn = None

        # Shot List Widgets
        self.playblast_shot_path_le = None
        self.playblast_shot_path_browse_btn = None
        self.playblast_shot_btn = None
        self.playblast_sequence_path_le = None
        self.playblast_sequence_path_browse_btn = None
        self.playblast_sequence_btn = None
        self.frame_selected_shot_btn = None
        self.shots_table = None

        # Tab Widget
        self.tab_wdg = None

        # -------------------------------------
        #
        #       Other Variables
        #
        # -------------------------------------

        self.sequencer_shots_list = mbr_egn_get_sequencer_shots()
        self.cam_transforms_list = mbr_egn_get_bind_cameras()
        self.sequencer_time_ranges_list = mbr_egn_get_all_sequence_shots_timeline_range()

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

        self.btn_style = """
            QPushButton {
                background-color: #5d5d5d;
                color: #dddddd;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px 10px;

                font-style: italic;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: black;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
            """

        self.btn_style_reduced_font = """
            QPushButton {
                background-color: #5d5d5d;
                color: #dddddd;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px 10px;

                font-style: italic;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: black;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
            """

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
    #       Create Widgets
    #
    # -------------------------------------

    def create_widgets(self):

        # -------------------------------------
        #
        #       Shot Setup - Setup Widgets
        #
        # -------------------------------------

        # Referenced Cameras Radio Button
        self.referenced_cams_radio_btn = wdg.QRadioButton('Referenced Cameras')
        self.referenced_cams_radio_btn.setChecked(True)

        # Imported Cameras Radio Button
        self.imported_cams_radio_btn = wdg.QRadioButton('Imported Cameras')

        # Create Locs Setup
        self.create_locs_setup_btn = wdg.QPushButton('Create\nLocator Setup')
        self.create_locs_setup_btn.setStyleSheet(self.btn_style)
        self.create_locs_setup_btn.setFixedHeight(70)
        self.create_locs_setup_btn.setFixedWidth(150)

        # Create Camera Handles
        self.create_camera_handles_btn = wdg.QPushButton('Create\nCamera Handles')
        self.create_camera_handles_btn.setStyleSheet(self.btn_style)
        self.create_camera_handles_btn.setVisible(False)
        self.create_camera_handles_btn.setFixedHeight(70)
        self.create_camera_handles_btn.setFixedWidth(150)

        # -------------------------------------
        #
        #       Shot Setup - SC Widgets
        #
        # -------------------------------------

        # Use Loc Handles Radio Button
        self.use_loc_handles_radio_btn = wdg.QRadioButton('Use Locator Handles')
        self.use_loc_handles_radio_btn.setChecked(True)

        # Use Camera Handles
        self.use_cam_handles_radio_btn = wdg.QRadioButton('Use Camera Handles')

        # Use Custom Range
        self.use_custom_range_radio_btn = wdg.QRadioButton('Use Custom Range')

        # Range Start LineEdit
        self.range_start_le = wdg.QLineEdit()
        self.range_start_le.setText(str(int(cmds.playbackOptions(q=True, minTime=True))))
        self.range_start_le.setFixedWidth(60)
        self.range_start_le.setEnabled(False)

        # Range End LineEdit
        self.range_end_le = wdg.QLineEdit()
        self.range_end_le.setText(str(int(cmds.playbackOptions(q=True, maxTime=True))))
        self.range_end_le.setFixedWidth(60)
        self.range_end_le.setEnabled(False)

        # Create Shot Button
        self.create_sequencer_shot_btn = wdg.QPushButton('Create\nSequencer Shot')
        self.create_sequencer_shot_btn.setStyleSheet(self.btn_style)
        self.create_sequencer_shot_btn.setFixedHeight(70)
        self.create_sequencer_shot_btn.setFixedWidth(150)

        # -------------------------------------
        #
        #       Shot List Widgets
        #
        # -------------------------------------

        # Playblast Shot Path Line Edit
        self.playblast_shot_path_le = wdg.QLineEdit()
        self.playblast_shot_path_le.setFixedWidth(550)

        # Playblast Shot Path Browse Button
        self.playblast_shot_path_browse_btn = wdg.QPushButton('...')
        self.playblast_shot_path_browse_btn.setFixedWidth(30)
        self.playblast_shot_path_browse_btn.setFixedHeight(20)

        # Playblast Shot Button
        self.playblast_shot_btn = wdg.QPushButton('Playblast Selected Shots')
        self.playblast_shot_btn.setStyleSheet(self.btn_style)
        self.playblast_shot_btn.setFixedWidth(250)

        # Playblast Sequence Path Line Edit
        self.playblast_sequence_path_le = wdg.QLineEdit()
        self.playblast_sequence_path_le.setFixedWidth(550)

        # Playblast Sequence Path Browse Button
        self.playblast_sequence_path_browse_btn = wdg.QPushButton('...')
        self.playblast_sequence_path_browse_btn.setFixedWidth(30)
        self.playblast_sequence_path_browse_btn.setFixedHeight(20)

        # Playblast Sequence Button
        self.playblast_sequence_btn = wdg.QPushButton('Playblast Sequence')
        self.playblast_sequence_btn.setStyleSheet(self.btn_style)
        self.playblast_sequence_btn.setFixedWidth(250)

        # Shots Table List
        self.shots_table = wdg.QTableWidget(len(self.sequencer_shots_list), 5)
        self.shots_table.setHorizontalHeaderLabels(['Selected', 'Bind Camera', 'Shot Name', 'Time Range', 'Actions'])

        self.shots_table.setColumnWidth(0, 70)
        self.shots_table.setColumnWidth(1, 150)
        self.shots_table.setColumnWidth(2, 150)
        self.shots_table.setColumnWidth(3, 150)
        self.shots_table.setColumnWidth(4, 250)

        for num in range(len(self.sequencer_shots_list)):
            self.shots_table.setRowHeight(num, 45)

        # Filling up the Bind Camera cell
        self.shot_checkboxes = []
        for num in range(len(self.sequencer_shots_list)):
            # Add Checkboxes to each row
            checkbox = wdg.QCheckBox()
            self.shot_checkboxes.append(checkbox)
            checkbox.setChecked(True)
            checkbox_container = wdg.QWidget()
            checkbox_lyt = wdg.QHBoxLayout(checkbox_container)
            checkbox_lyt.addWidget(checkbox)
            checkbox_lyt.setAlignment(core.Qt.AlignCenter)
            checkbox_lyt.setContentsMargins(0, 0, 0, 0)
            self.shots_table.setCellWidget(num, 0, checkbox_container)

            # Add Camera Transform label to each row
            cam_transform_item = wdg.QTableWidgetItem(self.cam_transforms_list[num])
            cam_transform_item.setTextAlignment(core.Qt.AlignCenter)
            self.shots_table.setItem(num, 1, cam_transform_item)

            # Add Sequencer Shot Name label to each row
            sequencer_shot_item = wdg.QTableWidgetItem(self.sequencer_shots_list[num])
            sequencer_shot_item.setTextAlignment(core.Qt.AlignCenter)
            self.shots_table.setItem(num, 2, sequencer_shot_item)

            # Add Time Range label to each row
            time_range_item = wdg.QTableWidgetItem(
                f"{str(self.sequencer_time_ranges_list[num][0])[:-2]} - {str(self.sequencer_time_ranges_list[num][1])[:-2]}")
            time_range_item.setTextAlignment(core.Qt.AlignCenter)
            self.shots_table.setItem(num, 3, time_range_item)

            frame_btn = wdg.QPushButton('Frame')
            frame_btn.setStyleSheet(self.btn_style)
            frame_btn.clicked.connect(self.frame_row_clicked)

            playblast_btn = wdg.QPushButton('Playblast')
            playblast_btn.setStyleSheet(self.btn_style)
            playblast_btn.clicked.connect(self.playblast_row_clicked)

            # Add Action Buttons to each row
            actions_container = wdg.QWidget()
            actions_lyt = wdg.QHBoxLayout(actions_container)
            actions_lyt.addWidget(frame_btn)
            actions_lyt.addWidget(playblast_btn)
            actions_lyt.setAlignment(core.Qt.AlignCenter)
            actions_lyt.setContentsMargins(0, 0, 0, 0)
            self.shots_table.setCellWidget(num, 4, actions_container)

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

        main_tab_lyt = wdg.QVBoxLayout()

        # -------------------------------------
        #
        #       Tab Widget and Layouts
        #
        # -------------------------------------

        self.tab_wdg = wdg.QTabWidget()

        # Shot Creation Tab
        shot_setup_tab_wdg = wdg.QWidget()
        shot_setup_tab_lyt = wdg.QVBoxLayout(shot_setup_tab_wdg)
        shot_setup_tab_lyt.setAlignment(core.Qt.AlignTop)

        # Shot List Tab
        shot_list_tab_wdg = wdg.QWidget()
        shot_list_tab_lyt = wdg.QVBoxLayout(shot_list_tab_wdg)
        shot_list_tab_lyt.setAlignment(core.Qt.AlignTop)

        # Add Tabs
        self.tab_wdg.addTab(shot_setup_tab_wdg, 'Shot Creation')
        self.tab_wdg.addTab(shot_list_tab_wdg, 'Shot List')

        # -------------------------------------
        #
        #       Shot Setup - Setup GB
        #
        # -------------------------------------

        setup_grp = wdg.QGroupBox('Setup')
        setup_grp.setStyleSheet(self.group_boxes_style)
        setup_grp.setFixedHeight(125)
        setup_lyt = wdg.QHBoxLayout()
        setup_lyt.setContentsMargins(0, 0, 0, 0)
        setup_lyt.setAlignment(core.Qt.AlignTop)
        setup_grp.setLayout(setup_lyt)

        camera_import_type_lyt = wdg.QVBoxLayout()
        camera_import_type_lyt.setContentsMargins(20, 10, 0, 0)
        camera_import_type_lyt.setAlignment(core.Qt.AlignTop)

        create_handles_lyt = wdg.QVBoxLayout()
        create_handles_lyt.setContentsMargins(20, 15, 100, 0)
        create_handles_lyt.setAlignment(core.Qt.AlignLeft)

        # -------------------------------------
        #
        #       Shot Setup - Shot Creation GB
        #
        # -------------------------------------

        shot_creation_grp = wdg.QGroupBox('Sequencer Shot Creation')
        shot_creation_grp.setStyleSheet(self.group_boxes_style)
        shot_creation_grp.setFixedHeight(140)
        shot_creation_lyt = wdg.QHBoxLayout()
        shot_creation_lyt.setContentsMargins(0, 0, 0, 0)
        shot_creation_lyt.setAlignment(core.Qt.AlignTop)
        shot_creation_grp.setLayout(shot_creation_lyt)

        shot_range_options_lyt = wdg.QVBoxLayout()
        shot_range_options_lyt.setContentsMargins(20, 10, 0, 0)
        shot_range_options_lyt.setAlignment(core.Qt.AlignLeft)

        handles_range_lyt = wdg.QVBoxLayout()
        handles_range_lyt.setContentsMargins(0, 0, 0, 0)
        handles_range_lyt.setAlignment(core.Qt.AlignLeft)

        custom_range_lyt = wdg.QHBoxLayout()
        custom_range_lyt.setContentsMargins(0, 0, 0, 0)
        custom_range_lyt.setAlignment(core.Qt.AlignLeft)

        shot_create_btn_lyt = wdg.QVBoxLayout()
        shot_create_btn_lyt.setContentsMargins(20, 0, 100, 0)
        shot_create_btn_lyt.setAlignment(core.Qt.AlignLeft)

        # -------------------------------------
        #
        #       Shot List
        #
        # -------------------------------------

        # Playblast Options GroupBox
        playblast_options_grp = wdg.QGroupBox('Playblast Options')
        playblast_options_grp.setStyleSheet(self.group_boxes_style)
        playblast_options_grp.setFixedHeight(145)
        playblast_options_lyt = wdg.QFormLayout()
        playblast_options_lyt.setContentsMargins(15, 15, 0, 0)
        playblast_options_lyt.setAlignment(core.Qt.AlignTop)
        playblast_options_lyt.setLabelAlignment(core.Qt.AlignLeft)
        playblast_options_grp.setLayout(playblast_options_lyt)

        # Playblast Shot Path Layout
        playblast_shot_path_lyt = wdg.QHBoxLayout()

        # Playblast Sequence Path layout
        playblast_sequence_path_lyt = wdg.QHBoxLayout()

        # Playblast Actions Layout
        playblast_actions_lyt = wdg.QHBoxLayout()

        # Group Rows
        playblast_options_lyt.addRow('Playblast Shot Path     ', playblast_shot_path_lyt)
        playblast_options_lyt.addRow('Playblast Sequence Path     ', playblast_sequence_path_lyt)
        playblast_options_lyt.addRow('Playblast Actions     ', playblast_actions_lyt)

        # Additional Options GroupBox
        additional_options_grp = wdg.QGroupBox('Additional Options')
        additional_options_grp.setStyleSheet(self.group_boxes_style)
        additional_options_grp.setFixedHeight(100)

        # Shot Table Layout
        shot_table_lyt = wdg.QVBoxLayout()
        shot_table_lyt.setContentsMargins(0, 20, 0, 0)

        # -------------------------------------
        #
        #       Layout Arrangement
        #
        # -------------------------------------

        # Main Layout
        main_lyt.addLayout(main_tab_lyt)

        # Main Tab Layout
        main_tab_lyt.addWidget(self.tab_wdg)

        # Shot Setup Tab Layout
        shot_setup_tab_lyt.addWidget(setup_grp)
        shot_setup_tab_lyt.addWidget(shot_creation_grp)

        # Setup Layout
        setup_lyt.addLayout(camera_import_type_lyt)
        setup_lyt.addLayout(create_handles_lyt)

        # Shot Creation Layout
        shot_creation_lyt.addLayout(shot_range_options_lyt)
        shot_creation_lyt.addLayout(shot_create_btn_lyt)

        # Shot Range Options Layout
        shot_range_options_lyt.addLayout(handles_range_lyt)
        shot_range_options_lyt.addLayout(custom_range_lyt)

        # Shot List Tab Layout
        shot_list_tab_lyt.addWidget(playblast_options_grp)
        shot_list_tab_lyt.addLayout(shot_table_lyt)

        # -------------------------------------
        #
        #       Widgets Arrangement
        #
        # -------------------------------------

        # Camera Import Type Layout
        camera_import_type_lyt.addWidget(self.referenced_cams_radio_btn)
        camera_import_type_lyt.addWidget(self.imported_cams_radio_btn)

        # Create Handles Layout
        create_handles_lyt.addWidget(self.create_locs_setup_btn)
        create_handles_lyt.addWidget(self.create_camera_handles_btn)

        # Handles Range Layout
        handles_range_lyt.addWidget(self.use_loc_handles_radio_btn)
        handles_range_lyt.addWidget(self.use_cam_handles_radio_btn)
        handles_range_lyt.addWidget(self.use_custom_range_radio_btn)

        # Custom Range Layout
        custom_range_lyt.addWidget(self.range_start_le)
        custom_range_lyt.addWidget(self.range_end_le)

        # Shot Create Button Layout
        shot_create_btn_lyt.addWidget(self.create_sequencer_shot_btn)

        # Shot List Tab Layout
        # shot_list_tab_lyt.addWidget(self.frame_selected_shot_btn)
        playblast_shot_path_lyt.addWidget(self.playblast_shot_path_le)
        playblast_shot_path_lyt.addWidget(self.playblast_shot_path_browse_btn)
        playblast_sequence_path_lyt.addWidget(self.playblast_sequence_path_le)
        playblast_sequence_path_lyt.addWidget(self.playblast_sequence_path_browse_btn)
        playblast_actions_lyt.addWidget(self.playblast_shot_btn)
        playblast_actions_lyt.addWidget(self.playblast_sequence_btn)

        # Shot Table Layout
        shot_table_lyt.addWidget(self.shots_table)

    # -------------------------------------
    #
    #       Create Connections
    #
    # -------------------------------------

    def create_connections(self):

        self.tab_wdg.currentChanged.connect(self.tab_wdg_changed)

        self.referenced_cams_radio_btn.clicked.connect(self.referenced_cams_radio_btn_clicked)
        self.imported_cams_radio_btn.clicked.connect(self.imported_cams_radio_btn_clicked)
        self.create_locs_setup_btn.clicked.connect(self.create_locs_setup_btn_clicked)
        self.create_camera_handles_btn.clicked.connect(self.create_camera_handles_btn_clicked)

        self.use_loc_handles_radio_btn.clicked.connect(self.use_loc_handles_radio_btn_clicked)
        self.use_cam_handles_radio_btn.clicked.connect(self.use_cam_handles_radio_btn_clicked)
        self.use_custom_range_radio_btn.clicked.connect(self.use_custom_range_radio_btn_clicked)
        self.create_sequencer_shot_btn.clicked.connect(self.create_sequencer_shot_btn_clicked)

        self.playblast_shot_path_browse_btn.clicked.connect(self.playblast_shot_path_browse_btn_clicked)
        self.playblast_sequence_path_browse_btn.clicked.connect(self.playblast_sequence_path_browse_btn_clicked)
        self.playblast_shot_btn.clicked.connect(self.playblast_shot_btn_clicked)
        self.playblast_sequence_btn.clicked.connect(self.playblast_sequence_btn_clicked)

        # self.frame_selected_shot_btn.clicked.connect(self.frame_selected_shot_btn_clicked)

    # -------------------------------------
    #
    #       Set Defaults
    #
    # -------------------------------------

    def set_defaults(self):

        playblast_default_path = 'S:/JORDAN/reference/artist'
        self.playblast_shot_path_le.setText(playblast_default_path)
        self.playblast_sequence_path_le.setText(playblast_default_path)

    # -------------------------------------
    #
    #       Signals
    #
    # -------------------------------------

    def tab_wdg_changed(self, index):

        if index == 0:
            screen = wdg.QApplication.primaryScreen()
            screen_height = screen.availableGeometry().height()

            if screen_height < 720:
                initial_height = int(screen_height * 0.85)
            else:
                initial_height = 360

            self.resize(400, initial_height)
            self.setMinimumSize(400, min(initial_height, int(screen_height * 0.5)))
            self.setFixedSize(400, initial_height)

        elif index == 1:
            screen = wdg.QApplication.primaryScreen()
            screen_height = screen.availableGeometry().height()

            if screen_height < 720:
                initial_height = int(screen_height * 0.85)
            else:
                initial_height = 1000

            self.resize(830, initial_height)
            self.setMinimumSize(830, min(initial_height, int(screen_height * 0.5)))
            self.setFixedSize(830, initial_height)

    def referenced_cams_radio_btn_clicked(self):

        self.create_locs_setup_btn.setVisible(True)
        self.create_camera_handles_btn.setVisible(False)

    def imported_cams_radio_btn_clicked(self):

        self.create_locs_setup_btn.setVisible(False)
        self.create_camera_handles_btn.setVisible(True)

    @staticmethod
    def create_locs_setup_btn_clicked():
        mbr_egn_create_cam_locs_with_handles()

    @staticmethod
    def create_camera_handles_btn_clicked():
        mbr_egn_add_camera_handles()

    def use_loc_handles_radio_btn_clicked(self):

        self.range_start_le.setEnabled(False)
        self.range_end_le.setEnabled(False)

    def use_cam_handles_radio_btn_clicked(self):

        self.range_start_le.setEnabled(False)
        self.range_end_le.setEnabled(False)

    def use_custom_range_radio_btn_clicked(self):

        self.range_start_le.setEnabled(True)
        self.range_end_le.setEnabled(True)

    def create_sequencer_shot_btn_clicked(self):

        selection = cmds.ls(selection=True)

        if self.use_loc_handles_radio_btn.isChecked():

            if '_subOffsetCam' in selection[0] and cmds.listRelatives(selection[1], shapes=True, type='camera')[0]:

                colon_idx = selection[1].find(':')
                cam_nmp = selection[1][:colon_idx]
                mbr_egn_create_sequencer_shot_from_loc_handles(cam_nmp, selection[1])

            else:
                wdg.QMessageBox.warning(None, 'Warning', 'You need to select first a locator, then the camera')


        elif self.use_cam_handles_radio_btn.isChecked():

            for idx in range(len(selection)):

                cam_transform = selection[idx]
                cam_shape = cmds.listRelatives(cam_transform, shapes=True, type='camera')[0]
                print(cam_transform)

                if cam_shape:
                    print('works')

                    if cmds.attributeQuery('startFrame', node=cam_transform, exists=True) and cmds.attributeQuery(
                            'endFrame', node=cam_transform, exists=True):
                        mbr_egn_create_sequencer_shot_from_cam_handles(cam_transform)

                else:
                    wdg.QMessageBox.warning(None, 'Warning', 'All selected objects must be cameras')

        elif self.use_custom_range_radio_btn.isChecked():

            if len(selection) > 1:
                wdg.QMessageBox.warning(None, 'Warning', 'You can only create one shot at a time with this option')
                return

            start_frame = self.range_start_le.text
            self.range_start_le.setText(start_frame)

            end_frame = int(self.range_end_le.text())
            self.range_end_le.setText(end_frame)

    # @staticmethod
    # def frame_selected_shot_btn_clicked():
    #     mbr_egn_frame_timeline_to_sequencer_range()

    def playblast_shot_path_browse_btn_clicked(self):

        # Raise dialog window to prompt user to choose a folder
        folder = wdg.QFileDialog.getExistingDirectory(
            None,
            'Select Folder',
            '/',
            wdg.QFileDialog.ShowDirsOnly
        )

        if folder:
            playblast_shot_new_path = folder
            self.playblast_shot_path_le.setText(playblast_shot_new_path)

    def playblast_shot_btn_clicked(self):

        rows = [r for r in range(self.shots_table.rowCount()) if self.shot_checkboxes[r].isChecked()]

        if not rows:
            wdg.QMessageBox.information(self, 'Playblast', 'No shots are selected')
            return

        for row in rows:
            self.playblast_shot_by_row(row)

    def playblast_sequence_btn_clicked(self):

        self.playblast_sequence()

    def playblast_sequence_path_browse_btn_clicked(self):

        # Raise dialog window to prompt user to choose a folder
        folder = wdg.QFileDialog.getExistingDirectory(
            None,
            'Select Folder',
            '/',
            wdg.QFileDialog.ShowDirsOnly
        )

        if folder:
            playblast_sequence_new_path = folder
            self.playblast_sequence_path_le.setText(playblast_sequence_new_path)

    def frame_row_clicked(self):

        row = self._row_of_sender()
        if row < 0:
            return
        data = self.get_row_data(row)

        if not cmds.objExists(data['shot']):
            wdg.QMessageBox.warning(self, 'Warning', f"Shot {data['shot']} no longer exists")
            return

        cmds.playbackOptions(minTime=data['start'], maxTime=data['end'])

    def playblast_row_clicked(self):

        row = self._row_of_sender()
        if row < 0:
            return

        self.playblast_shot_by_row(row)

    # -------------------------------------
    #
    #       Utility Methods
    #
    # -------------------------------------

    def _row_of_sender(self):

        btn = self.sender()
        container = btn.parentWidget()
        pos = container.mapTo(self.shots_table.viewport(), core.QPoint(0, 0))
        return self.shots_table.indexAt(pos).row()

    def get_row_data(self, row):

        start, end = self.shots_table.item(row, 3).text().split(' - ')
        return {
            'camera': self.shots_table.item(row, 1).text(),
            'shot': self.shots_table.item(row, 2).text(),
            'start': int(start),
            'end': int(end),
        }

    def playblast_shot_by_row(self, row):

        data = self.get_row_data(row)

        if not cmds.objExists(data['shot']):
            wdg.QMessageBox.warning(self, 'Warning', f"Shot {data['shot']} no longer exists")
            return

        cmds.playbackOptions(minTime=data['start'], maxTime=data['end'])

        # Filename string
        scene_name = cmds.file(query=True, sceneName=True, shortName=True)
        base_name = os.path.splitext(scene_name)[0]

        base_path = self.playblast_shot_path_le.text()
        cam_name_idx = data['camera'].find(':')
        cam_name = data['camera'][:cam_name_idx]
        version = base_name[-4:]

        panels = [p for p in cmds.getPanel(visiblePanels=True)
                  if cmds.getPanel(typeOf=p) == 'modelPanel']
        if not panels:
            cmds.warning('No visible model panel found')
            return
        panel = panels[0]

        original_cam = cmds.modelPanel(panel, query=True, camera=True)

        cmds.modelPanel(panel, edit=True, camera=data['camera'])
        cmds.setFocus(panel)  # make it the active panel
        cmds.refresh()  # let the viewport actually update

        cmds.sequenceManager(currentTime=data['start'])

        try:
            mbr_egn_execute_playblast(data['start'], data['end'], f'{base_path}/{cam_name}_previs_pb_{version}.mov',
                                      False)
        finally:
            cmds.modelPanel(panel, edit=True, camera=original_cam)

    def playblast_sequence(self):

        scene_name = cmds.file(query=True, sceneName=True, shortName=True)
        base_name = os.path.splitext(scene_name)[0]

        base_path = self.playblast_sequence_path_le.text()
        base_name_first_idx = base_name.find('_')
        base_name_second_idx = base_name.find('_', base_name_first_idx + 1)
        seq_name = base_name[:base_name_second_idx]
        version = base_name[-4:]

        shots = cmds.ls(type='shot')
        seq_start = int(min(cmds.shot(s, query=True, sequenceStartTime=True) for s in shots))
        seq_end = int(max(cmds.shot(s, query=True, sequenceEndTime=True) for s in shots))

        panels = [p for p in cmds.getPanel(visiblePanels=True)
                  if cmds.getPanel(typeOf=p) == 'modelPanel']
        if not panels:
            cmds.warning('No visible model panel found')
            return
        panel = panels[0]
        cmds.sequenceManager(modelPanel=panel)

        mbr_egn_execute_playblast(seq_start, seq_end, f"{base_path}/{seq_name}_previs_pb_{version}.mov", True)


# -------------------------------------
#
#       Run Function
#
# -------------------------------------

def run():
    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = Sequencer_Shot_Manager(parent=mbr_util_get_maya_window())
    MAIN_WINDOW.show()