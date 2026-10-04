# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_compat import wdg, core, gui
from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_utils import mbr_util_get_maya_window
from TOS_Pipeline.pipeline.dcc.maya.ui.utils.qt_helpers import *

from TOS_Pipeline.pipeline.dcc.maya.engine.utils.maya_utils import *

from TOS_Pipeline.pipeline.core.fs_utils import *
from TOS_Pipeline.pipeline.core.naming import *

import maya.cmds as cmds

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

class tos_asset_loader_window(wdg.QMainWindow):

    def __init__(self, parent=None):
        super(tos_asset_loader_window, self).__init__(parent)

        # -------------------------------------
        #
        #       Window Title and Size
        #
        # -------------------------------------

        self.setWindowTitle(f"TOS Asset Loader {__VERSION__}")
        self.setFocusPolicy(core.Qt.ClickFocus)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = 790

        self.resize(740, initial_height)
        self.setMinimumSize(740, min(initial_height, int(screen_height * 0.5)))

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
        self.set_folder_btn = None
        self.lvl_01_combo = None
        self.lvl_02_combo = None
        self.lvl_03_combo = None
        self.lvl_04_combo = None
        self.lvl_05_combo = None

        self.file_list = None

        self.namespace_le = None
        self.quantity_spin = None
        self.reference_radio_btn = None
        self.import_radio_btn = None
        self.open_file_radio_btn = None

        self.thumbnail_label = None
        self.metadata_date_label = None
        self.metadata_size_label = None

        self.load_btn = None

        # -------------------------------------
        #
        #       Initialization Variables
        #
        # -------------------------------------

        # Variables
        self.init_lvl_01_folder_list = None
        self.lvl_01_folder_list = None
        self.current_file = None

        self.lvl_01_text, self.lvl_02_text, self.lvl_03_text = None, None, None
        self.lvl_04_text, self.lvl_05_text = None, None

        self.lvl_01_dir, self.lvl_02_dir, self.lvl_03_dir = None, None, None
        self.lvl_04_dir, self.lvl_05_dir = None, None

        # Init Assets List
        self.project_path = mbr_util_get_tos_path()

        if self.project_path:
            self.assets_path = f"{self.project_path}Assets"
        else:
            self.assets_path = None

        # Current workspace variable
        if self.assets_path:
            self.current_wks = cmds.workspace(q=True, rd=True)
        else:
            self.current_wks = 'Project is not set'

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

        self.wks_read_style = "text-align: left; padding-left: 6px;"
        self.thumbnail_style = "background-color: black;"

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

        self.lvl_combos = [self.lvl_01_combo, self.lvl_02_combo, self.lvl_03_combo, self.lvl_04_combo, self.lvl_05_combo]
        self.lvl_texts = [self.lvl_01_text, self.lvl_02_text, self.lvl_03_text, self.lvl_04_text, self.lvl_05_text]

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
        self.title_label = wdg.QLabel('Asset Loader')
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
        #       Top Widgets
        #
        # -------------------------------------

        # Workspace LineEdit
        self.wks_read_le = wdg.QLineEdit(self.current_wks)
        self.wks_read_le.setStyleSheet(self.wks_read_style)
        self.wks_read_le.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.wks_read_le.setFixedHeight(self.wks_height)
        self.wks_read_le.setEnabled(False)

        # Set Folder Button
        self.set_folder_btn = wdg.QPushButton('Set')
        self.set_folder_btn.setFixedWidth(35)
        self.set_folder_btn.setFixedHeight(self.wks_height)

        # Folder Lvl 01 Combo Box
        self.lvl_01_combo = wdg.QComboBox()
        self.lvl_01_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)

        # Folder Lvl 02 Combo Box
        self.lvl_02_combo = wdg.QComboBox()
        self.lvl_02_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)

        # Folder Lvl 03 Combo Box
        self.lvl_03_combo = wdg.QComboBox()
        self.lvl_03_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)

        # Folder Lvl 04 Combo Box
        self.lvl_04_combo = wdg.QComboBox()
        self.lvl_04_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)

        # Folder Lvl 05 Combo Box
        self.lvl_05_combo = wdg.QComboBox()
        self.lvl_05_combo.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)

        # -------------------------------------
        #
        #       Middle Widgets
        #
        # -------------------------------------

        # File List Widget
        self.file_list = wdg.QListWidget()
        self.file_list.setEnabled(False)
        self.file_list.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Expanding)

        # -------------------------------------
        #
        #       Bottom Widgets
        #
        # -------------------------------------

        # Namespace LineEdit
        self.namespace_le = wdg.QLineEdit()

        # Quantity Spinbox
        self.quantity_spin = wdg.QSpinBox()
        self.quantity_spin.setValue(1)

        # Reference Radio Button
        self.reference_radio_btn = wdg.QRadioButton('Reference')
        self.reference_radio_btn.setChecked(True)

        # Import Radio Button
        self.import_radio_btn = wdg.QRadioButton('Import')

        # Open File Radio Button
        self.open_file_radio_btn = wdg.QRadioButton('Open File')

        # -------------------------------------
        #
        #       Right Widgets
        #
        # -------------------------------------

        # Thumbnail Label
        self.thumbnail_label = wdg.QLabel()
        self.thumbnail_label.setFixedSize(300,300)
        self.thumbnail_label.setStyleSheet(self.thumbnail_style)
        self.thumbnail_label.setAlignment(core.Qt.AlignCenter)
        self.thumbnail_label.setScaledContents(False)

        # Metadata Date Label
        self.metadata_date_label = wdg.QLabel('')

        # Metadata File Size Label
        self.metadata_size_label = wdg.QLabel('')

        # Load Button
        self.load_btn = wdg.QPushButton('LOAD ASSET')
        self.load_btn.setStyleSheet(self.btn_style)
        self.load_btn.setFixedWidth(300)
        self.load_btn.setFixedHeight(100)

    # -------------------------------------
    #
    #       Create Layout
    #
    # -------------------------------------

    def create_layout(self):
        pass

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

        # -------------------------------------
        #
        #       Title Layout
        #
        # -------------------------------------

        title_frame_lyt = wdg.QVBoxLayout()

        title_lyt = wdg.QVBoxLayout(self.title_frame)
        title_lyt.setAlignment(core.Qt.AlignCenter)

        project_frame_lyt = wdg.QVBoxLayout()

        project_lyt = wdg.QVBoxLayout(self.project_frame)
        project_lyt.setAlignment(core.Qt.AlignCenter)

        # -------------------------------------
        #
        #       Section Layouts
        #
        # -------------------------------------

        # Top Layout
        top_lyt = wdg.QVBoxLayout()
        top_lyt.setContentsMargins(0,20,0,0)

        # Upper Layout
        upper_lyt = wdg.QVBoxLayout()

        # Middle Layout
        middle_lyt = wdg.QVBoxLayout()
        middle_lyt.setContentsMargins(0,0,0,0)

        # Bottom Layout
        bottom_lyt = wdg.QVBoxLayout()

        # Right Layout
        right_lyt = wdg.QVBoxLayout()
        right_lyt.setContentsMargins(0,0,0,0)

        # -------------------------------------
        #
        #       Upper Layouts Sections
        #
        # -------------------------------------

        # Set Folder Group
        set_folder_grp = wdg.QGroupBox('Workspace Folder')
        set_folder_grp.setStyleSheet(self.group_boxes_style)
        set_folder_lyt = wdg.QHBoxLayout()
        set_folder_lyt.setContentsMargins(10,15,10,15)
        set_folder_lyt.setAlignment(core.Qt.AlignLeft)
        set_folder_grp.setLayout(set_folder_lyt)

        # Folder Levels Layouts
        lvl_01_lyt = wdg.QHBoxLayout()
        lvl_02_lyt = wdg.QHBoxLayout()
        lvl_03_lyt = wdg.QHBoxLayout()
        lvl_04_lyt = wdg.QHBoxLayout()
        lvl_05_lyt = wdg.QHBoxLayout()

        # Folder Selection Group
        folder_selection_grp = wdg.QGroupBox('Folder Selection')
        folder_selection_grp.setStyleSheet(self.group_boxes_style)
        folder_selection_lyt = wdg.QFormLayout()
        folder_selection_lyt.setLabelAlignment(core.Qt.AlignLeft)
        folder_selection_lyt.setContentsMargins(10,15,10,15)
        folder_selection_grp.setLayout(folder_selection_lyt)

        # Folder Selection Group Rows
        folder_selection_lyt.addRow(lvl_01_lyt)
        folder_selection_lyt.addRow(lvl_02_lyt)
        folder_selection_lyt.addRow(lvl_03_lyt)
        folder_selection_lyt.addRow(lvl_04_lyt)
        folder_selection_lyt.addRow(lvl_05_lyt)

        # -------------------------------------
        #
        #       Middle Layout Sections
        #
        # -------------------------------------

        # File Selection Group
        file_selection_grp = wdg.QGroupBox('File Selection')
        file_selection_grp.setStyleSheet(self.group_boxes_style)
        file_selection_grp.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        file_selection_grp.setFixedHeight(145)
        file_selection_lyt = wdg.QVBoxLayout()
        file_selection_lyt.setContentsMargins(10,10,10,10)
        file_selection_grp.setLayout(file_selection_lyt)

        # -------------------------------------
        #
        #       Bottom Layout Sections
        #
        # -------------------------------------

        # Options Group
        options_grp = wdg.QGroupBox('Options')
        options_grp.setStyleSheet(self.group_boxes_style)
        options_lyt = wdg.QFormLayout()
        options_lyt.setLabelAlignment(core.Qt.AlignLeft)
        options_lyt.setContentsMargins(10,15,10,15)
        options_grp.setLayout(options_lyt)

        # Options Layouts
        namespace_lyt = wdg.QHBoxLayout()
        quantity_lyt = wdg.QHBoxLayout()
        import_type_lyt = wdg.QHBoxLayout()
        import_type_lyt.setAlignment(core.Qt.AlignLeft)

        # Options Group Rows
        options_lyt.addRow('Namespace     ', namespace_lyt)
        options_lyt.addRow('Quantity     ', quantity_lyt)
        options_lyt.addRow(import_type_lyt)

        # -------------------------------------
        #
        #       Right Layout Sections
        #
        # -------------------------------------

        # Thumbnail Layout
        thumbnail_lyt = wdg.QVBoxLayout()
        thumbnail_lyt.setContentsMargins(0,0,0,15)

        # Metadata Layout Rows
        metadata_date_lyt = wdg.QHBoxLayout()
        metadata_size_lyt = wdg.QHBoxLayout()

        # Metadata Group
        metadata_grp = wdg.QGroupBox('Metadata')
        metadata_grp.setStyleSheet(self.group_boxes_style)
        metadata_lyt = wdg.QFormLayout()
        metadata_lyt.setLabelAlignment(core.Qt.AlignLeft)
        metadata_lyt.setContentsMargins(10,15,10,15)
        metadata_grp.setLayout(metadata_lyt)

        # Metadata Group Rows
        metadata_lyt.addRow('Last Saved     ', metadata_date_lyt)
        metadata_lyt.addRow('File Size     ', metadata_size_lyt)

        # Load Button
        load_lyt = wdg.QVBoxLayout()
        load_lyt.setAlignment(core.Qt.AlignLeft)
        load_lyt.setContentsMargins(0,20,0,0)

        # -------------------------------------
        #
        #       Layout Arrangement
        #
        # -------------------------------------

        # Main Layout
        main_lyt.addLayout(title_frame_lyt)
        main_lyt.addLayout(project_frame_lyt)
        main_lyt.addLayout(sub_main_lyt)

        # Title Frame Layout
        title_frame_lyt.addLayout(title_lyt)

        # Sub Main Layout
        sub_main_lyt.addLayout(sub_main_left_lyt)
        sub_main_lyt.addLayout(sub_main_right_lyt)

        # Sub Main Left Layout
        sub_main_left_lyt.addLayout(top_lyt)
        sub_main_left_lyt.addLayout(upper_lyt)
        sub_main_left_lyt.addLayout(middle_lyt)
        sub_main_left_lyt.addLayout(bottom_lyt)
        sub_main_left_lyt.addStretch(1)

        # Sub Main Right Layout
        sub_main_right_lyt.addLayout(right_lyt)

        # Top Layout
        top_lyt.addWidget(set_folder_grp)

        # Upper Layout
        upper_lyt.addWidget(folder_selection_grp)

        # Middle Layout
        middle_lyt.addWidget(file_selection_grp)

        # Bottom Layout
        bottom_lyt.addWidget(options_grp)

        # Right Layout
        right_lyt.addLayout(thumbnail_lyt)
        right_lyt.addWidget(metadata_grp)
        right_lyt.addLayout(load_lyt)

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

        # Top Widgets
        set_folder_lyt.addWidget(self.wks_read_le)
        set_folder_lyt.addWidget(self.set_folder_btn)

        # Upper Widgets
        lvl_01_lyt.addWidget(self.lvl_01_combo)
        lvl_02_lyt.addWidget(self.lvl_02_combo)
        lvl_03_lyt.addWidget(self.lvl_03_combo)
        lvl_04_lyt.addWidget(self.lvl_04_combo)
        lvl_05_lyt.addWidget(self.lvl_05_combo)

        # Middle Widgets
        file_selection_lyt.addWidget(self.file_list)

        # Bottom Widgets
        namespace_lyt.addWidget(self.namespace_le)
        quantity_lyt.addWidget(self.quantity_spin)
        import_type_lyt.addWidget(self.reference_radio_btn)
        import_type_lyt.addWidget(self.import_radio_btn)
        import_type_lyt.addWidget(self.open_file_radio_btn)

        # Right Widgets
        thumbnail_lyt.addWidget(self.thumbnail_label)
        metadata_date_lyt.addWidget(self.metadata_date_label)
        metadata_size_lyt.addWidget(self.metadata_size_label)
        load_lyt.addWidget(self.load_btn)

    # -------------------------------------
    #
    #       Create Connections
    #
    # -------------------------------------

    def create_connections(self):

        self.set_folder_btn.clicked.connect(self.set_folder_btn_clicked)

        self.lvl_01_combo.currentIndexChanged.connect(self.lvl_01_combo_changed)
        self.lvl_02_combo.currentIndexChanged.connect(self.lvl_02_combo_changed)
        self.lvl_03_combo.currentIndexChanged.connect(self.lvl_03_combo_changed)
        self.lvl_04_combo.currentIndexChanged.connect(self.lvl_04_combo_changed)
        self.lvl_05_combo.currentIndexChanged.connect(self.lvl_05_combo_changed)

        self.file_list.currentRowChanged.connect(self.file_list_changed)

        self.reference_radio_btn.clicked.connect(self.reference_radio_btn_clicked)
        self.import_radio_btn.clicked.connect(self.import_radio_btn_clicked)
        self.open_file_radio_btn.clicked.connect(self.open_file_radio_btn_clicked)

        self.load_btn.clicked.connect(self.load_btn_clicked)

    # -------------------------------------
    #
    #       Set Defaults
    #
    # -------------------------------------

    def set_defaults(self):

        # Checks if the assets path is valid or not
        if self.assets_path:

            # Enables combo boxes if the assets path is valid
            self.lvl_01_combo.setEnabled(True)
            self.lvl_02_combo.setEnabled(False)
            self.lvl_03_combo.setEnabled(False)
            self.lvl_04_combo.setEnabled(False)
            self.lvl_05_combo.setEnabled(False)

            # Fills first combo box
            self.init_lvl_01_folder_list = ['-']
            self.init_lvl_01_folder_list.append(mbr_util_list_directory_contents(self.assets_path, content_type='folders'))
            self.lvl_01_folder_list = [self.init_lvl_01_folder_list[0]] + self.init_lvl_01_folder_list[1]
            self.lvl_01_combo.addItems(self.lvl_01_folder_list)

        else:
            self.lvl_01_combo.setEnabled(False)
            self.lvl_02_combo.setEnabled(False)
            self.lvl_03_combo.setEnabled(False)
            self.lvl_04_combo.setEnabled(False)
            self.lvl_05_combo.setEnabled(False)


    # -------------------------------------
    #
    #       Widget Signals
    #
    # -------------------------------------

    def set_folder_btn_clicked(self):

        # Block combos signals
        mbr_helper_block_signals(self.lvl_combos)

        tos_root = mbr_util_get_tos_root()

        if tos_root:
            project_path = f"{tos_root}/Production"
        else:
            return

        # Set project to project path
        cmds.workspace(project_path, openWorkspace=True)

        # Sets the read button text to current workspace
        self.wks_read_le.setText(project_path)

        # Sets Assets Path
        self.assets_path = f"{project_path}/Assets"

        # Enables combo boxes if the assets path is valid
        self.lvl_01_combo.setEnabled(True)
        self.lvl_02_combo.setEnabled(False)
        self.lvl_03_combo.setEnabled(False)
        self.lvl_04_combo.setEnabled(False)
        self.lvl_05_combo.setEnabled(False)

        # Fills first combo box
        self.init_lvl_01_folder_list = ['-']
        self.init_lvl_01_folder_list.append(mbr_util_list_directory_contents(self.assets_path, content_type='folders'))
        self.lvl_01_folder_list = [self.init_lvl_01_folder_list[0]] + self.init_lvl_01_folder_list[1]
        self.lvl_01_combo.addItems(self.lvl_01_folder_list)

        # Disables Set Project Button
        self.set_folder_btn.setEnabled(False)

        # Unlock combos signals
        mbr_helper_unlock_signals(self.lvl_combos)

    def lvl_01_combo_changed(self):

        # Preventing unwanted changes on combo boxes
        mbr_helper_block_signals(self.lvl_combos[1:])

        # Function variables
        self.lvl_01_text = self.lvl_01_combo.currentText()
        for item in self.lvl_texts[1:]:
            item = None

        # Clear Combos
        mbr_helper_clear_combos(self.lvl_combos[1:])
        self.file_list.clear()

        # Adding folders on the first combo box
        self.lvl_01_dir = f"{self.wks_read_le.text()}Assets/{self.lvl_01_text}"
        lvl_01_list = mbr_util_list_directory_contents(self.lvl_01_dir, content_type='folders')
        lvl_01_dirs_filtered = [x for x in lvl_01_list if not x.startswith('.')]
        lvl_01_dirs_sorted = sorted(lvl_01_dirs_filtered, key=lambda x: x.replace('_', ' ').lower())

        if len(lvl_01_dirs_sorted) > 0:
            self.lvl_02_combo.addItem('-')
            self.lvl_02_combo.addItems(lvl_01_dirs_sorted)

            # Settings Defaults
            self.lvl_02_combo.setEnabled(True)
            mbr_helper_set_disabled(self.lvl_combos[2:])

        # Adding files on the file combo box
        lvl_01_files = mbr_util_list_directory_contents(self.lvl_01_dir, content_type='files')
        lvl_01_files_filtered = []

        for item in lvl_01_files:
            if item.endswith(('.mb', '.ma')):
                lvl_01_files_filtered.append(item)

        # Combo Boxes clean up
        if len(lvl_01_files) == 0:
            self.file_list.setEnabled(False)
        else:
            self.file_list.setEnabled(True)
            self.file_list.addItems(lvl_01_files_filtered)

        # Reactivating signals on combo boxes
        mbr_helper_unlock_signals(self.lvl_combos[1:])

    def lvl_02_combo_changed(self):

        # Preventing unwanted changes on combo boxes
        mbr_helper_block_signals(self.lvl_combos[2:])

        # Function variables
        self.lvl_02_text = self.lvl_02_combo.currentText()
        for item in self.lvl_texts[2:]:
            item = None

        # Clear Combos
        mbr_helper_clear_combos(self.lvl_combos[2:])
        self.file_list.clear()

        # Adding folders on the first combo box
        self.lvl_02_dir = f"{self.lvl_01_dir}/{self.lvl_02_text}"
        lvl_02_list = mbr_util_list_directory_contents(self.lvl_02_dir, content_type='folders')
        lvl_02_dirs_filtered = [x for x in lvl_02_list if not x.startswith('.')]
        lvl_02_dirs_sorted = sorted(lvl_02_dirs_filtered, key=lambda x: x.replace('_', ' ').lower())

        if len(lvl_02_dirs_sorted) > 0:
            self.lvl_03_combo.addItem('-')
            self.lvl_03_combo.addItems(lvl_02_dirs_sorted)

            # Settings Defaults
            self.lvl_03_combo.setEnabled(True)
            mbr_helper_set_disabled(self.lvl_combos[3:])

        # Adding files on the file combo box
        lvl_02_files = mbr_util_list_directory_contents(self.lvl_02_dir, content_type='files')
        lvl_02_files_filtered = []

        for item in lvl_02_files:
            if item.endswith(('.mb', '.ma')):
                lvl_02_files_filtered.append(item)

        # Combo Boxes clean up
        if len(lvl_02_files) == 0:
            self.file_list.setEnabled(False)
        else:
            self.file_list.setEnabled(True)
            self.file_list.addItems(lvl_02_files_filtered)

        # Reactivating signals on combo boxes
        mbr_helper_unlock_signals(self.lvl_combos[2:])

    def lvl_03_combo_changed(self):

        # Preventing unwanted changes on combo boxes
        mbr_helper_block_signals(self.lvl_combos[3:])

        # Function variables
        self.lvl_03_text = self.lvl_03_combo.currentText()
        for item in self.lvl_texts[3:]:
            item = None

        # Clear Combos
        mbr_helper_clear_combos(self.lvl_combos[3:])
        self.file_list.clear()

        # Adding folders on the first combo box
        self.lvl_03_dir = f"{self.lvl_02_dir}/{self.lvl_03_text}"
        lvl_03_list = mbr_util_list_directory_contents(self.lvl_03_dir, content_type='folders')
        lvl_03_dirs_filtered = [x for x in lvl_03_list if not x.startswith('.')]
        lvl_03_dirs_sorted = sorted(lvl_03_dirs_filtered, key=lambda x: x.replace('_', ' ').lower())

        if len(lvl_03_dirs_sorted) > 0:
            self.lvl_04_combo.addItem('-')
            self.lvl_04_combo.addItems(lvl_03_dirs_sorted)

            # Settings Defaults
            self.lvl_04_combo.setEnabled(True)
            mbr_helper_set_disabled(self.lvl_combos[4:])

        # Adding files on the file combo box
        lvl_03_files = mbr_util_list_directory_contents(self.lvl_03_dir, content_type='files')
        lvl_03_files_filtered = []

        for item in lvl_03_files:
            if item.endswith(('.mb', '.ma')):
                lvl_03_files_filtered.append(item)

        # Combo Boxes clean up
        if len(lvl_03_files) == 0:
            self.file_list.setEnabled(False)
        else:
            self.file_list.setEnabled(True)
            self.file_list.addItems(lvl_03_files_filtered)

        # Reactivating signals on combo boxes
        mbr_helper_unlock_signals(self.lvl_combos[3:])


    def lvl_04_combo_changed(self):

        # Preventing unwanted changes on combo boxes
        mbr_helper_block_signals(self.lvl_combos[4:])

        # Function variables
        self.lvl_04_text = self.lvl_04_combo.currentText()
        for item in self.lvl_texts[4:]:
            item = None

        # Clear Combos
        mbr_helper_clear_combos(self.lvl_combos[4:])
        self.file_list.clear()

        # Adding folders on the first combo box
        self.lvl_04_dir = f"{self.lvl_03_dir}/{self.lvl_04_text}"
        lvl_04_list = mbr_util_list_directory_contents(self.lvl_04_dir, content_type='folders')
        lvl_04_dirs_filtered = [x for x in lvl_04_list if not x.startswith('.')]
        lvl_04_dirs_sorted = sorted(lvl_04_dirs_filtered, key=lambda x: x.replace('_', ' ').lower())

        if len(lvl_04_dirs_sorted) > 0:
            self.lvl_05_combo.addItem('-')
            self.lvl_05_combo.addItems(lvl_04_dirs_sorted)

            # Settings Defaults
            self.lvl_05_combo.setEnabled(True)
            mbr_helper_set_disabled(self.lvl_combos[5:])

        # Adding files on the file combo box
        lvl_04_files = mbr_util_list_directory_contents(self.lvl_04_dir, content_type='files')
        lvl_04_files_filtered = []

        for item in lvl_04_files:
            if item.endswith(('.mb', '.ma')):
                lvl_04_files_filtered.append(item)

        # Combo Boxes clean up
        if len(lvl_04_files) == 0:
            self.file_list.setEnabled(False)
        else:
            self.file_list.setEnabled(True)
            self.file_list.addItems(lvl_04_files_filtered)

        # Reactivating signals on combo boxes
        mbr_helper_unlock_signals(self.lvl_combos[4:])

    def lvl_05_combo_changed(self):

        # Preventing unwanted changes on combo boxes
        mbr_helper_block_signals(self.lvl_combos[5:])

        # Function variables
        self.lvl_05_text = self.lvl_05_combo.currentText()

        # Clear Combos
        self.file_list.clear()

        # Adding files on the file combo box
        lvl_05_files = mbr_util_list_directory_contents(self.lvl_05_dir, content_type='files')
        lvl_05_files_filtered = []

        for item in lvl_05_files:
            if item.endswith(('.mb', '.ma')):
                lvl_05_files_filtered.append(item)

        # Combo Boxes clean up
        if len(lvl_05_files) == 0:
            self.file_list.setEnabled(False)
        else:
            self.file_list.setEnabled(True)
            self.file_list.addItems(lvl_05_files_filtered)

        # Reactivating signals on combo boxes
        mbr_helper_unlock_signals(self.lvl_combos[5:])

    def file_list_changed(self):

        if not self.file_list.currentItem():
            return

        # Initial Variables
        self.current_file = self.file_list.currentItem().text()
        # self.get_thumbnail()

        # Fill Namespace
        current_file = self.file_list.currentItem().text()
        file_name_ext_index = current_file.find('_')
        self.namespace_le.setText(current_file[:file_name_ext_index].upper())

    def reference_radio_btn_clicked(self):

        self.namespace_le.setReadOnly(False)
        self.namespace_le.setStyleSheet("")

        # Fill Namespace
        current_file = self.file_list.currentItem().text()
        file_name_ext_index = current_file.find('.')
        self.namespace_le.setText(current_file[:file_name_ext_index].upper())

    def import_radio_btn_clicked(self):

        self.namespace_le.clear()
        self.namespace_le.setReadOnly(True)
        self.namespace_le.setStyleSheet("QLineEdit {background-color: #3d3d3d;}")

    def open_file_radio_btn_clicked(self):

        self.namespace_le.clear()
        self.namespace_le.setReadOnly(True)
        self.namespace_le.setStyleSheet("QLineEdit {background-color: #3d3d3d;}")

    def load_btn_clicked(self):

        # Initial Variables
        self.current_file = self.file_list.currentItem().text()
        asset_quantity = self.quantity_spin.value()
        #
        # Declares the maya file type
        if self.current_file.endswith('.ma'):
            maya_file_type = 'mayaAscii'
        elif self.current_file.endswith('.mb'):
            maya_file_type = 'mayaBinary'

        # Get File Path
        if self.lvl_01_text is not None and self.lvl_02_text is None:
            file_path = f"{self.lvl_01_dir}/{self.current_file}"

        elif self.lvl_02_text is not None and self.lvl_03_text is None:
            file_path = f"{self.lvl_02_dir}/{self.current_file}"

        elif self.lvl_03_text is not None and self.lvl_04_text is None:
            file_path = f"{self.lvl_03_dir}/{self.current_file}"

        elif self.lvl_04_text is not None and self.lvl_05_text is None:
            file_path = f"{self.lvl_04_dir}/{self.current_file}"

        elif self.lvl_05_text is not None:
            file_path = f"{self.lvl_05_dir}/{self.current_file}"


        # Open file depending on which radio button is checked
        if self.reference_radio_btn.isChecked():
            for asset in range(asset_quantity):
                mbr_util_file_reference(file_path, maya_file_type, self.namespace_le.text())

        elif self.import_radio_btn.isChecked():
            for asset in range(asset_quantity):
                mbr_util_file_import(file_path, maya_file_type)

        elif self.open_file_radio_btn.isChecked():
            for asset in range(asset_quantity):
                mbr_util_open_file(file_path)

        # Block signals of combo boxes
        mbr_helper_block_signals(self.lvl_combos)

        # Reset Variables to None
        for item in self.lvl_texts:
            item = None

        # Clear Combo Boxes and disable them
        mbr_helper_clear_combos(self.lvl_combos[1:])
        mbr_helper_set_disabled(self.lvl_combos[1:])
        self.file_list.clear()

        # Set first combo box to first index
        self.lvl_01_combo.setCurrentIndex(0)

        # Reactivating signals on combo boxes
        mbr_helper_unlock_signals(self.lvl_combos)

# -------------------------------------
#
#       Run Function
#
# -------------------------------------

def run():

    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = tos_asset_loader_window(parent=mbr_util_get_maya_window())
    MAIN_WINDOW.show()