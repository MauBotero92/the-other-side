# -------------------------------------------
#
#       Import modules
#
# -------------------------------------------

from TOS_Pipeline.src.dcc.maya.utils.qt_compat import wdg, core, gui
from TOS_Pipeline.src.dcc.maya.utils.qt_utils import mbr_util_get_maya_window
from TOS_Pipeline.src.dcc.maya.utils.qt_helpers import *
from TOS_Pipeline.src.dcc.maya.utils.maya_utils import *

from TOS_Pipeline.src.dcc.maya.layout.engine.camera_framer_engine import *

import maya.cmds as cmds

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

class Camera_Framer(wdg.QMainWindow):

    def __init__(self, parent=None):
        super(Camera_Framer, self).__init__(parent)

        # -------------------------------------
        #
        #       Window Title and Size
        #
        # -------------------------------------

        self.setWindowTitle(f"MBR Camera Framer {__VERSION__}")
        self.setFocusPolicy(core.Qt.ClickFocus)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = 660

        self.resize(700, initial_height)
        self.setMinimumSize(700, min(initial_height, int(screen_height * 0.5)))
        self.setFixedSize(700, initial_height)

        # -------------------------------------
        #
        #       Menu Bar
        #
        # -------------------------------------

        menubar = self.menuBar()
        settings_menu = menubar.addMenu('Settings')
        menubar.addMenu('Help')

        self.refresh_action = gui.QAction('Refresh', self)
        self.refresh_action.setShortcut('F5')
        settings_menu.addAction(self.refresh_action)

        # -------------------------------------
        #
        #       Widgets Variables
        #
        # -------------------------------------

        # Camera Nodes Names
        self.cam_node_orbit_label = None
        self.cam_node_orbit_le = None
        self.cam_node_placement_label = None
        self.cam_node_placement_le = None
        self.cam_node_offset_label = None
        self.cam_node_offset_le = None

        # Initial Setup Camera Widgets
        self.init_camera_label = None
        self.init_camera_combo = None
        self.init_create_setup_btn = None

        # Initial Setup Subject Widgets
        self.subject_01_check = None
        self.subject_01_le = None
        self.subject_01_btn = None

        self.subject_02_check = None
        self.subject_02_le = None
        self.subject_02_btn = None

        # Action Buttons Widgets
        self.frame_btn = None
        self.bake_to_cam_btn = None

        self.select_orbit_node_btn = None
        self.select_placement_node_btn = None
        self.select_offset_node_btn = None

        # Separator Widgets
        self.separator_wdg = None

        # Camera Main Options Widgets
        self.focal_length_label = None
        self.focal_length_combo = None
        self.focal_length_key_btn = None

        # Camera Additional Options Widgets
        self.dof_check = None
        self.frustum_check = None

        # Camera Nodes Widgets
        self.orbit_radio_btn = None
        self.placement_radio_btn = None
        self.offset_radio_btn = None

        self.scale_label = None
        self.scale_combo = None

        # Camera Sliders Widgets
        self.translate_x_slider = None
        self.translate_x_le = None

        self.translate_y_slider = None
        self.translate_y_le = None

        self.translate_z_slider = None
        self.translate_z_le = None

        self.rotate_x_slider = None
        self.rotate_x_le = None

        self.rotate_y_slider = None
        self.rotate_y_le = None

        self.rotate_z_slider = None
        self.rotate_z_le = None

        self.key_all_btn = None

        # -------------------------------------
        #
        #       Other Variables
        #
        # -------------------------------------

        self.cam_ns = mbr_util_get_camera_namespaces()

        self.orbit_node = 'camera_all'
        self.placement_node = 'cam_offset'
        self.offset_node = 'animCam'
        self.anim_cam_node = 'animCam'

        self.scale_list = ['0.01', '0.1', '1.0', '10.0', '100.0']
        self.scale_factor = 1.0
        self.start_value = None

        self.lens_kit = ['24.0', '28.0', '35.0', '40.0', '55.0', '65.0', '75.0', '85.0', '120.0']

        self.attr_le = {}

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

        self.btn_small_style = """
            QPushButton {
                background-color: #5d5d5d;
                color: #dddddd;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px 10px;

                font-style: italic;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: black;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
            """

        self.separator_style = "color: #a9a9a9; background-color: #a9a9a9;"

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
        #       Camera Node Names Widgets
        #
        # -------------------------------------

        self.cam_node_orbit_label = wdg.QLabel('Orbit Node')
        self.cam_node_orbit_le = wdg.QLineEdit(self.orbit_node)

        self.cam_node_placement_label = wdg.QLabel('Placement Node')
        self.cam_node_placement_le = wdg.QLineEdit(self.placement_node)

        self.cam_node_offset_label = wdg.QLabel('Offset Node')
        self.cam_node_offset_le = wdg.QLineEdit(self.offset_node)

        # -------------------------------------
        #
        #       Initial Setup Widgets
        #
        # -------------------------------------

        # Initial Setup Camera Widgets
        self.init_camera_label = wdg.QLabel('Camera     ')

        self.init_camera_combo = wdg.QComboBox()
        self.init_camera_combo.setFixedWidth(200)
        if len(self.cam_ns) > 0:
            self.init_camera_combo.addItems(self.cam_ns)
        if len(self.cam_ns) == 0:
            self.init_camera_combo.setEnabled(False)

        self.init_create_setup_btn = wdg.QPushButton('Create Setup')
        self.init_create_setup_btn.setStyleSheet(self.btn_style)

        # Initial Setup Subject Widgets
        self.subject_01_check = wdg.QLabel('Subject   ')
        # self.subject_01_check.setChecked(True)

        self.subject_01_le = wdg.QLineEdit()
        self.subject_01_le.setFixedWidth(250)
        self.subject_01_le.setEnabled(False)

        self.subject_01_btn = wdg.QPushButton('<')

        # self.subject_02_check = wdg.QCheckBox('Subject 2     ')
        #
        # self.subject_02_le = wdg.QLineEdit()
        # self.subject_02_le.setFixedWidth(250)
        # self.subject_02_le.setEnabled(False)
        #
        # self.subject_02_btn = wdg.QPushButton('<')

        # -------------------------------------
        #
        #       Action Buttons Widgets
        #
        # -------------------------------------

        # Action Buttons Widgets
        self.frame_btn = wdg.QPushButton('Frame')
        self.frame_btn.setStyleSheet(self.btn_style)
        self.frame_btn.setFixedWidth(150)

        self.bake_to_cam_btn = wdg.QPushButton('Bake To Camera')
        self.bake_to_cam_btn.setStyleSheet(self.btn_style)
        self.bake_to_cam_btn.setFixedWidth(150)

        self.select_orbit_node_btn = wdg.QPushButton('Select Orbit')
        self.select_orbit_node_btn.setStyleSheet(self.btn_style)
        self.select_orbit_node_btn.setFixedWidth(150)

        self.select_placement_node_btn = wdg.QPushButton('Select Placement')
        self.select_placement_node_btn.setStyleSheet(self.btn_style)
        self.select_placement_node_btn.setFixedWidth(150)

        self.select_offset_node_btn = wdg.QPushButton('Select Offset')
        self.select_offset_node_btn.setStyleSheet(self.btn_style)
        self.select_offset_node_btn.setFixedWidth(150)

        # -------------------------------------
        #
        #       Separator Widgets
        #
        # -------------------------------------

        self.separator_wdg = wdg.QFrame()
        self.separator_wdg.setFixedWidth(600)
        self.separator_wdg.setFrameShape(wdg.QFrame.HLine)
        self.separator_wdg.setFrameShadow(wdg.QFrame.Plain)
        self.separator_wdg.setStyleSheet(self.separator_style)

        # -------------------------------------
        #
        #       Camera Options Widgets
        #
        # -------------------------------------

        # Camera Main Options Widgets
        self.focal_length_label = wdg.QLabel('Focal Length     ')

        self.focal_length_combo = wdg.QComboBox()
        self.focal_length_combo.setFixedWidth(70)
        self.focal_length_combo.addItems(self.lens_kit)

        self.focal_length_key_btn = wdg.QPushButton('KEY')
        self.focal_length_key_btn.setStyleSheet(self.btn_small_style)
        self.focal_length_key_btn.setFixedHeight(25)

        # Camera Additional Options Widgets
        self.dof_check = wdg.QCheckBox('Depth of Field')

        self.frustum_check = wdg.QCheckBox('Frustum')


        # -------------------------------------
        #
        #       Camera Nodes Widgets
        #
        # -------------------------------------

        # Camera Nodes Widgets
        self.orbit_radio_btn = wdg.QRadioButton('Orbit     ')
        self.orbit_radio_btn.setChecked(True)

        self.placement_radio_btn = wdg.QRadioButton('Placement     ')

        self.offset_radio_btn = wdg.QRadioButton('Offset     ')

        self.scale_label = wdg.QLabel('Unit Scale')

        self.scale_combo = wdg.QComboBox()
        self.scale_combo.setFixedWidth(70)
        self.scale_combo.addItems(self.scale_list)
        self.scale_combo.setCurrentIndex(2)

        # -------------------------------------
        #
        #       Camera Sliders Widgets
        #
        # -------------------------------------

        # Camera Sliders Widgets
        self.translate_x_slider = wdg.QSlider()
        self.translate_x_slider.setOrientation(core.Qt.Horizontal)
        self.translate_x_slider.setFixedWidth(500)
        self.translate_x_slider.setRange(-200, 200)
        self.translate_x_slider.setValue(0)

        self.translate_x_le = wdg.QLineEdit()
        self.translate_x_le.setFixedWidth(50)
        self.translate_x_le.setEnabled(False)

        self.translate_y_slider = wdg.QSlider()
        self.translate_y_slider.setOrientation(core.Qt.Horizontal)
        self.translate_y_slider.setFixedWidth(500)
        self.translate_y_slider.setRange(-200, 200)
        self.translate_y_slider.setValue(0)

        self.translate_y_le = wdg.QLineEdit()
        self.translate_y_le.setFixedWidth(50)
        self.translate_y_le.setEnabled(False)

        self.translate_z_slider = wdg.QSlider()
        self.translate_z_slider.setOrientation(core.Qt.Horizontal)
        self.translate_z_slider.setFixedWidth(500)
        self.translate_z_slider.setRange(-200, 200)
        self.translate_z_slider.setValue(0)

        self.translate_z_le = wdg.QLineEdit()
        self.translate_z_le.setFixedWidth(50)
        self.translate_z_le.setEnabled(False)

        self.rotate_x_slider = wdg.QSlider()
        self.rotate_x_slider.setOrientation(core.Qt.Horizontal)
        self.rotate_x_slider.setFixedWidth(500)
        self.rotate_x_slider.setRange(-180, 180)
        self.rotate_x_slider.setValue(0)

        self.rotate_x_le = wdg.QLineEdit()
        self.rotate_x_le.setFixedWidth(50)
        self.rotate_x_le.setEnabled(False)

        self.rotate_y_slider = wdg.QSlider()
        self.rotate_y_slider.setOrientation(core.Qt.Horizontal)
        self.rotate_y_slider.setFixedWidth(500)
        self.rotate_y_slider.setRange(-180, 180)
        self.rotate_y_slider.setValue(0)

        self.rotate_y_le = wdg.QLineEdit()
        self.rotate_y_le.setFixedWidth(50)
        self.rotate_y_le.setEnabled(False)

        self.rotate_z_slider = wdg.QSlider()
        self.rotate_z_slider.setOrientation(core.Qt.Horizontal)
        self.rotate_z_slider.setFixedWidth(500)
        self.rotate_z_slider.setRange(-180, 180)
        self.rotate_z_slider.setValue(0)

        self.rotate_z_le = wdg.QLineEdit()
        self.rotate_z_le.setFixedWidth(50)
        self.rotate_z_le.setEnabled(False)

        self.key_all_btn = wdg.QPushButton('KEY ALL')
        self.key_all_btn.setStyleSheet(self.btn_small_style)
        self.key_all_btn.setFixedWidth(70)

        # -------------------------------------
        #
        #       Attributes Dictionary
        #
        # -------------------------------------

        self.attr_le = {
            'tx': self.translate_x_le,
            'ty': self.translate_y_le,
            'tz': self.translate_z_le,
            'rx': self.rotate_x_le,
            'ry': self.rotate_y_le,
            'rz': self.rotate_z_le,
        }

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
        #       Main and Sub Main Layout
        #
        # -------------------------------------

        main_lyt = wdg.QVBoxLayout(central_wdg)

        sub_main_lyt = wdg.QVBoxLayout()
        sub_main_lyt.setContentsMargins(0,0,0,0)
        sub_main_lyt.setAlignment(core.Qt.AlignTop)

        # -------------------------------------
        #
        #       Camera Nodes Names Layout
        #
        # -------------------------------------

        cam_nodes_suffixes_lyt = wdg.QHBoxLayout()
        cam_nodes_suffixes_lyt.setContentsMargins(10,0,0,0)
        cam_nodes_suffixes_lyt.setAlignment(core.Qt.AlignTop)

        # -------------------------------------
        #
        #       Camera Nodes Names Sections
        #
        # -------------------------------------

        cam_node_name_orbit = wdg.QVBoxLayout()

        cam_node_name_placement = wdg.QVBoxLayout()

        cam_node_name_offset = wdg.QVBoxLayout()

        # -------------------------------------
        #
        #       Initial Setup Layout
        #
        # -------------------------------------

        initial_setup_grp = wdg.QGroupBox('Initial Setup')
        initial_setup_grp.setStyleSheet(self.group_boxes_style)
        initial_setup_grp.setFixedHeight(125)
        initial_setup_lyt = wdg.QVBoxLayout()
        initial_setup_grp.setLayout(initial_setup_lyt)

        initial_setup_sub_lyt = wdg.QHBoxLayout()
        initial_setup_sub_lyt.setAlignment(core.Qt.AlignLeft)

        # -------------------------------------
        #
        #       Initial Setup Sections
        #
        # -------------------------------------

        camera_lyt = wdg.QVBoxLayout()
        camera_lyt.setContentsMargins(10,5,0,0)
        camera_lyt.setAlignment(core.Qt.AlignLeft)

        subjects_lyt = wdg.QGridLayout()
        subjects_lyt.setContentsMargins(20,5,0,0)
        subjects_lyt.setAlignment(core.Qt.AlignLeft)

        # -------------------------------------
        #
        #       Initial Setup - Camera
        #
        # -------------------------------------

        camera_nmp_lyt = wdg.QHBoxLayout()
        camera_nmp_lyt.setAlignment(core.Qt.AlignTop)
        camera_nmp_lyt.setContentsMargins(0,0,0,0)

        create_cam_setup_lyt = wdg.QHBoxLayout()

        # -------------------------------------
        #
        #       Action Buttons Layout
        #
        # -------------------------------------

        action_main_lyt = wdg.QVBoxLayout()

        action_btn_lyt = wdg.QHBoxLayout()
        action_btn_lyt.setContentsMargins(0,10,0,10)
        action_btn_lyt.setAlignment(core.Qt.AlignCenter)

        node_picker_lyt = wdg.QHBoxLayout()
        node_picker_lyt.setContentsMargins(0,0,0,0)
        node_picker_lyt.setAlignment(core.Qt.AlignCenter)

        node_picker_radio_btn_lyt = wdg.QHBoxLayout()
        node_picker_radio_btn_lyt.setContentsMargins(0,0,0,0)
        node_picker_radio_btn_lyt.setAlignment(core.Qt.AlignCenter)

        # -------------------------------------
        #
        #       Separator Layout
        #
        # -------------------------------------

        separator_lyt = wdg.QHBoxLayout()

        # -------------------------------------
        #
        #       Framer Layout
        #
        # -------------------------------------

        framer_lyt = wdg.QVBoxLayout()
        framer_lyt.setContentsMargins(0,10,0,0)
        framer_lyt.setAlignment(core.Qt.AlignTop)

        # -------------------------------------
        #
        #       Framer Sections
        #
        # -------------------------------------

        camera_options_lyt = wdg.QHBoxLayout()
        camera_options_lyt.setContentsMargins(40,0,0,20)

        scale_lyt = wdg.QHBoxLayout()
        scale_lyt.setContentsMargins(0,0,0,0)
        scale_lyt.setAlignment(core.Qt.AlignCenter)

        camera_nodes_lyt = wdg.QHBoxLayout()
        camera_nodes_lyt.setContentsMargins(0,0,0,0)
        camera_nodes_lyt.setAlignment(core.Qt.AlignCenter)

        camera_sliders_lyt = wdg.QFormLayout()
        camera_sliders_lyt.setContentsMargins(10,10,0,0)
        camera_sliders_lyt.setFieldGrowthPolicy(wdg.QFormLayout.FieldsStayAtSizeHint)
        camera_sliders_lyt.setLabelAlignment(core.Qt.AlignRight)
        camera_sliders_lyt.setHorizontalSpacing(5)
        camera_sliders_lyt.setFormAlignment(core.Qt.AlignHCenter | core.Qt.AlignTop)

        # -------------------------------------
        #
        #       Framer - Camera Options
        #
        # -------------------------------------

        camera_main_options_lyt = wdg.QVBoxLayout()
        camera_main_options_lyt.setContentsMargins(0,0,0,0)
        camera_main_options_lyt.setAlignment(core.Qt.AlignLeft)

        camera_focal_length_lyt = wdg.QHBoxLayout()

        # -------------------------------------
        #
        #       Framer - Cam Additional Options
        #
        # -------------------------------------

        camera_additional_options_lyt = wdg.QVBoxLayout()
        camera_additional_options_lyt.setContentsMargins(30,0,0,0)

        # -------------------------------------
        #
        #       Framer - Sliders
        #
        # -------------------------------------

        translate_x_lyt = wdg.QHBoxLayout()

        translate_y_lyt = wdg.QHBoxLayout()

        translate_z_lyt = wdg.QHBoxLayout()

        rotate_x_lyt = wdg.QHBoxLayout()

        rotate_y_lyt = wdg.QHBoxLayout()

        rotate_z_lyt = wdg.QHBoxLayout()

        key_all_lyt = wdg.QHBoxLayout()
        key_all_lyt.setContentsMargins(0,5,30,0)
        key_all_lyt.setAlignment(core.Qt.AlignRight)

        # -------------------------------------
        #
        #       Layout Arrangement
        #
        # -------------------------------------

        # Main Layout
        main_lyt.addLayout(sub_main_lyt)

        # Sub Main Layout
        # sub_main_lyt.addWidget(cam_nodes_suffixes_grp)
        sub_main_lyt.addWidget(initial_setup_grp)
        sub_main_lyt.addLayout(action_main_lyt)
        sub_main_lyt.addLayout(separator_lyt)
        sub_main_lyt.addLayout(framer_lyt)

        # Initial Setup Layout
        initial_setup_lyt.addLayout(initial_setup_sub_lyt)
        initial_setup_lyt.addLayout(cam_nodes_suffixes_lyt)
        initial_setup_sub_lyt.addLayout(camera_lyt)
        initial_setup_sub_lyt.addLayout(subjects_lyt)
        initial_setup_sub_lyt.addStretch(1)

        # Camera Node Names Layout
        cam_nodes_suffixes_lyt.addLayout(cam_node_name_orbit)
        cam_nodes_suffixes_lyt.addLayout(cam_node_name_placement)
        cam_nodes_suffixes_lyt.addLayout(cam_node_name_offset)

        # Camera Layout
        camera_lyt.addLayout(camera_nmp_lyt)
        camera_lyt.addLayout(create_cam_setup_lyt)

        # Action Layout
        action_main_lyt.addLayout(action_btn_lyt)

        # Framer Layout
        framer_lyt.addLayout(camera_options_lyt)
        framer_lyt.addLayout(scale_lyt)
        framer_lyt.addLayout(node_picker_lyt)
        framer_lyt.addLayout(node_picker_radio_btn_lyt)
        framer_lyt.addLayout(camera_sliders_lyt)
        framer_lyt.addLayout(key_all_lyt)

        # Camera Options Layout
        camera_options_lyt.addLayout(camera_main_options_lyt)
        camera_options_lyt.addLayout(camera_additional_options_lyt)

        # Camera Main Options Layout
        camera_main_options_lyt.addLayout(camera_focal_length_lyt)

        # Camera Sliders Layout
        camera_sliders_lyt.addRow('TX     ', translate_x_lyt)
        camera_sliders_lyt.addRow('TY     ', translate_y_lyt)
        camera_sliders_lyt.addRow('TZ     ', translate_z_lyt)
        camera_sliders_lyt.addRow('RX     ', rotate_x_lyt)
        camera_sliders_lyt.addRow('RY     ', rotate_y_lyt)
        camera_sliders_lyt.addRow('RZ     ', rotate_z_lyt)

        # -------------------------------------
        #
        #       Widgets Arrangement
        #
        # -------------------------------------

        # Camera Nodes Names Layout
        cam_node_name_orbit.addWidget(self.cam_node_orbit_label)
        cam_node_name_orbit.addWidget(self.cam_node_orbit_le)
        cam_node_name_placement.addWidget(self.cam_node_placement_label)
        cam_node_name_placement.addWidget(self.cam_node_placement_le)
        cam_node_name_offset.addWidget(self.cam_node_offset_label)
        cam_node_name_offset.addWidget(self.cam_node_offset_le)

        # Camera Init Layout
        camera_nmp_lyt.addWidget(self.init_camera_label)
        camera_nmp_lyt.addWidget(self.init_camera_combo)
        # create_cam_setup_lyt.addWidget(self.init_create_setup_btn)

        # Subject 01 Layout
        subjects_lyt.addWidget(self.subject_01_check, 0, 0)
        subjects_lyt.addWidget(self.subject_01_le, 0, 1)
        subjects_lyt.addWidget(self.subject_01_btn, 0, 2)

        # Action Buttons Layout
        action_btn_lyt.addWidget(self.frame_btn)
        action_btn_lyt.addWidget(self.bake_to_cam_btn)

        # Separator Layout
        separator_lyt.addWidget(self.separator_wdg)

        # Camera Focal Length Layout
        camera_focal_length_lyt.addWidget(self.focal_length_label)
        camera_focal_length_lyt.addWidget(self.focal_length_combo)
        camera_focal_length_lyt.addWidget(self.focal_length_key_btn)

        # Camera Additional Options Layout
        camera_additional_options_lyt.addWidget(self.dof_check)
        camera_additional_options_lyt.addWidget(self.frustum_check)

        # Camera Nodes Layout
        scale_lyt.addWidget(self.scale_label)
        scale_lyt.addWidget(self.scale_combo)

        # Node Picker Layout
        node_picker_lyt.addWidget(self.select_orbit_node_btn)
        node_picker_lyt.addWidget(self.select_placement_node_btn)
        node_picker_lyt.addWidget(self.select_offset_node_btn)
        node_picker_radio_btn_lyt.addWidget(self.orbit_radio_btn)
        node_picker_radio_btn_lyt.addWidget(self.placement_radio_btn)
        node_picker_radio_btn_lyt.addWidget(self.offset_radio_btn)

        # Camera Sliders Layout (TX)
        translate_x_lyt.addWidget(self.translate_x_slider)
        translate_x_lyt.addWidget(self.translate_x_le)

        # Camera Sliders Layout (TY)
        translate_y_lyt.addWidget(self.translate_y_slider)
        translate_y_lyt.addWidget(self.translate_y_le)

        # Camera Sliders Layout (TZ)
        translate_z_lyt.addWidget(self.translate_z_slider)
        translate_z_lyt.addWidget(self.translate_z_le)

        # Camera Sliders Layout (RX)
        rotate_x_lyt.addWidget(self.rotate_x_slider)
        rotate_x_lyt.addWidget(self.rotate_x_le)

        # Camera Sliders Layout (RY)
        rotate_y_lyt.addWidget(self.rotate_y_slider)
        rotate_y_lyt.addWidget(self.rotate_y_le)

        # Camera Sliders Layout (RZ)
        rotate_z_lyt.addWidget(self.rotate_z_slider)
        rotate_z_lyt.addWidget(self.rotate_z_le)

        # Key All Layout
        key_all_lyt.addWidget(self.key_all_btn)


    # -------------------------------------
    #
    #       Create Connections
    #
    # -------------------------------------

    def create_connections(self):

        self.refresh_action.triggered.connect(self.refresh_action_triggered)

        self.cam_node_orbit_le.editingFinished.connect(self.cam_node_orbit_edited)
        self.cam_node_placement_le.editingFinished.connect(self.cam_node_placement_edited)
        self.cam_node_offset_le.editingFinished.connect(self.cam_node_offset_edited)

        self.init_camera_combo.currentIndexChanged.connect(self.init_camera_combo_changed)

        self.subject_01_btn.clicked.connect(self.subject_01_clicked)
        # self.subject_02_btn.clicked.connect(self.subject_02_clicked)

        self.frame_btn.clicked.connect(self.frame_btn_clicked)
        self.bake_to_cam_btn.clicked.connect(self.bake_to_cam_btn_clicked)

        self.select_orbit_node_btn.clicked.connect(self.select_orbit_node_btn_clicked)
        self.select_placement_node_btn.clicked.connect(self.select_placement_node_btn_clicked)
        self.select_offset_node_btn.clicked.connect(self.select_offset_node_btn_clicked)

        self.focal_length_combo.currentIndexChanged.connect(self.focal_length_combo_changed)

        self.scale_combo.currentIndexChanged.connect(self.scale_combo_changed)

        self.orbit_radio_btn.toggled.connect(self.orbit_radio_btn_toggled)
        self.placement_radio_btn.toggled.connect(self.placement_radio_btn_toggled)
        self.offset_radio_btn.toggled.connect(self.offset_radio_btn_toggled)

        self.dof_check.toggled.connect(self.dof_check_toggled)
        self.frustum_check.toggled.connect(self.frustum_check_toggled)

        self.translate_x_slider.sliderPressed.connect(lambda: self.slider_pressed('tx'))
        self.translate_x_slider.valueChanged.connect(lambda v: self.slider_changed('tx', v))
        self.translate_x_slider.sliderReleased.connect(lambda: self.slider_released(self.translate_x_slider))

        self.translate_y_slider.sliderPressed.connect(lambda: self.slider_pressed('ty'))
        self.translate_y_slider.valueChanged.connect(lambda v: self.slider_changed('ty', v))
        self.translate_y_slider.sliderReleased.connect(lambda: self.slider_released(self.translate_y_slider))

        self.translate_z_slider.sliderPressed.connect(lambda: self.slider_pressed('tz'))
        self.translate_z_slider.valueChanged.connect(lambda v: self.slider_changed('tz', v))
        self.translate_z_slider.sliderReleased.connect(lambda: self.slider_released(self.translate_z_slider))

        self.rotate_x_slider.sliderPressed.connect(lambda: self.slider_pressed('rx'))
        self.rotate_x_slider.valueChanged.connect(lambda v: self.slider_changed('rx', v))
        self.rotate_x_slider.sliderReleased.connect(lambda: self.slider_released(self.rotate_x_slider))

        self.rotate_y_slider.sliderPressed.connect(lambda: self.slider_pressed('ry'))
        self.rotate_y_slider.valueChanged.connect(lambda v: self.slider_changed('ry', v))
        self.rotate_y_slider.sliderReleased.connect(lambda: self.slider_released(self.rotate_y_slider))

        self.rotate_z_slider.sliderPressed.connect(lambda: self.slider_pressed('rz'))
        self.rotate_z_slider.valueChanged.connect(lambda v: self.slider_changed('rz', v))
        self.rotate_z_slider.sliderReleased.connect(lambda: self.slider_released(self.rotate_z_slider))

        self.key_all_btn.clicked.connect(self.key_all_btn_clicked)

    # -------------------------------------
    #
    #       Set Defaults
    #
    # -------------------------------------

    def set_defaults(self):

        # Get camera lens of current camera and sets it on the focal length
        cur_ns = self.init_camera_combo.currentText()
        if cmds.objExists(f"{cur_ns}:{self.anim_cam_node}.Lens"):
            cur_focal_length = cmds.getAttr(f"{cur_ns}:{self.anim_cam_node}.Lens")
            self.focal_length_combo.setCurrentText(str(cur_focal_length))

        # Disable orbit translation
        self.translate_x_slider.setEnabled(False)
        self.translate_y_slider.setEnabled(False)
        self.translate_z_slider.setEnabled(False)

        # Get camera depth of field state and set the checkbox
        if cmds.objExists(f"{cur_ns}:{self.anim_cam_node}Shape.depthOfField"):
            cur_dof = cmds.getAttr(f"{cur_ns}:{self.anim_cam_node}Shape.depthOfField")
            if cur_dof == 0:
                self.dof_check.setChecked(False)
            else:
                self.dof_check.setChecked(True)

        if cmds.objExists(f"{cur_ns}:{self.anim_cam_node}Shape.displayCameraFrustum"):
            cur_frustum = cmds.getAttr(f"{cur_ns}:{self.anim_cam_node}Shape.displayCameraFrustum")
            if cur_frustum == 0:
                self.frustum_check.setChecked(False)
            else:
                self.frustum_check.setChecked(True)

        # Set Line Edit initial values
        if cmds.objExists(f"{cur_ns}:{self.orbit_node}"):
            cur_tx = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.tx")
            cur_ty = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.ty")
            cur_tz = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.tz")
            cur_rx = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.rx")
            cur_ry = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.ry")
            cur_rz = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.rz")

            self.translate_x_le.setText(str(round(cur_tx, 3)))
            self.translate_y_le.setText(str(round(cur_ty, 3)))
            self.translate_z_le.setText(str(round(cur_tz, 3)))
            self.rotate_x_le.setText(str(round(cur_rx, 3)))
            self.rotate_y_le.setText(str(round(cur_ry, 3)))
            self.rotate_z_le.setText(str(round(cur_rz, 3)))

        self.cam_node_orbit_label.setFocus()

    # -------------------------------------
    #
    #       Signals
    #
    # -------------------------------------

    def refresh_action_triggered(self):

        self.cam_ns = mbr_util_get_camera_namespaces()
        self.init_camera_combo.clear()

        if len(self.cam_ns) > 0:
            self.init_camera_combo.setEnabled(True)
            self.init_camera_combo.addItems(self.cam_ns)
        if len(self.cam_ns) == 0:
            self.init_camera_combo.setEnabled(False)


    def cam_node_orbit_edited(self):

        self.orbit_node = self.cam_node_orbit_le.text()

    def cam_node_placement_edited(self):

        self.placement_node = self.cam_node_placement_le.text()

    def cam_node_offset_edited(self):

        self.offset_node = self.cam_node_offset_le.text()

    def init_camera_combo_changed(self):

        # Get camera lens of current camera and sets it on the focal length
        cur_ns = self.init_camera_combo.currentText()
        cur_focal_length = cmds.getAttr(f"{cur_ns}:{self.anim_cam_node}.Lens")
        self.focal_length_combo.setCurrentText(str(cur_focal_length))

    def subject_01_clicked(self):

        selected_obj = mbr_util_get_selected_object()
        self.subject_01_le.setText(selected_obj)

    def frame_btn_clicked(self):

        target = f"{self.init_camera_combo.currentText()}:{self.orbit_node}"
        source = self.subject_01_le.text()

        mbr_util_match_translation_to_obj(target, source)
        cmds.setAttr(f"{self.init_camera_combo.currentText()}:{self.placement_node}.tz", 150)

    def bake_to_cam_btn_clicked(self):

        cur_cam_node = f"{self.init_camera_combo.currentText()}:{self.anim_cam_node}"

        # Duplicate the camera
        dup_cam = cmds.duplicate(cur_cam_node)[0]
        new_cam = cmds.rename(dup_cam, f"{cur_cam_node}_baked")

        # Unparent camera
        cmds.parent(new_cam, world=True)

        # Constrain wp camera to old camera
        mbr_util_parent_constraint(cur_cam_node, new_cam, offset=False)

        # Bake camera
        cmds.select(new_cam, r=True)
        mbt_util_bake_anim()

        # Delete Constraint
        cons = cmds.listRelatives(new_cam, type='constraint')[0] or []
        cmds.delete(cons)

    def select_orbit_node_btn_clicked(self):

        cur_ns = self.init_camera_combo.currentText()
        cmds.select(f"{cur_ns}:{self.orbit_node}", r=True)

        self.orbit_radio_btn.setChecked(True)

    def select_placement_node_btn_clicked(self):

        cur_ns = self.init_camera_combo.currentText()
        cmds.select(f"{cur_ns}:{self.placement_node}", r=True)

        self.placement_radio_btn.setChecked(True)

    def select_offset_node_btn_clicked(self):

        cur_ns = self.init_camera_combo.currentText()
        cmds.select(f"{cur_ns}:{self.offset_node}", r=True)

        self.offset_radio_btn.setChecked(True)

    def focal_length_combo_changed(self):

        cur_ns = self.init_camera_combo.currentText()
        cur_lens = self.focal_length_combo.currentText()
        cmds.setAttr(f"{cur_ns}:{self.anim_cam_node}.Lens", float(cur_lens))

    def dof_check_toggled(self, checked):

        cur_ns = self.init_camera_combo.currentText()
        cur_dof = f"{cur_ns}:{self.anim_cam_node}.depthOfField"

        if checked:
            cmds.setAttr(cur_dof, 1)
        else:
            cmds.setAttr(cur_dof, 0)

    def frustum_check_toggled(self, checked):

        cur_ns = self.init_camera_combo.currentText()
        cur_frustum = f"{cur_ns}:{self.anim_cam_node}.displayCameraFrustum"

        if checked:
            cmds.setAttr(cur_frustum, 1)
        else:
            cmds.setAttr(cur_frustum, 0)

    def scale_combo_changed(self):

        cur_scale = self.scale_combo.currentText()

        try:
            self.scale_factor = float(cur_scale)
        except ValueError:
            self.scale_factor = 1.0

    def orbit_radio_btn_toggled(self):
        cur_ns = self.init_camera_combo.currentText()

        # Disable orbit translation
        self.translate_x_slider.setEnabled(False)
        self.translate_y_slider.setEnabled(False)
        self.translate_z_slider.setEnabled(False)

        # Set Line Edit initial values
        if cmds.objExists(f"{cur_ns}:{self.orbit_node}"):
            cur_tx = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.tx")
            cur_ty = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.ty")
            cur_tz = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.tz")
            cur_rx = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.rx")
            cur_ry = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.ry")
            cur_rz = cmds.getAttr(f"{cur_ns}:{self.orbit_node}.rz")

            self.translate_x_le.setText(str(round(cur_tx, 3)))
            self.translate_y_le.setText(str(round(cur_ty, 3)))
            self.translate_z_le.setText(str(round(cur_tz, 3)))
            self.rotate_x_le.setText(str(round(cur_rx, 3)))
            self.rotate_y_le.setText(str(round(cur_ry, 3)))
            self.rotate_z_le.setText(str(round(cur_rz, 3)))

    def placement_radio_btn_toggled(self):
        cur_ns = self.init_camera_combo.currentText()

        # Disable orbit translation
        self.translate_x_slider.setEnabled(True)
        self.translate_y_slider.setEnabled(True)
        self.translate_z_slider.setEnabled(True)

        # Set Line Edit initial values
        if cmds.objExists(f"{cur_ns}:{self.placement_node}"):
            cur_tx = cmds.getAttr(f"{cur_ns}:{self.placement_node}.tx")
            cur_ty = cmds.getAttr(f"{cur_ns}:{self.placement_node}.ty")
            cur_tz = cmds.getAttr(f"{cur_ns}:{self.placement_node}.tz")
            cur_rx = cmds.getAttr(f"{cur_ns}:{self.placement_node}.rx")
            cur_ry = cmds.getAttr(f"{cur_ns}:{self.placement_node}.ry")
            cur_rz = cmds.getAttr(f"{cur_ns}:{self.placement_node}.rz")

            self.translate_x_le.setText(str(round(cur_tx, 3)))
            self.translate_y_le.setText(str(round(cur_ty, 3)))
            self.translate_z_le.setText(str(round(cur_tz, 3)))
            self.rotate_x_le.setText(str(round(cur_rx, 3)))
            self.rotate_y_le.setText(str(round(cur_ry, 3)))
            self.rotate_z_le.setText(str(round(cur_rz, 3)))

    def offset_radio_btn_toggled(self):
        cur_ns = self.init_camera_combo.currentText()

        # Disable orbit translation
        self.translate_x_slider.setEnabled(True)
        self.translate_y_slider.setEnabled(True)
        self.translate_z_slider.setEnabled(True)

        # Set Line Edit initial values
        if cmds.objExists(f"{cur_ns}:{self.offset_node}"):
            cur_tx = cmds.getAttr(f"{cur_ns}:{self.offset_node}.tx")
            cur_ty = cmds.getAttr(f"{cur_ns}:{self.offset_node}.ty")
            cur_tz = cmds.getAttr(f"{cur_ns}:{self.offset_node}.tz")
            cur_rx = cmds.getAttr(f"{cur_ns}:{self.offset_node}.rx")
            cur_ry = cmds.getAttr(f"{cur_ns}:{self.offset_node}.ry")
            cur_rz = cmds.getAttr(f"{cur_ns}:{self.offset_node}.rz")

            self.translate_x_le.setText(str(round(cur_tx, 3)))
            self.translate_y_le.setText(str(round(cur_ty, 3)))
            self.translate_z_le.setText(str(round(cur_tz, 3)))
            self.rotate_x_le.setText(str(round(cur_rx, 3)))
            self.rotate_y_le.setText(str(round(cur_ry, 3)))
            self.rotate_z_le.setText(str(round(cur_rz, 3)))

    def slider_pressed(self, attr):

        cmds.undoInfo(openChunk=True)
        node = self.get_active_node()

        # Save where the attribute was when the drag started
        self.start_value = cmds.getAttr(f"{node}.{attr}") if node else None

    def slider_changed(self, attr, value):

        node = self.get_active_node()
        if node is None or self.start_value is None:
            return

        new_value = self.start_value + value * self.scale_factor
        cmds.setAttr(f"{node}.{attr}", new_value)
        self.attr_le[attr].setText(f"{str(round(new_value, 3))}")


    def slider_released(self, slider):

        # Snap the slider back to center so the next drag starts from 0
        slider.blockSignals(True)
        slider.setValue(0)
        slider.blockSignals(False)
        self.start_value = None
        cmds.undoInfo(closeChunk=True)

    def key_all_btn_clicked(self):

        cur_ns = self.init_camera_combo.currentText()

        if self.orbit_radio_btn.isChecked():
            cmds.setKeyframe(f"{cur_ns}:{self.orbit_node}", attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])

        elif self.placement_radio_btn.isChecked():
            cmds.setKeyframe(f"{cur_ns}:{self.placement_node}", attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])

        elif self.offset_radio_btn.isChecked():
            cmds.setKeyframe(f"{cur_ns}:{self.offset_node}", attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])

    # -------------------------------------
    #
    #       Utility Methods
    #
    # -------------------------------------

    def get_active_node(self):

        cur_ns = self.init_camera_combo.currentText()

        if self.orbit_radio_btn.isChecked():
            node = self.orbit_node

        elif self.placement_radio_btn.isChecked():
            node = self.placement_node

        elif self.offset_radio_btn.isChecked():
            node = self.offset_node

        else:
            return None

        return f"{cur_ns}:{node}"

# -------------------------------------
#
#       Run Function
#
# -------------------------------------

def run():
    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = Camera_Framer(parent=mbr_util_get_maya_window())
    MAIN_WINDOW.show()