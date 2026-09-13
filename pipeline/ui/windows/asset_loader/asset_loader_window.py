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
        self.wks_read_le = wdg.QLineEdit()
        self.wks_read_le.setStyleSheet(self.wks_read_style)
        self.wks_read_le.setSizePolicy(wdg.QSizePolicy.Expanding, wdg.QSizePolicy.Fixed)
        self.wks_read_le.setFixedHeight(self.wks_height)
        self.wks_read_le.setEnabled(False)
        # self.wks_read_le.setText()

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

def asset_loader_run():

    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = tos_asset_loader_window(parent=mbr_util_get_maya_window())
    MAIN_WINDOW.show()