# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

from TOS_Pipeline.src.dcc.maya.utils.qt_compat import wdg, core, gui
from TOS_Pipeline.src.dcc.maya.utils.qt_utils import mbr_util_get_maya_window
from TOS_Pipeline.src.dcc.maya.utils.qt_helpers import *
from TOS_Pipeline.src.dcc.maya.utils.maya_utils import *

from TOS_Pipeline.src.core.fs_utils import *
from TOS_Pipeline.src.core.naming import *

from TOS_Pipeline.src.dcc.maya.animation.engine.ikfk_matcher_engine import *

import maya.cmds as cmds
from maya.api import OpenMaya as om

# -------------------------------------
#
#       Global Variables
#
# -------------------------------------

MAIN_WINDOW = None
__VERSION__ = '1.2'

# -------------------------------------
#
#       Main Class
#
# -------------------------------------

class tos_ikfk_matcher_window(wdg.QMainWindow):

    def __init__(self, parent=None):
        super(tos_ikfk_matcher_window, self).__init__(parent)

        # -------------------------------------
        #
        #       Window Title and Size
        #
        # -------------------------------------

        self.setWindowTitle(f"TOS IKFK Matcher {__VERSION__}")
        self.setFocusPolicy(core.Qt.ClickFocus)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = 560

        self.resize(550, initial_height)
        self.setMinimumSize(550, min(initial_height, int(screen_height * 0.5)))

        # -------------------------------------
        #
        #       Menu Bar
        #
        # -------------------------------------

        menubar = self.menuBar()

        help_menu = menubar.addMenu('Help')
        settings_menu = menubar.addMenu('Settings')

        help_action = gui.QAction('Go to pipeline-help channel in Slack', self)
        help_menu.addAction(help_action)

        self.refresh_action = gui.QAction('Refresh', self)
        settings_menu.addAction(self.refresh_action)

        # -------------------------------------
        #
        #       Widget Variables
        #
        # -------------------------------------

        self.title_frame = None
        self.title_label = None
        self.project_frame = None
        self.project_label = None

        self.namespace_combo = None

        self.body_part_label = None
        self.current_label = None
        self.new_label = None
        self.rt_arm_check = None
        self.rt_arm_current_btn = None
        self.rt_arm_new_btn = None
        self.lf_arm_check = None
        self.lf_arm_current_btn = None
        self.lf_arm_new_btn = None
        self.rt_leg_check = None
        self.rt_leg_current_btn = None
        self.rt_leg_new_btn = None
        self.lf_leg_check = None
        self.lf_leg_current_btn = None
        self.lf_leg_new_btn = None

        self.check_group = None

        self.match_pose_btn = None
        self.match_anim_btn = None
        self.pose_radial_btn = None
        self.anim_radial_btn = None
        self.timeline_left_le = None
        self.timeline_right_le = None

        # -------------------------------------
        #
        #       Initialization Variables
        #
        # -------------------------------------

        self.btn_width = 35
        self.btn_height = 25

        self.namespaces_list = mbr_util_get_namespaces()

        self.callback_id = om.MEventMessage.addEventCallback(
            'SelectionChanged',
            self.on_selection_changed
        )

        self.selected_namespace = None

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

        self.btn_disabled_style = """
            QPushButton,
            QPushButton:hover,
            QPushButton:pressed,
            QPushButton:checked,
            QPushButton:default,
            QPushButton:focus {
                background-color: #3b3b3b;
                color: #737373;
                border: none;
            }
            """

        self.btn_enabled_style = """
            QPushButton,
            QPushButton:hover,
            QPushButton:pressed,
            QPushButton:checked,
            QPushButton:default,
            QPushButton:focus {
                background-color: #4b4b4b;
                color: #ffffff;
                border: none;
            }
            """

        self.match_btn_style = """
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
        self.title_frame.setStyleSheet("background-color: #1c0029")

        # Title Label
        self.title_label = wdg.QLabel('IK/FK Matcher')
        self.title_label.setStyleSheet("font-size: 25px; color: #ffffff; font-weight: bold; font-style: italic")
        self.title_label.setAlignment(core.Qt.AlignCenter)

        # The Other Side Frame
        self.project_frame = wdg.QFrame()
        self.project_frame.setStyleSheet("background-color: #ffffff")

        # The Other Side Label
        self.project_label = wdg.QLabel('The Other Side')
        self.project_label.setStyleSheet('font-size: 20px; color: #1c0029; font-weight: bold')
        self.project_label.setAlignment(core.Qt.AlignCenter)

        # -------------------------------------
        #
        #       Top Widgets
        #
        # -------------------------------------

        # Namespace Combo Box
        self.namespace_combo = wdg.QComboBox()
        self.namespace_combo.addItems(self.namespaces_list)
        if 'JOHNHEALTHY' in self.namespaces_list:
            self.namespace_combo.setCurrentText('JOHNHEALTHY')

        # -------------------------------------
        #
        #       Limb Selection Widgets
        #
        # -------------------------------------

        # Body Part Label
        self.body_part_label = wdg.QLabel('Body Part')

        # Current Label
        self.current_label = wdg.QLabel('Current')

        # New Label
        self.new_label = wdg.QLabel('New')

        # Right Arm Checkbox
        self.rt_arm_check = wdg.QCheckBox('Right Arm')
        self.rt_arm_check.setStyleSheet("color: #ff8a8a;")
        self.rt_arm_check.setAutoExclusive(False)

        # Right Arm Current Combo Box
        self.rt_arm_current_btn = wdg.QPushButton('FK')
        self.rt_arm_current_btn.setFixedWidth(self.btn_width)
        self.rt_arm_current_btn.setFixedHeight(self.btn_height)

        # Right Arm New Combo Box
        self.rt_arm_new_btn = wdg.QPushButton('FK')
        self.rt_arm_new_btn.setFixedWidth(self.btn_width)
        self.rt_arm_new_btn.setFixedHeight(self.btn_height)

        # Left Arm Checkbox
        self.lf_arm_check = wdg.QCheckBox('Left Arm')
        self.lf_arm_check.setStyleSheet("color: #76c4ff;")
        self.lf_arm_check.setAutoExclusive(False)

        # Left Arm Current Combo Box
        self.lf_arm_current_btn = wdg.QPushButton('FK')
        self.lf_arm_current_btn.setFixedWidth(self.btn_width)
        self.lf_arm_current_btn.setFixedHeight(self.btn_height)

        # Left Arm New Combo Box
        self.lf_arm_new_btn = wdg.QPushButton('FK')
        self.lf_arm_new_btn.setFixedWidth(self.btn_width)
        self.lf_arm_new_btn.setFixedHeight(self.btn_height)

        # Right Leg Checkbox
        self.rt_leg_check = wdg.QCheckBox('Right Leg')
        self.rt_leg_check.setStyleSheet("color: #ff8a8a;")
        self.rt_leg_check.setAutoExclusive(False)

        # Right Arm Current Combo Box
        self.rt_leg_current_btn = wdg.QPushButton('FK')
        self.rt_leg_current_btn.setFixedWidth(self.btn_width)
        self.rt_leg_current_btn.setFixedHeight(self.btn_height)

        # Right Arm New Combo Box
        self.rt_leg_new_btn = wdg.QPushButton('FK')
        self.rt_leg_new_btn.setFixedWidth(self.btn_width)
        self.rt_leg_new_btn.setFixedHeight(self.btn_height)

        # Left Leg Checkbox
        self.lf_leg_check = wdg.QCheckBox('Left Leg')
        self.lf_leg_check.setStyleSheet("color: #76c4ff;")
        self.lf_leg_check.setAutoExclusive(False)

        # Right Arm Current Combo Box
        self.lf_leg_current_btn = wdg.QPushButton('FK')
        self.lf_leg_current_btn.setFixedWidth(self.btn_width)
        self.lf_leg_current_btn.setFixedHeight(self.btn_height)

        # Right Arm New Combo Box
        self.lf_leg_new_btn = wdg.QPushButton('FK')
        self.lf_leg_new_btn.setFixedWidth(self.btn_width)
        self.lf_leg_new_btn.setFixedHeight(self.btn_height)

        # Check Group
        self.check_group = wdg.QButtonGroup()
        self.check_group.setExclusive(True)
        self.check_group.addButton(self.rt_arm_check)
        self.check_group.addButton(self.lf_arm_check)
        self.check_group.addButton(self.rt_leg_check)
        self.check_group.addButton(self.lf_leg_check)

        # -------------------------------------
        #
        #       Match Buttons Widgets
        #
        # -------------------------------------

        # Match Pose Button
        self.match_pose_btn = wdg.QPushButton('MATCH\nPOSE')
        self.match_pose_btn.setFixedWidth(180)
        self.match_pose_btn.setFixedHeight(150)
        self.match_pose_btn.setStyleSheet(self.match_btn_style)

        # Match Animation Button
        self.match_anim_btn = wdg.QPushButton('MATCH\nANIM')
        self.match_anim_btn.setFixedWidth(180)
        self.match_anim_btn.setFixedHeight(150)
        self.match_anim_btn.setStyleSheet(self.match_btn_style)

        # -------------------------------------
        #
        #       Extra Options Widgets
        #
        # -------------------------------------

        # Pose Radial Button
        self.pose_radial_btn = wdg.QRadioButton('Pose')

        # Animation Radial Button
        self.anim_radial_btn = wdg.QRadioButton('Animation')

        # Timeline Left
        self.timeline_left_le = wdg.QLineEdit()
        self.timeline_left_le.setFixedWidth(80)

        # Timeline Right
        self.timeline_right_le = wdg.QLineEdit()
        self.timeline_right_le.setFixedWidth(80)

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
        main_lyt.setContentsMargins(40, 30, 40, 0)

        # -------------------------------------
        #
        #       Title Layout
        #
        # -------------------------------------

        title_frame_lyt = wdg.QVBoxLayout()

        title_lyt = wdg.QVBoxLayout(self.title_frame)
        title_lyt.setAlignment(core.Qt.AlignCenter)

        # Project Layout
        project_frame_lyt = wdg.QVBoxLayout()

        project_lyt = wdg.QVBoxLayout(self.project_frame)
        project_lyt.setAlignment(core.Qt.AlignCenter)

        # -------------------------------------
        #
        #       Body Layout
        #
        # -------------------------------------

        # Body Layout
        body_lyt = wdg.QHBoxLayout()
        body_lyt.setContentsMargins(0, 20, 0, 0)

        # -------------------------------------
        #
        #       Left Layout
        #
        # -------------------------------------

        # Left Layout
        left_lyt = wdg.QVBoxLayout()

        # Namespace Group
        namespace_grp = wdg.QGroupBox('Namespace')
        namespace_lyt = wdg.QHBoxLayout()
        namespace_grp.setLayout(namespace_lyt)

        namespace_grp.setStyleSheet(self.group_boxes_style)

        # Limb Selection Group
        limb_selection_grp = wdg.QGroupBox('Limb Selection')
        limb_selection_lyt = wdg.QGridLayout()
        limb_selection_lyt.setAlignment(core.Qt.AlignLeft)
        limb_selection_lyt.setHorizontalSpacing(30)
        limb_selection_grp.setLayout(limb_selection_lyt)

        limb_selection_grp.setStyleSheet(self.group_boxes_style)

        # -------------------------------------
        #
        #       Right Layout
        #
        # -------------------------------------

        # Right Layout
        right_lyt = wdg.QVBoxLayout()
        right_lyt.setAlignment(core.Qt.AlignTop)
        right_lyt.setContentsMargins(10, 20, 0, 0)

        # Match Button Layout
        match_lyt = wdg.QVBoxLayout()

        # Match Options Layout
        options_lyt = wdg.QVBoxLayout()

        # Timeline Layout
        timeline_lyt = wdg.QHBoxLayout()
        timeline_lyt.setAlignment(core.Qt.AlignLeft)

        # -------------------------------------
        #
        #       Layout Arrangement
        #
        # -------------------------------------

        main_lyt.addLayout(title_frame_lyt)
        main_lyt.addLayout(project_frame_lyt)
        main_lyt.addLayout(body_lyt)

        body_lyt.addLayout(left_lyt)
        body_lyt.addLayout(right_lyt)

        left_lyt.addWidget(namespace_grp)
        left_lyt.addWidget(limb_selection_grp)

        left_lyt.addLayout(options_lyt)
        left_lyt.addLayout(timeline_lyt)
        right_lyt.addLayout(match_lyt)

        # -------------------------------------
        #
        #       Widgets Arrangement
        #
        # -------------------------------------

        title_frame_lyt.addWidget(self.title_frame)
        title_lyt.addWidget(self.title_label)
        project_frame_lyt.addWidget(self.project_frame)
        project_lyt.addWidget(self.project_label)

        namespace_lyt.addWidget(self.namespace_combo)

        limb_selection_lyt.addWidget(self.body_part_label, 0, 0)
        limb_selection_lyt.addWidget(self.current_label, 0, 1)
        limb_selection_lyt.addWidget(self.new_label, 0, 2)

        limb_selection_lyt.addWidget(self.rt_arm_check, 1, 0)
        limb_selection_lyt.addWidget(self.rt_arm_current_btn, 1, 1)
        limb_selection_lyt.addWidget(self.rt_arm_new_btn, 1, 2)

        limb_selection_lyt.addWidget(self.lf_arm_check, 2, 0)
        limb_selection_lyt.addWidget(self.lf_arm_current_btn, 2, 1)
        limb_selection_lyt.addWidget(self.lf_arm_new_btn, 2, 2)

        limb_selection_lyt.addWidget(self.rt_leg_check, 3, 0)
        limb_selection_lyt.addWidget(self.rt_leg_current_btn, 3, 1)
        limb_selection_lyt.addWidget(self.rt_leg_new_btn, 3, 2)

        limb_selection_lyt.addWidget(self.lf_leg_check, 4, 0)
        limb_selection_lyt.addWidget(self.lf_leg_current_btn, 4, 1)
        limb_selection_lyt.addWidget(self.lf_leg_new_btn, 4, 2)

        match_lyt.addWidget(self.match_pose_btn)
        match_lyt.addWidget(self.match_anim_btn)
        options_lyt.addWidget(self.pose_radial_btn)
        options_lyt.addWidget(self.anim_radial_btn)
        timeline_lyt.addWidget(self.timeline_left_le)
        timeline_lyt.addWidget(self.timeline_right_le)

    # -------------------------------------
    #
    #       Create Connections
    #
    # -------------------------------------

    def create_connections(self):

        self.refresh_action.triggered.connect(self.refresh_action_triggered)

        self.namespace_combo.currentIndexChanged.connect(self.namespace_combo_changed)

        self.check_group.buttonClicked.connect(self.check_group_btn_clicked)

        self.pose_radial_btn.clicked.connect(self.pose_radial_btn_clicked)
        self.anim_radial_btn.clicked.connect(self.anim_radial_btn_clicked)

        self.match_pose_btn.clicked.connect(self.match_pose_btn_clicked)
        self.match_anim_btn.clicked.connect(self.match_anim_btn_clicked)

    # -------------------------------------
    #
    #       Set Defaults
    #
    # -------------------------------------

    def set_defaults(self):

        # Disable Buttons
        self.rt_arm_current_btn.setStyleSheet(self.btn_disabled_style)
        self.rt_arm_new_btn.setStyleSheet(self.btn_disabled_style)

        self.lf_arm_current_btn.setStyleSheet(self.btn_disabled_style)
        self.lf_arm_new_btn.setStyleSheet(self.btn_disabled_style)

        self.rt_leg_current_btn.setStyleSheet(self.btn_disabled_style)
        self.rt_leg_new_btn.setStyleSheet(self.btn_disabled_style)

        self.lf_leg_current_btn.setStyleSheet(self.btn_disabled_style)
        self.lf_leg_new_btn.setStyleSheet(self.btn_disabled_style)

        # Changing Buttons text based on rig's setup
        self.selected_namespace = self.namespace_combo.currentText()

        if self.selected_namespace == 'JOHNHEALTHY':
            rt_arm_setup = cmds.getAttr(f"{self.selected_namespace}:r_hand_switch_ctrl.IkFk")
            lf_arm_setup = cmds.getAttr(f"{self.selected_namespace}:l_hand_switch_ctrl.IkFk")
            rt_leg_setup = cmds.getAttr(f"{self.selected_namespace}:r_ankle_switch_ctrl.IkFk")
            lf_leg_setup = cmds.getAttr(f"{self.selected_namespace}:l_ankle_switch_ctrl.IkFk")

            if rt_arm_setup == 1.0:
                self.rt_arm_current_btn.setText('FK')
            else:
                self.rt_arm_current_btn.setText('IK')

            if lf_arm_setup == 1.0:
                self.lf_arm_current_btn.setText('FK')
            else:
                self.lf_arm_current_btn.setText('IK')

            if rt_leg_setup == 1.0:
                self.rt_leg_current_btn.setText('FK')
            else:
                self.rt_leg_current_btn.setText('IK')

            if lf_leg_setup == 1.0:
                self.lf_leg_current_btn.setText('FK')
            else:
                self.lf_leg_current_btn.setText('IK')

            # Switch Buttons to the opposite
            if self.rt_arm_current_btn.text() == 'FK':
                self.rt_arm_new_btn.setText('IK')
            else:
                self.rt_arm_new_btn.setText('FK')

            if self.lf_arm_current_btn.text() == 'FK':
                self.lf_arm_new_btn.setText('IK')
            else:
                self.lf_arm_new_btn.setText('FK')

            if self.rt_leg_current_btn.text() == 'FK':
                self.rt_leg_new_btn.setText('IK')
            else:
                self.rt_leg_new_btn.setText('FK')

            if self.lf_leg_current_btn.text() == 'FK':
                self.lf_leg_new_btn.setText('IK')
            else:
                self.lf_leg_new_btn.setText('FK')

        else:
            wdg.QMessageBox.critical(self, 'Error', 'John Healthy namespace needs to match "JOHNHEALTHY"')
            return

        # Check default checkbox
        self.rt_arm_check.setChecked(True)
        self.rt_arm_current_btn.setStyleSheet(self.btn_enabled_style)
        self.rt_arm_new_btn.setStyleSheet(self.btn_enabled_style)

        # Set default to Pose
        self.pose_radial_btn.setChecked(True)
        self.match_anim_btn.setEnabled(False)

        self.timeline_left_le.setReadOnly(True)
        self.timeline_left_le.setStyleSheet("QLineEdit {background-color: #3d3d3d;}")

        self.timeline_right_le.setReadOnly(True)
        self.timeline_right_le.setStyleSheet("QLineEdit {background-color: #3d3d3d;}")

        # Match Anim default style
        self.match_anim_btn.setStyleSheet("""
            QPushButton {
                font-style: italic;
                font-weight: bold;
                font-size: 30px;
            }
        """)

    # -------------------------------------
    #
    #       Widget Signals
    #
    # -------------------------------------

    def refresh_action_triggered(self):

        # Changing Buttons text based on rig's setup
        self.selected_namespace = self.namespace_combo.currentText()

        rt_arm_setup = cmds.getAttr(f"{self.selected_namespace}:r_hand_switch_ctrl.IkFk")
        lf_arm_setup = cmds.getAttr(f"{self.selected_namespace}:l_hand_switch_ctrl.IkFk")
        rt_leg_setup = cmds.getAttr(f"{self.selected_namespace}:r_ankle_switch_ctrl.IkFk")
        lf_leg_setup = cmds.getAttr(f"{self.selected_namespace}:l_ankle_switch_ctrl.IkFk")

        if rt_arm_setup == 1.0:
            self.rt_arm_current_btn.setText('FK')
        else:
            self.rt_arm_current_btn.setText('IK')

        if lf_arm_setup == 1.0:
            self.lf_arm_current_btn.setText('FK')
        else:
            self.lf_arm_current_btn.setText('IK')

        if rt_leg_setup == 1.0:
            self.rt_leg_current_btn.setText('FK')
        else:
            self.rt_leg_current_btn.setText('IK')

        if lf_leg_setup == 1.0:
            self.lf_leg_current_btn.setText('FK')
        else:
            self.lf_leg_current_btn.setText('IK')

        # Switch Buttons to the opposite
        if self.rt_arm_current_btn.text() == 'FK':
            self.rt_arm_new_btn.setText('IK')
        else:
            self.rt_arm_new_btn.setText('FK')

        if self.lf_arm_current_btn.text() == 'FK':
            self.lf_arm_new_btn.setText('IK')
        else:
            self.lf_arm_new_btn.setText('FK')

        if self.rt_leg_current_btn.text() == 'FK':
            self.rt_leg_new_btn.setText('IK')
        else:
            self.rt_leg_new_btn.setText('FK')

        if self.lf_leg_current_btn.text() == 'FK':
            self.lf_leg_new_btn.setText('IK')
        else:
            self.lf_leg_new_btn.setText('FK')

    def namespace_combo_changed(self):

        # Changing Buttons text based on rig's setup
        self.selected_namespace = self.namespace_combo.currentText()

        rt_arm_setup = cmds.getAttr(f"{self.selected_namespace}:r_hand_switch_ctrl.IkFk")
        lf_arm_setup = cmds.getAttr(f"{self.selected_namespace}:l_hand_switch_ctrl.IkFk")
        rt_leg_setup = cmds.getAttr(f"{self.selected_namespace}:r_ankle_switch_ctrl.IkFk")
        lf_leg_setup = cmds.getAttr(f"{self.selected_namespace}:l_ankle_switch_ctrl.IkFk")

        if rt_arm_setup == 1.0:
            self.rt_arm_current_btn.setText('FK')
        else:
            self.rt_arm_current_btn.setText('IK')

        if lf_arm_setup == 1.0:
            self.lf_arm_current_btn.setText('FK')
        else:
            self.lf_arm_current_btn.setText('IK')

        if rt_leg_setup == 1.0:
            self.rt_leg_current_btn.setText('FK')
        else:
            self.rt_leg_current_btn.setText('IK')

        if lf_leg_setup == 1.0:
            self.lf_leg_current_btn.setText('FK')
        else:
            self.lf_leg_current_btn.setText('IK')

        # Switch Buttons to the opposite
        if self.rt_arm_current_btn.text() == 'FK':
            self.rt_arm_new_btn.setText('IK')
        else:
            self.rt_arm_new_btn.setText('FK')

        if self.lf_arm_current_btn.text() == 'FK':
            self.lf_arm_new_btn.setText('IK')
        else:
            self.lf_arm_new_btn.setText('FK')

        if self.rt_leg_current_btn.text() == 'FK':
            self.rt_leg_new_btn.setText('IK')
        else:
            self.rt_leg_new_btn.setText('FK')

        if self.lf_leg_current_btn.text() == 'FK':
            self.lf_leg_new_btn.setText('IK')
        else:
            self.lf_leg_new_btn.setText('FK')

    def check_group_btn_clicked(self, button):

        if button is self.rt_arm_check:
            self.rt_arm_current_btn.setStyleSheet(self.btn_enabled_style)
            self.rt_arm_new_btn.setStyleSheet(self.btn_enabled_style)

            self.lf_arm_current_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_arm_new_btn.setStyleSheet(self.btn_disabled_style)
            self.rt_leg_current_btn.setStyleSheet(self.btn_disabled_style)
            self.rt_leg_new_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_leg_current_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_leg_new_btn.setStyleSheet(self.btn_disabled_style)

        elif button is self.lf_arm_check:
            self.lf_arm_current_btn.setStyleSheet(self.btn_enabled_style)
            self.lf_arm_new_btn.setStyleSheet(self.btn_enabled_style)

            self.rt_arm_current_btn.setStyleSheet(self.btn_disabled_style)
            self.rt_arm_new_btn.setStyleSheet(self.btn_disabled_style)
            self.rt_leg_current_btn.setStyleSheet(self.btn_disabled_style)
            self.rt_leg_new_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_leg_current_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_leg_new_btn.setStyleSheet(self.btn_disabled_style)

        elif button is self.rt_leg_check:
            self.rt_leg_current_btn.setStyleSheet(self.btn_enabled_style)
            self.rt_leg_new_btn.setStyleSheet(self.btn_enabled_style)

            self.rt_arm_current_btn.setStyleSheet(self.btn_disabled_style)
            self.rt_arm_new_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_arm_current_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_arm_new_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_leg_current_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_leg_new_btn.setStyleSheet(self.btn_disabled_style)

        elif button is self.lf_leg_check:
            self.lf_leg_current_btn.setStyleSheet(self.btn_enabled_style)
            self.lf_leg_new_btn.setStyleSheet(self.btn_enabled_style)

            self.rt_arm_current_btn.setStyleSheet(self.btn_disabled_style)
            self.rt_arm_new_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_arm_current_btn.setStyleSheet(self.btn_disabled_style)
            self.lf_arm_new_btn.setStyleSheet(self.btn_disabled_style)
            self.rt_leg_current_btn.setStyleSheet(self.btn_disabled_style)
            self.rt_leg_new_btn.setStyleSheet(self.btn_disabled_style)

    def pose_radial_btn_clicked(self):

        self.match_pose_btn.setEnabled(True)
        self.match_anim_btn.setEnabled(False)

        self.match_pose_btn.setStyleSheet(self.match_btn_style)
        self.match_anim_btn.setStyleSheet("""
            QPushButton {
                font-style: italic;
                font-weight: bold;
                font-size: 30px;
            }
        """)

        self.timeline_left_le.clear()
        self.timeline_left_le.setReadOnly(True)
        self.timeline_left_le.setStyleSheet("QLineEdit {background-color: #3d3d3d;}")

        self.timeline_right_le.clear()
        self.timeline_right_le.setReadOnly(True)
        self.timeline_right_le.setStyleSheet("QLineEdit {background-color: #3d3d3d;}")

    def anim_radial_btn_clicked(self):

        self.match_pose_btn.setEnabled(False)
        self.match_anim_btn.setEnabled(True)

        self.match_anim_btn.setStyleSheet(self.match_btn_style)
        self.match_pose_btn.setStyleSheet("""
            QPushButton {
                font-style: italic;
                font-weight: bold;
                font-size: 30px;
            }
        """)

        self.timeline_left_le.setReadOnly(False)
        self.timeline_left_le.setStyleSheet("")

        self.timeline_right_le.setReadOnly(False)
        self.timeline_right_le.setStyleSheet("")

        timeline_start = int(cmds.playbackOptions(q=True, min=True))
        timeline_end = int(cmds.playbackOptions(q=True, max=True))

        self.timeline_left_le.setText(str(timeline_start))
        self.timeline_right_le.setText(str(timeline_end))

    def match_pose_btn_clicked(self):

        current_btn_checked = self.check_group.checkedButton().text()
        self.selected_namespace = self.namespace_combo.currentText()

        # Identifies the current setup for the selected limb
        if current_btn_checked == 'Right Arm':
            current_setup = self.rt_arm_current_btn.text()

        elif current_btn_checked == 'Left Arm':
            current_setup = self.lf_arm_current_btn.text()

        elif current_btn_checked == 'Right Leg':
            current_setup = self.rt_leg_current_btn.text()

        elif current_btn_checked == 'Left Leg':
            current_setup = self.lf_leg_current_btn.text()

        # Apply the snap function depending on the user selection
        if current_setup == 'IK':
            if self.rt_arm_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Arm'
                side_var = 'Right'
                # pose_ik_fk_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_pose_ik_fk_snap(self.selected_namespace, limb_var, side_var)

            elif self.lf_arm_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Arm'
                side_var = 'Left'
                # pose_ik_fk_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_pose_ik_fk_snap(self.selected_namespace, limb_var, side_var)

            elif self.rt_leg_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Leg'
                side_var = 'Right'
                # pose_ik_fk_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_pose_ik_fk_snap(self.selected_namespace, limb_var, side_var)

            elif self.lf_leg_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Leg'
                side_var = 'Left'
                # pose_ik_fk_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_pose_ik_fk_snap(self.selected_namespace, limb_var, side_var)

        else:
            if self.rt_arm_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Arm'
                side_var = 'Right'
                # pose_fk_ik_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_pose_fk_ik_snap(self.selected_namespace, limb_var, side_var)

            elif self.lf_arm_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Arm'
                side_var = 'Left'
                # pose_fk_ik_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_pose_fk_ik_snap(self.selected_namespace, limb_var, side_var)

            elif self.rt_leg_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Leg'
                side_var = 'Right'
                # pose_fk_ik_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_pose_fk_ik_snap(self.selected_namespace, limb_var, side_var)

            elif self.lf_leg_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Leg'
                side_var = 'Left'
                # pose_fk_ik_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_pose_fk_ik_snap(self.selected_namespace, limb_var, side_var)


        # Changing Buttons text based on rig's setup
        self.selected_namespace = self.namespace_combo.currentText()

        rt_arm_setup = cmds.getAttr(f"{self.selected_namespace}:r_hand_switch_ctrl.IkFk")
        lf_arm_setup = cmds.getAttr(f"{self.selected_namespace}:l_hand_switch_ctrl.IkFk")
        rt_leg_setup = cmds.getAttr(f"{self.selected_namespace}:r_ankle_switch_ctrl.IkFk")
        lf_leg_setup = cmds.getAttr(f"{self.selected_namespace}:l_ankle_switch_ctrl.IkFk")

        if rt_arm_setup == 1.0:
            self.rt_arm_current_btn.setText('FK')
        else:
            self.rt_arm_current_btn.setText('IK')

        if lf_arm_setup == 1.0:
            self.lf_arm_current_btn.setText('FK')
        else:
            self.lf_arm_current_btn.setText('IK')

        if rt_leg_setup == 1.0:
            self.rt_leg_current_btn.setText('FK')
        else:
            self.rt_leg_current_btn.setText('IK')

        if lf_leg_setup == 1.0:
            self.lf_leg_current_btn.setText('FK')
        else:
            self.lf_leg_current_btn.setText('IK')

        # Switch Buttons to the opposite
        if self.rt_arm_current_btn.text() == 'FK':
            self.rt_arm_new_btn.setText('IK')
        else:
            self.rt_arm_new_btn.setText('FK')

        if self.lf_arm_current_btn.text() == 'FK':
            self.lf_arm_new_btn.setText('IK')
        else:
            self.lf_arm_new_btn.setText('FK')

        if self.rt_leg_current_btn.text() == 'FK':
            self.rt_leg_new_btn.setText('IK')
        else:
            self.rt_leg_new_btn.setText('FK')

        if self.lf_leg_current_btn.text() == 'FK':
            self.lf_leg_new_btn.setText('IK')
        else:
            self.lf_leg_new_btn.setText('FK')

    def match_anim_btn_clicked(self):
        current_btn_checked = self.check_group.checkedButton().text()
        self.selected_namespace = self.namespace_combo.currentText()

        # Identifies the current setup for the selected limb
        if current_btn_checked == 'Right Arm':
            current_setup = self.rt_arm_current_btn.text()

        elif current_btn_checked == 'Left Arm':
            current_setup = self.lf_arm_current_btn.text()

        elif current_btn_checked == 'Right Leg':
            current_setup = self.rt_leg_current_btn.text()

        elif current_btn_checked == 'Left Leg':
            current_setup = self.lf_leg_current_btn.text()

        # Apply the snap function depending on the user selection
        if current_setup == 'IK':
            if self.rt_arm_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Arm'
                side_var = 'Right'
                # anim_ik_fk_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_anim_ik_fk_snap(self.selected_namespace, limb_var, side_var)

            elif self.lf_arm_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Arm'
                side_var = 'Left'
                # anim_ik_fk_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_anim_ik_fk_snap(self.selected_namespace, limb_var, side_var)

            elif self.rt_leg_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Leg'
                side_var = 'Right'
                # anim_ik_fk_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_anim_ik_fk_snap(self.selected_namespace, limb_var, side_var)

            elif self.lf_leg_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Leg'
                side_var = 'Left'
                # anim_ik_fk_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_anim_ik_fk_snap(self.selected_namespace, limb_var, side_var)

        else:
            if self.rt_arm_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Arm'
                side_var = 'Right'
                # anim_fk_ik_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_anim_fk_ik_snap(self.selected_namespace, limb_var, side_var)

            elif self.lf_arm_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Arm'
                side_var = 'Left'
                # anim_fk_ik_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_anim_fk_ik_snap(self.selected_namespace, limb_var, side_var)

            elif self.rt_leg_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Leg'
                side_var = 'Right'
                # anim_fk_ik_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_anim_fk_ik_snap(self.selected_namespace, limb_var, side_var)

            elif self.lf_leg_check.isChecked():
                cmds.select(f"{self.selected_namespace}:origin_ctrl", r=True)
                limb_var = 'Leg'
                side_var = 'Left'
                # anim_fk_ik_snap(self.selected_namespace, limb_var, side_var)
                mbr_egn_anim_fk_ik_snap(self.selected_namespace, limb_var, side_var)

        # Changing Buttons text based on rig's setup
        self.selected_namespace = self.namespace_combo.currentText()

        rt_arm_setup = cmds.getAttr(f"{self.selected_namespace}:r_hand_switch_ctrl.IkFk")
        lf_arm_setup = cmds.getAttr(f"{self.selected_namespace}:l_hand_switch_ctrl.IkFk")
        rt_leg_setup = cmds.getAttr(f"{self.selected_namespace}:r_ankle_switch_ctrl.IkFk")
        lf_leg_setup = cmds.getAttr(f"{self.selected_namespace}:l_ankle_switch_ctrl.IkFk")

        if rt_arm_setup == 1.0:
            self.rt_arm_current_btn.setText('FK')
        else:
            self.rt_arm_current_btn.setText('IK')

        if lf_arm_setup == 1.0:
            self.lf_arm_current_btn.setText('FK')
        else:
            self.lf_arm_current_btn.setText('IK')

        if rt_leg_setup == 1.0:
            self.rt_leg_current_btn.setText('FK')
        else:
            self.rt_leg_current_btn.setText('IK')

        if lf_leg_setup == 1.0:
            self.lf_leg_current_btn.setText('FK')
        else:
            self.lf_leg_current_btn.setText('IK')

        # Switch Buttons to the opposite
        if self.rt_arm_current_btn.text() == 'FK':
            self.rt_arm_new_btn.setText('IK')
        else:
            self.rt_arm_new_btn.setText('FK')

        if self.lf_arm_current_btn.text() == 'FK':
            self.lf_arm_new_btn.setText('IK')
        else:
            self.lf_arm_new_btn.setText('FK')

        if self.rt_leg_current_btn.text() == 'FK':
            self.rt_leg_new_btn.setText('IK')
        else:
            self.rt_leg_new_btn.setText('FK')

        if self.lf_leg_current_btn.text() == 'FK':
            self.lf_leg_new_btn.setText('IK')
        else:
            self.lf_leg_new_btn.setText('FK')

    # -------------------------------------
    #
    #       Utility Methods
    #
    # -------------------------------------

    def on_selection_changed(self, *args):
        self.update_ui()

    def update_ui(self):
        sel = cmds.ls(sl=True)[0]
        upper_limbs_names = ['upperarm', 'lowerarm', 'hand']
        lower_limbs_names = ['thigh', 'knee', 'ankle']

        rt_arm_setup = cmds.getAttr(f"{self.selected_namespace}:r_hand_switch_ctrl.IkFk")
        lf_arm_setup = cmds.getAttr(f"{self.selected_namespace}:l_hand_switch_ctrl.IkFk")
        rt_leg_setup = cmds.getAttr(f"{self.selected_namespace}:r_ankle_switch_ctrl.IkFk")
        lf_leg_setup = cmds.getAttr(f"{self.selected_namespace}:l_ankle_switch_ctrl.IkFk")

        if ':r_' in sel:
            if any(name in sel for name in upper_limbs_names):
                if rt_arm_setup == 1.0:
                    self.rt_arm_current_btn.setText('FK')
                else:
                    self.rt_arm_current_btn.setText('IK')

                if self.rt_arm_current_btn.text() == 'FK':
                    self.rt_arm_new_btn.setText('IK')
                else:
                    self.rt_arm_new_btn.setText('FK')

            elif any(name in sel for name in lower_limbs_names):
                if rt_leg_setup == 1.0:
                    self.rt_leg_current_btn.setText('FK')
                else:
                    self.rt_leg_current_btn.setText('IK')

                if self.rt_leg_current_btn.text() == 'FK':
                    self.rt_leg_new_btn.setText('IK')
                else:
                    self.rt_leg_new_btn.setText('FK')

            else:
                print('no valid control')

        elif ':l_' in sel:
            if any(name in sel for name in upper_limbs_names):
                if lf_arm_setup == 1.0:
                    self.lf_arm_current_btn.setText('FK')
                else:
                    self.lf_arm_current_btn.setText('IK')
                if self.lf_arm_current_btn.text() == 'FK':
                    self.lf_arm_new_btn.setText('IK')
                else:
                    self.lf_arm_new_btn.setText('FK')

            elif any(name in sel for name in lower_limbs_names):
                if lf_leg_setup == 1.0:
                    self.lf_leg_current_btn.setText('FK')
                else:
                    self.lf_leg_current_btn.setText('IK')
                if self.lf_leg_current_btn.text() == 'FK':
                    self.lf_leg_new_btn.setText('IK')
                else:
                    self.lf_leg_new_btn.setText('FK')

            else:
                print('no valid control')

        else:
            print('no valid control')

    def close_event(self, event):
        om.MMessage.removeCallback(self.callback_id)
        super(tos_ikfk_matcher_window, self).closeEvent(event)

        if hasattr(self, 'callback_id') and self.callback_id:
            om.MMessage.removeCallback(self.callback_id)

        if hasattr(self, 'attr_callback') and self.attr_callback:
            om.MMessage.removeCallback(self.attr_callback)

        super(tos_ikfk_matcher_window, self).closeEvent(event)


# -------------------------------------
#
#       Run Function
#
# -------------------------------------

def run():

    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = tos_ikfk_matcher_window(parent=mbr_util_get_maya_window())
    MAIN_WINDOW.show()