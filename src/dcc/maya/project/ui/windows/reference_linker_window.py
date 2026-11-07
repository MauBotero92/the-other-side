# Import Modules
from PySide6 import QtWidgets as wdg
from PySide6 import QtCore as core
from PySide6 import QtGui as gui
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import os

############################
# VARIABLES
############################

MAIN_WINDOW = None
__version__ = '1.0'

assets_path = 'P:/The Other Side/Production/Assets'

# Camera Paths
camera_path = f"{assets_path}/Cam/NewCam_v5.ma"

# Chars Paths
danni_pregnant_path = f"{assets_path}/Chars/Danni_Pregnant/danni_pregnant_rig.ma"
danni_young_path = f"{assets_path}/Chars/Danni_Young/danni_young_rig,ma"
divine_being_path = f"{assets_path}/Chars/DivineBeing/DivineBeing_rig.ma"
doctor_female_path = f"{assets_path}/Chars/DoctorFemale_Hostpial_B/doctor_female_rig.ma"
eye_path = f"{assets_path}/Chars/Eye/eye_rig.ma"
john_healthy_path = f"{assets_path}/Chars/John_Healthy/johnHealthy_rig.ma"
john_sick_path = f"{assets_path}/Chars/John_Sick/sick_john_rig.ma"
tay_infant_path = f"{assets_path}/Chars/Tay_Infant/tay_infant_rig.ma"
tay_teen_path = f"{assets_path}/Chars/Tay_Teen/tay_teen_rig.ma"
tay_toddler_path = f"{assets_path}/Chars/Tay_Toddler/tay_toddler_rig.ma"

# Char Props Paths
backpack_apartment_tay_A_path = f"{assets_path}/CharProps/backpackApartmentTayA/backpackApartmentTayA.ma"
bed_hospital_A1_path = f"{assets_path}/CharProps/bedHospitalA/bedHospitalA1.ma"
bed_hospital_abyss_A1_path = f"{assets_path}/CharProps/bedHospitalAbyssA/bedHospitalAbyssA1.ma"
box_ring_wedding_A1_path = f"{assets_path}/CharProps/boxWeddingRingAbyssA/boxRingWeddingA1.ma"
brush_abyss_A1_path = f"{assets_path}/CharProps/brushAbyssA/brushAbyssA1.ma"
cap_abyss_A_path = f"{assets_path}/CharProps/capAbyssA/capAbyssA_Upload6.ma"
clipboard_A_path = f"{assets_path}/CharProps/clipboardA/clipboardA1.ma"
headphones_apartment_tay_A_path = f"{assets_path}/CharProps/headphonesApartmentTayA/headphonesApartmentTayA.ma"
light_hospital_A_path = f"{assets_path}/CharProps/lightHospitalA/lightHospitalA.ma"
picture_apartment_tay_A_path = f"{assets_path}/CharProps/pictureApartmentTayA/pictureApartmentTayA.ma"
ring_wedding_A1_path = f"{assets_path}/CharProps/ringWeddingA/ringWeddingA1.ma"
shopping_cart_seminary_A_path = f"{assets_path}/CharProps/shoppingcartSeminaryA/shoppingcartMillsA_v004.ma"
vanity_abyss_A_path = f"{assets_path}/CharProps/vanityAbyssA/vanityAbyssA.ma"

# Sets Paths
hospital_room_path = f"{assets_path}/Sets/Hospital Room/intRoomHospitalA1.ma"
spirit_world_path = f"{assets_path}/Sets/Spirit World/Maya/SpiritWorld_Set.ma"
train_platform_path = f"{assets_path}/Sets/Train Platform/Maya/TrainStation_Platform.ma"
train_station_path = f"{assets_path}/Sets/TrainStation/TrainStation_Set.mb"

# Vehicles Paths
train_proxy_path = f"{assets_path}/Vehicles/Train/train_proxy_rig.ma"
train_hires_path = f"{assets_path}/Vehicles/Train/train_rig.ma"


