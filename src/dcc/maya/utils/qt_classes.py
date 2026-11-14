# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

from TOS_Pipeline.src.dcc.maya.utils.qt_compat import wdg, core, gui

# -------------------------------------
#
#       Classes
#
# -------------------------------------

class MBR_TOS_Base_Window(wdg.QMainWindow):

    def __init__(self, parent=None, title='TOS Tool', width=500, height=500):
        super(MBR_TOS_Base_Window, self).__init__(parent)

        # -------------------------------------
        #
        #       Window Title and Size
        #
        # -------------------------------------

        self.setWindowTitle(title)
        self.setFocusPolicy(core.Qt.ClickFocus)

        screen = wdg.QApplication.primaryScreen()
        screen_height = screen.availableGeometry().height()

        if screen_height < 720:
            initial_height = int(screen_height * 0.85)
        else:
            initial_height = height

        self.resize(width, initial_height)
        self.setMinimumSize(width, min(initial_height, int(screen_height * 0.5)))

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

        self.btn_enabled_style = """
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

        self.btn_disabled_style = """
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

        self.title_frame_style = "background-color: #1c0029"
        self.title_label_style = "font-size: 25px; color: #ffffff; font-weight: bold; font-style: italic"
        self.project_frame_style = "background-color: #ffffff"
        self.project_label_style = "font-size: 20px; color: #1c0029; font-weight: bold"

        self.wks_read_style = "text-align: left; padding-left: 6px;"
        self.thumbnail_style = "background-color: black;"

        self.wks_height = 25

    def build_ui(self):

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.set_defaults()

    def group_widget(self,
                     title,
                     layout=wdg.QVBoxLayout,
                     margins=(0,0,0,0),
                     alignment=None,
                     height=None):

        grp = wdg.QGroupBox(title)
        grp.setStyleSheet(self.group_boxes_style)

        lyt = layout()
        lyt.setContentsMargins(*margins)

        if alignment is not None:
            lyt.setAlignment(alignment)

        if height is not None:
            grp.setFixedHeight(height)

        if isinstance(lyt, wdg.QFormLayout):
            lyt.setLabelAlignment(core.Qt.AlignLeft)

        grp.setLayout(lyt)
        return grp, lyt