############################
# FUNCTIONS
############################

def get_maya_window():
    '''
    This function will get Maya Main Window and return it
    '''
    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    maya_main_window = wrapInstance(int(maya_main_window_ptr), wdg.QWidget)
    return maya_main_window


def list_folder_in_dir(directory):
    '''
    This function returns a list of the folders in a directory, except the last item
    '''
    # List all entries in the given directory
    entries = os.listdir(directory)

    # Filter out the entries that are directories
    folders = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]

    return folders


def list_files_in_dir(directory):
    '''
    This function returns a list of the files in a directory
    '''
    # List all entries in the given directory
    entries = os.listdir(directory)

    # Filter out the entries that are files
    files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]

    return files


#################################
# TOS REFERENCE LINKER CLASS
#################################

# Subclass of QLineEdit to avoid highlighting text space after finished editing
class Custom_Line_Edit(wdg.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # When user presses Enter
        self.returnPressed.connect(self.clearFocus)

    def focus_out_event(self, event):
        super().focus_out_event(event)
        # Remove Selection
        self.deselect()
        # Hide Cursor
        self.setCursorPosition(0)


# Main Class for the TOS Reference Linker
class TOS_Reference_Linker(wdg.QMainWindow):

    def __init__(self, parent=None):
        super(TOS_Reference_Linker, self).__init__(parent)

        # -------------------------------------
        # WINDOW TITLE AND SIZE
        # -------------------------------------

        self.setWindowTitle(f"Reference Linker {__version__}")
        self.setFixedSize(570, 800)
        self.setFocusPolicy(core.Qt.ClickFocus)

        # -------------------------------------
        # MENU BAR
        # -------------------------------------

        menubar = self.menuBar()

        help_menu = menubar.addMenu('Help')

        help_action = gui.QAction('Go to pipeline-help channel in Slack', self)
        help_menu.addAction(help_action)

        # -------------------------------------
        # VARIABLES HELPERS
        # -------------------------------------

        self.current_wks = cmds.workspace(q=True, rd=True)

        # List all reference nodes
        self.all_reference_nodes = cmds.ls(type='reference')
        self.real_reference_nodes = []
        self.unloaded_reference_nodes = []

        for ref in self.all_reference_nodes:
            # Skip Maya's internal shared reference node
            if ref == "sharedReferenceNode":
                continue
            # Skip nodes that are themselves inside a reference
            if cmds.referenceQuery(ref, isNodeReferenced=True):
                continue
            # Skip nodes that are not real reference nodes
            try:
                is_loaded = cmds.referenceQuery(ref, isLoaded=True)
            except RuntimeError:
                # Happens for sharedReferenceNode or corrupted references
                continue
            if not is_loaded:
                self.unloaded_reference_nodes.append(ref)

        # -------------------------------------
        # WIDGETS STYLES
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
        # INITIALIZATION
        # -------------------------------------

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.set_defaults()

    def create_widgets(self):

        # -------------------------------------
        # TITLE WIDGETS
        # -------------------------------------

        # Title Frame
        self.title_frame = wdg.QFrame()
        self.title_frame.setStyleSheet("background-color: #1c0029; border-radius: 6px;")

        # Title Label
        self.title_label = wdg.QLabel('Reference Linker')
        self.title_label.setStyleSheet("font-size: 25px; color: #ffffff; font-weight: bold; font-style: italic")
        self.title_label.setAlignment(core.Qt.AlignCenter)

        # The Other Side Frame
        self.project_frame = wdg.QFrame()
        self.project_frame.setStyleSheet("background-color: #ffffff")

        # The Other Side Label
        self.project_label = wdg.QLabel('The Other Side')
        self.project_label.setStyleSheet("font-size: 20px; color: #1c0029; font-weight: bold")
        self.project_label.setAlignment(core.Qt.AlignCenter)

        # -------------------------------------
        # TOP WIDGETS
        # -------------------------------------

        # Workspace LineEdit
        self.wks_read_le = wdg.QLineEdit()
        self.wks_read_le.setText(self.current_wks)
        self.wks_read_le.setStyleSheet("text-align: left; padding-left: 6px;")
        self.wks_read_le.setFixedWidth(400)
        self.wks_read_le.setFixedHeight(25)
        self.wks_read_le.setEnabled(False)

        # Set Project Button
        self.set_project_btn = wdg.QPushButton('...')
        self.set_project_btn.setFixedWidth(35)
        self.set_project_btn.setFixedHeight(25)

        # -------------------------------------
        # MIDDLE WIDGETS
        # -------------------------------------

        # Reference Nodes List
        self.reference_nodes_list = wdg.QListWidget()
        self.reference_nodes_list.addItems(self.unloaded_reference_nodes)
        self.reference_nodes_list.setFocusPolicy(core.Qt.NoFocus)

        # RePath Button
        self.repath_btn = wdg.QPushButton('REPATH\nNODE')
        self.repath_btn.setStyleSheet(self.btn_style)
        self.repath_btn.setFixedWidth(150)
        self.repath_btn.setFixedHeight(150)

        # -------------------------------------
        # BOTTOM WIDGETS
        # -------------------------------------

        # Current Namespace Line Edit
        self.current_nmp_le = Custom_Line_Edit()
        self.current_nmp_le.setEnabled(False)
        self.current_nmp_le.setFixedWidth(285)

        # New Namespace Line Edit
        self.new_nmp_le = Custom_Line_Edit()
        self.new_nmp_le.setFixedWidth(285)

        # Rename Buttom
        self.rename_btn = wdg.QPushButton('RENAME')
        self.rename_btn.setStyleSheet(self.btn_style)
        self.rename_btn.setFixedWidth(150)
        self.rename_btn.setFixedHeight(90)

    def create_layout(self):

        # -------------------------------------
        # CENTRAL WIDGET
        # -------------------------------------

        central_wdg = wdg.QWidget()
        self.setCentralWidget(central_wdg)

        # -------------------------------------
        # MAIN LAYOUT
        # -------------------------------------

        main_lyt = wdg.QVBoxLayout(central_wdg)
        main_lyt.setAlignment(core.Qt.AlignTop)
        main_lyt.setContentsMargins(40, 30, 40, 20)

        # -------------------------------------
        # TITLE LAYOUT
        # -------------------------------------

        # Title Frame Layout
        title_frame_lyt = wdg.QVBoxLayout()

        # Title Label Layout
        title_label_lyt = wdg.QVBoxLayout(self.title_frame)
        title_label_lyt.setAlignment(core.Qt.AlignCenter)

        # Project Frame Layout
        project_frame_lyt = wdg.QVBoxLayout()

        # Project Label Layout
        project_label_lyt = wdg.QVBoxLayout(self.project_frame)
        project_label_lyt.setAlignment(core.Qt.AlignCenter)

        # -------------------------------------
        # TOP LAYOUT
        # -------------------------------------

        # Top Layout
        top_lyt = wdg.QVBoxLayout()
        top_lyt.setContentsMargins(0, 20, 0, 15)

        # Workspace Group
        wks_grp = wdg.QGroupBox('Workspace')
        wks_lyt = wdg.QHBoxLayout()
        wks_lyt.setContentsMargins(10, 15, 10, 15)
        wks_lyt.setAlignment(core.Qt.AlignLeft)
        wks_grp.setLayout(wks_lyt)

        wks_grp.setStyleSheet(self.group_boxes_style)

        # -------------------------------------
        # MIDDLE LAYOUT
        # -------------------------------------

        # Middle Layout
        middle_lyt = wdg.QHBoxLayout()
        middle_lyt.setAlignment(core.Qt.AlignLeft)

        # Reference Nodes Group
        reference_nodes_grp = wdg.QGroupBox('Reference Nodes')
        reference_nodes_grp.setFixedWidth(310)
        reference_nodes_lyt = wdg.QVBoxLayout()
        reference_nodes_lyt.setContentsMargins(10, 15, 10, 15)
        reference_nodes_lyt.setAlignment(core.Qt.AlignLeft)
        reference_nodes_grp.setLayout(reference_nodes_lyt)

        # Repath Layout
        repath_lyt = wdg.QVBoxLayout()
        repath_lyt.setContentsMargins(10, 0, 0, 0)

        # -------------------------------------
        # BOTTOM LAYOUT
        # -------------------------------------

        # Bottom Layout
        bottom_lyt = wdg.QHBoxLayout()
        bottom_lyt.setAlignment(core.Qt.AlignLeft)

        # Rename Reference Node Group
        rename_reference_node_grp = wdg.QGroupBox('Rename Reference Node')
        rename_reference_node_grp.setFixedWidth(310)
        rename_reference_node_lyt = wdg.QVBoxLayout()
        rename_reference_node_lyt.setContentsMargins(10, 15, 10, 15)
        rename_reference_node_lyt.setAlignment(core.Qt.AlignLeft)
        rename_reference_node_grp.setLayout(rename_reference_node_lyt)

        # Rename Button Layout
        rename_btn_lyt = wdg.QVBoxLayout()
        rename_btn_lyt.setContentsMargins(10, 0, 0, 0)

        # -------------------------------------
        # LAYOUT ARRANGEMENT
        # -------------------------------------

        # Main Layout
        main_lyt.addLayout(title_frame_lyt)
        main_lyt.addLayout(project_frame_lyt)
        main_lyt.addLayout(top_lyt)
        main_lyt.addLayout(middle_lyt)
        main_lyt.addLayout(bottom_lyt)

        # Title Layout
        title_frame_lyt.addLayout(title_label_lyt)

        # Top Layout
        top_lyt.addWidget(wks_grp)

        # Middle Layout
        middle_lyt.addWidget(reference_nodes_grp)
        middle_lyt.addLayout(repath_lyt)

        # Bottom Layout
        bottom_lyt.addWidget(rename_reference_node_grp)
        bottom_lyt.addLayout(rename_btn_lyt)

        # -------------------------------------
        # WIDGET ARRANGEMENT
        # -------------------------------------

        # Title Widgets
        title_frame_lyt.addWidget(self.title_frame)
        title_label_lyt.addWidget(self.title_label)
        project_frame_lyt.addWidget(self.project_frame)
        project_label_lyt.addWidget(self.project_label)

        # Workspace
        wks_lyt.addWidget(self.wks_read_le)
        wks_lyt.addWidget(self.set_project_btn)

        # Reference Nodes
        reference_nodes_lyt.addWidget(self.reference_nodes_list)

        # RePath
        repath_lyt.addWidget(self.repath_btn)

        # Rename Reference Node
        rename_reference_node_lyt.addWidget(self.current_nmp_le)
        rename_reference_node_lyt.addWidget(self.new_nmp_le)

        # Rename Button
        rename_btn_lyt.addWidget(self.rename_btn)

    def create_connections(self):
        self.set_project_btn.pressed.connect(self.set_project_btn_pressed)

        self.reference_nodes_list.itemSelectionChanged.connect(self.reference_nodes_list_selchanged)

        self.repath_btn.pressed.connect(self.repath_btn_pressed)
        self.rename_btn.pressed.connect(self.rename_btn_pressed)

    def set_project_btn_pressed(self):

        mel.eval("SetProject;")
        new_wks = cmds.workspace(q=True, rd=True)
        self.wks_read_le.setText(new_wks)
        self.set_project_btn.setDown(False)
        self.set_project_btn.clearFocus()

    def reference_nodes_list_selchanged(self):
        current_item = self.reference_nodes_list.currentItem().text()

        self.current_nmp_le.setText(current_item)
        self.new_nmp_le.clear()

    def repath_btn_pressed(self):
        current_item = self.reference_nodes_list.currentItem().text()

        # -------------------------------------
        # CHARACTERS
        # -------------------------------------

        # John Variations
        if 'JOHN' in current_item or 'john' in current_item:
            # Load John Healthy
            if 'HEALTHY' in current_item or 'healthy' in current_item:
                cmds.file(john_healthy_path, loadReference=current_item, options="v=0;")
            # Load John Sick
            elif 'SICK' in current_item or 'sick' in current_item:
                cmds.file(john_sick_path, loadReference=current_item, options="v=0;")

        # Tay Variations
        if 'TAY' in current_item or 'tay' in current_item:
            # Load Tay Infant
            if 'INFANT' in current_item or 'infant' in current_item:
                cmds.file(tay_infant_path, loadReference=current_item, options="v=0;")
            # Load Tay Teen
            elif 'TEEN' in current_item or 'teen' in current_item:
                cmds.file(tay_teen_path, loadReference=current_item, options="v=0;")
            # Load Tay Toddler
            elif 'TODDLER' in current_item or 'toddler' in current_item:
                cmds.file(tay_toddler_path, loadReference=current_item, options="v=0;")

        # Danni Variations
        if 'DANNI' in current_item or 'danni' in current_item:
            # Load Dani Pregnant
            if 'PREGNANT' in current_item or 'pregnant' in current_item:
                cmds.file(danni_pregnant_path, loadReference=current_item, options="v=0;")
            # Load Dani Young
            elif 'YOUNG' in current_item or 'young' in current_item:
                cmds.file(danni_young_path, loadReference=current_item, options="v=0;")

        # Load Divine Being
        if 'DIVINE' in current_item or 'divine' in current_item:
            cmds.file(divine_being_path, loadReference=current_item, options="v=0;")

        # Load Doctor Female
        if 'DOCTOR' in current_item and 'FEMALE' in current_item:
            cmds.file(doctor_female_path, loadReference=current_item, options="v=0;")

        # Load Doctor Female
        if 'doctor' in current_item and 'female' in current_item:
            cmds.file(doctor_female_path, loadReference=current_item, options="v=0;")

        # Load Eye
        if 'EYE' in current_item or 'eye' in current_item or 'Eye' in current_item:
            cmds.file(eye_path, loadReference=current_item, options="v=0;")

        # -------------------------------------
        # CHARACTER PROPS
        # -------------------------------------

        # Load Backpack Apartment Tay A
        if 'BACKPACK' in current_item or 'backpack' in current_item:
            cmds.file(backpack_apartment_tay_A_path, loadReference=current_item, options="v=0;")

        # Bed Variations
        if 'BED' in current_item or 'bed' in current_item:
            # Load Bed Hospital A
            if 'HOSPITAL' in current_item or 'hospital' in current_item:
                cmds.file(bed_hospital_A1_path, loadReference=current_item, options="v=0;")

            # Load Bed Hospital Abyss A
            elif 'HOSPITAL' in current_item and 'ABYSS' in current_item:
                cmds.file(bed_hospital_abyss_A1_path, loadReference=current_item, options="v=0;")

            elif 'hospital' in current_item and 'abyss' in current_item:
                cmds.file(bed_hospital_abyss_A1_path, loadReference=current_item, options="v=0;")

            elif 'LIGHT' in current_item or 'light' in current_item:
                cmds.file(light_hospital_A_path, loadReference=current_item, options="v=0;")

                # Load Box Ring Wedding A
        if 'BOX' in current_item or 'box' in current_item:
            cmds.file(box_ring_wedding_A1_path, loadReference=current_item, options="v=0;")

        # Load Brush Abyss A
        if 'BRUSH' in current_item or 'brush' in current_item:
            cmds.file(brush_abyss_A1_path, loadReference=current_item, options="v=0;")

        # Load Cap Abyss A
        if 'CAP' in current_item or 'cap' in current_item:
            cmds.file(cap_abyss_A_path, loadReference=current_item, options="v=0;")

        # Load Clipboard A
        if 'CLIPBOARD' in current_item or 'clipboard' in current_item:
            cmds.file(cap_abyss_A_path, loadReference=current_item, options="v=0;")

        # Load Headphones Apartment Tay A
        if 'HEADPHONES' in current_item or 'headphones' in current_item:
            cmds.file(headphones_apartment_tay_A_path, loadReference=current_item, options="v=0;")

        # Picture Variations
        if 'PICTURE' in current_item or 'picture' in current_item:

            # Load Picture Apartment Tay A
            if 'APARTMENT' in current_item or 'apartment' in current_item:
                cmds.file(picture_apartment_tay_A_path, loadReference=current_item, options="v=0;")

        # Load Ring Wedding A1
        if 'RING' in current_item or 'ring' in current_item:
            cmds.file(ring_wedding_A1_path, loadReference=current_item, options="v=0;")

        # Load Shopping Cart Seminary A
        if 'SHOPPING' in current_item or 'shopping' in current_item:
            cmds.file(shopping_cart_seminary_A_pathm, loadReference=current_item, options="v=0;")

        # Load Vanity Abyss A
        if 'VANITY' in current_item or 'vanity' in current_item:
            cmds.file(vanity_abyss_A_path, loadReference=current_item, options="v=0;")

        # -------------------------------------
        # SETS
        # -------------------------------------

        # Load Hospital Room
        if 'HOSPITAL' in current_item or 'hospital' in current_item:
            cmds.file(hospital_room_path, loadReference=current_item, options="v=0;")

        # Load Spirit World
        if 'SPIRIT' in current_item or 'spirit' in current_item:
            cmds.file(spirit_world_path, loadReference=current_item, options="v=0;")

        # Load Train Platform
        if 'PLATFORM' in current_item or 'platform' in current_item:
            cmds.file(train_platform_path, loadReference=current_item, options="v=0;")

        # Load Train Station
        if 'STATION' in current_item or 'station' in current_item:
            cmds.file(train_station_path, loadReference=current_item, options="v=0;")

        # -------------------------------------
        # VEHICLES
        # -------------------------------------

        # Train Variations
        if 'TRAIN' in current_item or 'train' in current_item:

            # Load Train Proxy
            if 'PROXY' in current_item or 'proxy' in current_item:
                cmds.file(train_proxy_path, loadReference=current_item, options="v=0;")

            # Load Train Hires
            else:
                cmds.file(train_hires_path, loadReference=current_item, options="v=0;")

    def rename_btn_pressed(self):
        current_nmp = self.current_nmp_le.text()
        new_nmp = self.new_nmp_le.text()

        cmds.lockNode(current_nmp, lock=False)
        cmds.rename(current_nmp, new_nmp)
        cmds.lockNode(new_nmp, lock=True)

        # List all reference nodes
        self.all_reference_nodes = cmds.ls(type='reference')
        self.real_reference_nodes = []
        self.unloaded_reference_nodes = []

        for ref in self.all_reference_nodes:
            # Skip Maya's internal shared reference node
            if ref == "sharedReferenceNode":
                continue
            # Skip nodes that are themselves inside a reference
            if cmds.referenceQuery(ref, isNodeReferenced=True):
                continue
            # Skip nodes that are not real reference nodes
            try:
                is_loaded = cmds.referenceQuery(ref, isLoaded=True)
            except RuntimeError:
                # Happens for sharedReferenceNode or corrupted references
                continue
            if not is_loaded:
                self.unloaded_reference_nodes.append(ref)

        self.reference_nodes_list.clear()
        self.reference_nodes_list.addItems(self.unloaded_reference_nodes)

    def set_defaults(self):
        pass


# Runs the tool
def run():
    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = TOS_Reference_Linker(parent=get_maya_window())
    MAIN_WINDOW.show()