# Import Modules
from PySide6 import QtWidgets as wdg
from PySide6 import QtCore as core
from PySide6 import QtGui as gui
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

############################
# VARIABLES
############################

MAIN_WINDOW = None
__version__ = '2.2'


############################
# FUNCTIONS
############################

def getMayaWindow():
    '''
    Get Maya Main Window and Return it
    '''
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), wdg.QWidget)
    return mayaMainWindow


def bake():
    '''
    Bakes Animation without updating the viewport
    '''
    cmds.BakeSimulation()
    # cmds.filterCurve()
    cmds.delete(cn=True, sc=True)
    mel.eval('generateAllUvTilePreviews')


def aimSpace(worldUpObject, axis):
    '''
    Creates an aim constraint relationship depending on the values of the arguments
    '''
    aimResponse = axis

    if aimResponse == '+X':
        cmds.aimConstraint(mo=True, w=1, aim=(1, 0, 0), u=(0, 0, 1), wut='objectRotation', wu=(0, 0, 1),
                           wuo=worldUpObject)
    else:
        if aimResponse == '+Y':
            cmds.aimConstraint(mo=True, w=1, aim=(0, 1, 0), u=(0, 0, 1), wut='objectRotation', wu=(0, 0, 1),
                               wuo=worldUpObject)
        else:
            if aimResponse == '+Z':
                cmds.aimConstraint(mo=True, w=1, aim=(0, 0, 1), u=(0, 1, 0), wut='objectRotation', wu=(0, 1, 0),
                                   wuo=worldUpObject)
            else:
                if aimResponse == '-X':
                    cmds.aimConstraint(mo=True, w=1, aim=(-1, 0, 0), u=(0, 0, 1), wut='objectRotation', wu=(0, 0, 1),
                                       wuo=worldUpObject)
                else:
                    if aimResponse == '-Y':
                        cmds.aimConstraint(mo=True, w=1, aim=(0, -1, 0), u=(0, 0, 1), wut='objectRotation',
                                           wu=(0, 0, 1), wuo=worldUpObject)
                    else:
                        if aimResponse == '-Z':
                            cmds.aimConstraint(mo=True, w=1, aim=(0, 0, -1), u=(0, 1, 0), wut='objectRotation',
                                               wu=(0, 1, 0), wuo=worldUpObject)


def addPhysics(goalSmoothness, goalWeight):
    '''
    Adds physics overlap to selected object (Only one at a time)
    '''
    selObject = cmds.ls(selection=True)
    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)

    # Create Proxy Transform
    cmds.spaceLocator(n='proxyTransform')

    # Proxy Transform Contrained to Sphere
    cmds.select(cl=True)
    cmds.select(selObject[0], tgl=True)
    cmds.select('proxyTransform', tgl=True)
    cmds.pointConstraint()

    # Proxy Transform baked to match Sphere animation
    cmds.select(cl=True)
    cmds.select('proxyTransform', tgl=True)
    bake()

    # Create Particle Emitter
    cmds.select(cl=True)
    cmds.emitter()
    cmds.nParticle()
    cmds.connectDynamic('nParticle1', em='emitter1')

    cmds.setAttr('nParticleShape1.particleRenderType', 4)
    cmds.setAttr('nParticleShape1.maxCount', 1)

    cmds.playbackOptions(min=minTime - 50, max=maxTime)
    cmds.setAttr('nucleus1.startFrame', minTime - 50)

    cmds.select('emitter1', r=True)
    cmds.select('proxyTransform', tgl=True)
    cmds.MatchTranslation()

    cmds.select('nParticle1', r=True)
    cmds.select('proxyTransform', tgl=True)
    cmds.MatchTransform()

    # Set a Goal
    cmds.goal('nParticle1', g='proxyTransform', w=0.5, utr=0)
    cmds.setAttr('nParticleShape1.goalSmoothness', goalSmoothness)
    cmds.setAttr('nParticleShape1.goalWeight[0]', goalWeight)

    # Particle Tracker
    cmds.spaceLocator(n='particleTracker')
    cmds.connectAttr('nParticleShape1.worldCentroid', 'particleTracker.translate', f=True)

    cmds.select('particleTracker', r=True)
    bake()
    cmds.delete('proxyTransform')
    cmds.delete('emitter1')
    cmds.delete('nParticle1')
    cmds.delete('nucleus1')

    cmds.select('particleTracker', r=True)
    cmds.select(selObject[0], tgl=True)
    cmds.pointConstraint()

    cmds.playbackOptions(min=minTime, max=maxTime)

    # Bake Object
    cmds.select(selObject[0], r=True)
    cmds.BakeSimulation()
    cmds.delete(sc=True)
    mel.eval('generateAllUvTilePreviews')
    cmds.delete('particleTracker')


######################################
# ANIM OVERLAP GENERATOR CLASS
######################################

# Main class
class AnimOverlapGenerator(wdg.QMainWindow):

    ############### INIT FUNCTION ###############
    #############################################
    #############################################

    def __init__(self, parent=None):
        super(AnimOverlapGenerator, self).__init__(parent)

        self.setWindowTitle(f"Anim Overlap Generator {__version__}")
        self.selectedAxis = '+X'
        self.selectedWorldSpaceConversion = 'Yes'
        self.rightEarSelectedAxis = '+X'
        self.leftEarSelectedAxis = '+X'
        self.earsRotationOffsetValue = 2
        self.targetAimSelectedAxis = '+X'
        self.rootsAimSelectedAxis = '+X'
        self.stringOffsetValue = 1

        # Menu Bar and How To Use the tool menu
        menuBar = self.menuBar()
        helpMenu = menuBar.addMenu('Help')

        howToUseAction = gui.QAction('Ears Overlap - How To Use', self)
        helpMenu.addAction(howToUseAction)
        howToUseAction.triggered.connect(self.howToUseActionTriggered)

        self.createUI()

    ################ USER INTERFACE ################
    ################################################
    ################################################

    def createUI(self):

        ############### LAYOUTS ################
        ########################################

        ### Central Widget ###
        centralWdg = wdg.QWidget()
        self.setCentralWidget(centralWdg)

        ### Main Layout ###
        mainLyt = wdg.QVBoxLayout(centralWdg)
        mainLyt.setAlignment(core.Qt.AlignTop)
        mainLyt.setContentsMargins(40, 30, 40, 0)

        ##### MAIN LAYOUT SECTIONS - Sections Layouts #####
        ### Title Layout ###
        titleLyt = wdg.QVBoxLayout()
        titleLyt.setAlignment(core.Qt.AlignCenter)
        mainLyt.addLayout(titleLyt)

        ### Upper Layout ###
        upperLyt = wdg.QVBoxLayout()
        upperLyt.setContentsMargins(0, 20, 0, 15)
        mainLyt.addLayout(upperLyt)

        ### Bottom Layout ###
        bottomLyt = wdg.QVBoxLayout()
        mainLyt.addLayout(bottomLyt)

        ##### TITLE LAYOUT CONTENTS #####
        ### Title Widgets ###
        # Anim Physics Generator Label
        animOverlapGeneratorLabel = wdg.QLabel('Anim Overlap Generator')
        animOverlapGeneratorLabel.setStyleSheet("font-size: 20px;")
        animOverlapGeneratorLabel.setAlignment(core.Qt.AlignCenter)
        titleLyt.addWidget(animOverlapGeneratorLabel)

        # Author Label
        authorLabel = wdg.QLabel('Author: Mauricio Botero Ruiz')
        authorLabel.setStyleSheet("font-size: 12px;")
        authorLabel.setAlignment(core.Qt.AlignCenter)
        titleLyt.addWidget(authorLabel)

        ##### UPPER LAYOUT SECTIONS - Tool Buttons Layouts #####
        ### TAB LAYOUT WIDGETS ###
        ## Tab Container Widget
        self.tabWdg = wdg.QTabWidget()
        upperLyt.addWidget(self.tabWdg)
        self.tabWdg.currentChanged.connect(self.tabWdgCurrentChanged)

        ## Aim Tab Widget
        aimTabWdg = wdg.QWidget()
        self.tabWdg.addTab(aimTabWdg, 'Aim Setup')
        aimTabLyt = wdg.QVBoxLayout(aimTabWdg)
        aimTabLyt.setAlignment(core.Qt.AlignTop)

        aimTopMainLyt = wdg.QHBoxLayout()
        aimTopMainLyt.setAlignment(core.Qt.AlignTop)
        aimTopMainLyt.setContentsMargins(0, 0, 0, 0)
        aimTabLyt.addLayout(aimTopMainLyt)

        aimTopSubLyt = wdg.QHBoxLayout()
        aimTopSubLyt.setAlignment(core.Qt.AlignTop)
        aimTopSubLyt.setContentsMargins(0, 0, 0, 0)
        aimTabLyt.addLayout(aimTopSubLyt)

        aimBotMainLyt = wdg.QHBoxLayout()
        aimBotMainLyt.setAlignment(core.Qt.AlignTop)
        aimBotMainLyt.setContentsMargins(0, 0, 0, 0)
        aimTabLyt.addLayout(aimBotMainLyt)

        aimBotSubLyt = wdg.QHBoxLayout()
        aimBotSubLyt.setAlignment(core.Qt.AlignTop)
        aimBotSubLyt.setContentsMargins(0, 0, 0, 0)
        aimTabLyt.addLayout(aimBotSubLyt)

        aimCreateLyt = wdg.QHBoxLayout()
        aimCreateLyt.setAlignment(core.Qt.AlignCenter)
        aimCreateLyt.setContentsMargins(0, 10, 0, 0)
        aimTabLyt.addLayout(aimCreateLyt)

        ## Overalp Physics Tab Widget
        overlapPhysicsTabWdg = wdg.QWidget()
        self.tabWdg.addTab(overlapPhysicsTabWdg, 'Overlap Physics')
        overlapPhysicsTabLyt = wdg.QVBoxLayout(overlapPhysicsTabWdg)
        overlapPhysicsTabLyt.setAlignment(core.Qt.AlignTop)

        overlapPhysicsMainLyt = wdg.QHBoxLayout()
        overlapPhysicsMainLyt.setAlignment(core.Qt.AlignTop)
        overlapPhysicsMainLyt.setContentsMargins(0, 20, 0, 0)
        overlapPhysicsTabLyt.addLayout(overlapPhysicsMainLyt)

        overlapPhysicsLabelsLyt = wdg.QVBoxLayout()
        overlapPhysicsLabelsLyt.setContentsMargins(0, 0, 0, 0)
        overlapPhysicsMainLyt.addLayout(overlapPhysicsLabelsLyt)

        overlapPhysicsNumericLyt = wdg.QVBoxLayout()
        overlapPhysicsNumericLyt.setAlignment(core.Qt.AlignLeft)
        overlapPhysicsNumericLyt.setContentsMargins(0, 0, 20, 0)
        overlapPhysicsMainLyt.addLayout(overlapPhysicsNumericLyt)

        overlapPhysicsAddLyt = wdg.QHBoxLayout()
        overlapPhysicsAddLyt.setContentsMargins(0, 0, 30, 0)
        overlapPhysicsMainLyt.addLayout(overlapPhysicsAddLyt)

        overlapPhysicsInstructionsLyt = wdg.QVBoxLayout()
        overlapPhysicsInstructionsLyt.setContentsMargins(0, 10, 0, 0)
        overlapPhysicsTabLyt.addLayout(overlapPhysicsInstructionsLyt)

        ## Ears Physics Tab Widget
        earsPhysicsTabWdg = wdg.QWidget()
        self.tabWdg.addTab(earsPhysicsTabWdg, 'Ears Overlap')
        earsPhysicsTabLyt = wdg.QVBoxLayout(earsPhysicsTabWdg)
        earsPhysicsTabLyt.setAlignment(core.Qt.AlignTop)

        earsPhysicsMainLyt = wdg.QVBoxLayout()
        earsPhysicsMainLyt.setAlignment(core.Qt.AlignCenter)
        earsPhysicsMainLyt.setContentsMargins(0, 20, 0, 0)
        earsPhysicsTabLyt.addLayout(earsPhysicsMainLyt)

        earsPhysicsRightEarAimLyt = wdg.QHBoxLayout()
        earsPhysicsMainLyt.addLayout(earsPhysicsRightEarAimLyt)

        earsPhysicsLeftEarAimLyt = wdg.QHBoxLayout()
        earsPhysicsMainLyt.addLayout(earsPhysicsLeftEarAimLyt)

        earsPhysicsGoalLyt = wdg.QHBoxLayout()
        earsPhysicsMainLyt.addLayout(earsPhysicsGoalLyt)

        earsRotationOffsetLyt = wdg.QHBoxLayout()
        earsPhysicsMainLyt.addLayout(earsRotationOffsetLyt)

        earsGenerateLyt = wdg.QHBoxLayout()
        earsGenerateLyt.setContentsMargins(0, 10, 0, 0)
        earsPhysicsMainLyt.addLayout(earsGenerateLyt)

        ## Aim String Tab Widget
        aimStringTabWdg = wdg.QWidget()
        self.tabWdg.addTab(aimStringTabWdg, 'Aim String')
        aimStringTabLyt = wdg.QVBoxLayout(aimStringTabWdg)
        aimStringTabLyt.setAlignment(core.Qt.AlignTop)

        aimStringMainLyt = wdg.QVBoxLayout()
        aimStringMainLyt.setAlignment(core.Qt.AlignTop)
        aimStringMainLyt.setContentsMargins(0, 20, 0, 0)
        aimStringTabLyt.addLayout(aimStringMainLyt)

        aimStringTargetAxisLyt = wdg.QHBoxLayout()
        aimStringTargetAxisLyt.setAlignment(core.Qt.AlignLeft)
        aimStringMainLyt.addLayout(aimStringTargetAxisLyt)

        aimStringRootsAxisLyt = wdg.QHBoxLayout()
        aimStringRootsAxisLyt.setAlignment(core.Qt.AlignLeft)
        aimStringMainLyt.addLayout(aimStringRootsAxisLyt)

        aimStringOffsetLyt = wdg.QHBoxLayout()
        aimStringOffsetLyt.setAlignment(core.Qt.AlignLeft)
        aimStringMainLyt.addLayout(aimStringOffsetLyt)

        aimStringGenerateLyt = wdg.QHBoxLayout()
        aimStringGenerateLyt.setContentsMargins(0, 10, 0, 0)
        aimStringMainLyt.addLayout(aimStringGenerateLyt)

        ##### BOTTOM LAYOUT SECTIONS - Instructions Layouts #####
        instructionsLyt = wdg.QVBoxLayout()
        bottomLyt.addLayout(instructionsLyt)

        ############### WIDGETS ################
        ########################################

        ##### UPPER LAYOUT WIDGETS #####
        # Aim Tab Widgets
        self.upAxisLabel = wdg.QLabel('Up Axis:')
        self.upAxisLabel.setContentsMargins(0, 15, 0, 0)
        aimTopMainLyt.addWidget(self.upAxisLabel)

        self.positiveXAxisButton = wdg.QPushButton('+ X')
        self.positiveXAxisButton.setFixedWidth(50)
        self.positiveXAxisButton.setCheckable(True)
        self.positiveXAxisButton.setChecked(True)
        aimTopSubLyt.addWidget(self.positiveXAxisButton)
        self.positiveXAxisButton.toggled.connect(self.positiveXAxisButtonToggled)

        self.negativeXAxisButton = wdg.QPushButton('- X')
        self.negativeXAxisButton.setFixedWidth(50)
        self.negativeXAxisButton.setCheckable(True)
        aimTopSubLyt.addWidget(self.negativeXAxisButton)
        self.negativeXAxisButton.toggled.connect(self.negativeXAxisButtonToggled)

        self.positiveYAxisButton = wdg.QPushButton('+ Y')
        self.positiveYAxisButton.setFixedWidth(50)
        self.positiveYAxisButton.setCheckable(True)
        aimTopSubLyt.addWidget(self.positiveYAxisButton)
        self.positiveYAxisButton.toggled.connect(self.positiveYAxisButtonToggled)

        self.negativeYAxisButton = wdg.QPushButton('- Y')
        self.negativeYAxisButton.setFixedWidth(50)
        self.negativeYAxisButton.setCheckable(True)
        aimTopSubLyt.addWidget(self.negativeYAxisButton)
        self.negativeYAxisButton.toggled.connect(self.negativeYAxisButtonToggled)

        self.positiveZAxisButton = wdg.QPushButton('+ Z')
        self.positiveZAxisButton.setFixedWidth(50)
        self.positiveZAxisButton.setCheckable(True)
        aimTopSubLyt.addWidget(self.positiveZAxisButton)
        self.positiveZAxisButton.toggled.connect(self.positiveZButtonToggled)

        self.negativeZAxisButton = wdg.QPushButton('- Z')
        self.negativeZAxisButton.setFixedWidth(50)
        self.negativeZAxisButton.setCheckable(True)
        aimTopSubLyt.addWidget(self.negativeZAxisButton)
        self.negativeZAxisButton.toggled.connect(self.negativeZAxisButtonToggled)

        self.xformOffsetSpinBox = wdg.QDoubleSpinBox()
        self.xformOffsetSpinBox.setFixedWidth(90)
        self.xformOffsetSpinBox.setFixedHeight(25)
        self.xformOffsetSpinBox.setMinimum(1)
        self.xformOffsetSpinBox.setMaximum(200)
        self.xformOffsetSpinBox.setSingleStep(1.0)
        self.xformOffsetSpinBox.setValue(20)
        aimTopSubLyt.addWidget(self.xformOffsetSpinBox)

        self.axisGroup = wdg.QButtonGroup()
        self.axisGroup.setExclusive(True)
        self.axisGroup.addButton(self.positiveXAxisButton)
        self.axisGroup.addButton(self.negativeXAxisButton)
        self.axisGroup.addButton(self.positiveYAxisButton)
        self.axisGroup.addButton(self.negativeYAxisButton)
        self.axisGroup.addButton(self.positiveZAxisButton)
        self.axisGroup.addButton(self.negativeZAxisButton)

        self.worldSpaceConversionLabel = wdg.QLabel('World Space Translation?:')
        self.worldSpaceConversionLabel.setContentsMargins(0, 20, 0, 0)
        aimBotMainLyt.addWidget(self.worldSpaceConversionLabel)

        self.worldSpaceConversionYesButton = wdg.QPushButton('Yes')
        self.worldSpaceConversionYesButton.setFixedWidth(70)
        self.worldSpaceConversionYesButton.setCheckable(True)
        self.worldSpaceConversionYesButton.setChecked(True)
        aimBotSubLyt.addWidget(self.worldSpaceConversionYesButton)
        self.worldSpaceConversionYesButton.toggled.connect(self.worldSpaceConversionYesButtonToggled)

        self.worldSpaceConversionNoButton = wdg.QPushButton('No')
        self.worldSpaceConversionNoButton.setFixedWidth(70)
        self.worldSpaceConversionNoButton.setCheckable(True)
        aimBotSubLyt.addWidget(self.worldSpaceConversionNoButton)
        self.worldSpaceConversionNoButton.toggled.connect(self.worldSpaceConversionNoButtonToggled)

        self.worldSpaceConversionGroup = wdg.QButtonGroup()
        self.worldSpaceConversionGroup.setExclusive(True)
        self.worldSpaceConversionGroup.addButton(self.worldSpaceConversionYesButton)
        self.worldSpaceConversionGroup.addButton(self.worldSpaceConversionNoButton)

        self.createAimSetupButton = wdg.QPushButton('GENERATE AIM SETUP')
        self.createAimSetupButton.setContentsMargins(0, 30, 0, 0)
        self.createAimSetupButton.setFixedWidth(150)
        self.createAimSetupButton.setFixedHeight(40)
        aimCreateLyt.addWidget(self.createAimSetupButton)
        self.createAimSetupButton.pressed.connect(self.createAimSetupButtonPressed)

        # Overlap Physics Widgets
        self.goalSmoothnessLabel = wdg.QLabel('Goal Smoothness')
        overlapPhysicsLabelsLyt.addWidget(self.goalSmoothnessLabel)

        self.goalWeightLabel = wdg.QLabel('Goal Weight')
        overlapPhysicsLabelsLyt.addWidget(self.goalWeightLabel)

        self.goalSmoothnessNumeric = wdg.QDoubleSpinBox()
        self.goalSmoothnessNumeric.setFixedWidth(90)
        self.goalSmoothnessNumeric.setMinimum(0.0)
        self.goalSmoothnessNumeric.setMaximum(4.0)
        self.goalSmoothnessNumeric.setSingleStep(0.1)
        self.goalSmoothnessNumeric.setValue(2.0)
        overlapPhysicsNumericLyt.addWidget(self.goalSmoothnessNumeric)

        self.goalWeightNumeric = wdg.QDoubleSpinBox()
        self.goalWeightNumeric.setFixedWidth(90)
        self.goalWeightNumeric.setMinimum(0.0)
        self.goalWeightNumeric.setMaximum(1.0)
        self.goalWeightNumeric.setSingleStep(0.01)
        self.goalWeightNumeric.setDecimals(2)
        self.goalWeightNumeric.setValue(0.62)
        overlapPhysicsNumericLyt.addWidget(self.goalWeightNumeric)

        self.addPhysicsButton = wdg.QPushButton('GENERATE OVERLAP PHYSICS')
        self.addPhysicsButton.setFixedWidth(200)
        self.addPhysicsButton.setFixedHeight(40)
        overlapPhysicsAddLyt.addWidget(self.addPhysicsButton)
        self.addPhysicsButton.pressed.connect(self.addPhysicsButtonPressed)

        self.goalSmoothnessInstructionsLabel = wdg.QLabel('Goal Smoothness (0-4): Higher Number = More Offset')
        overlapPhysicsInstructionsLyt.addWidget(self.goalSmoothnessInstructionsLabel)

        self.goalWeightInstructionsLabel = wdg.QLabel('Goal Weight (0-1): Higher Number = Less Offset')
        overlapPhysicsInstructionsLyt.addWidget(self.goalWeightInstructionsLabel)

        # Ears Physics Widgets
        # Right Ear Aim Setup Widgets
        self.rightEarUpAxisLabel = wdg.QLabel('Right Ear Up Axis')
        earsPhysicsRightEarAimLyt.addWidget(self.rightEarUpAxisLabel)

        self.rightEarUpAxisPositiveX = wdg.QPushButton('+ X')
        self.rightEarUpAxisPositiveX.setFixedWidth(50)
        self.rightEarUpAxisPositiveX.setCheckable(True)
        self.rightEarUpAxisPositiveX.setChecked(True)
        earsPhysicsRightEarAimLyt.addWidget(self.rightEarUpAxisPositiveX)
        self.rightEarUpAxisPositiveX.toggled.connect(self.rightEarUpAxisPositiveXToggled)

        self.rightEarUpAxisNegativeX = wdg.QPushButton('- X')
        self.rightEarUpAxisNegativeX.setFixedWidth(50)
        self.rightEarUpAxisNegativeX.setCheckable(True)
        earsPhysicsRightEarAimLyt.addWidget(self.rightEarUpAxisNegativeX)
        self.rightEarUpAxisNegativeX.toggled.connect(self.rightEarUpAxisNegativeXToggled)

        self.rightEarUpAxisPositiveY = wdg.QPushButton('+ Y')
        self.rightEarUpAxisPositiveY.setFixedWidth(50)
        self.rightEarUpAxisPositiveY.setCheckable(True)
        earsPhysicsRightEarAimLyt.addWidget(self.rightEarUpAxisPositiveY)
        self.rightEarUpAxisPositiveY.toggled.connect(self.rightEarUpAxisPositiveYToggled)

        self.rightEarUpAxisNegativeY = wdg.QPushButton('- Y')
        self.rightEarUpAxisNegativeY.setFixedWidth(50)
        self.rightEarUpAxisNegativeY.setCheckable(True)
        earsPhysicsRightEarAimLyt.addWidget(self.rightEarUpAxisNegativeY)
        self.rightEarUpAxisNegativeY.toggled.connect(self.rightEarUpAxisNegativeYToggled)

        self.rightEarUpAxisPositiveZ = wdg.QPushButton('+ Z')
        self.rightEarUpAxisPositiveZ.setFixedWidth(50)
        self.rightEarUpAxisPositiveZ.setCheckable(True)
        earsPhysicsRightEarAimLyt.addWidget(self.rightEarUpAxisPositiveZ)
        self.rightEarUpAxisPositiveZ.toggled.connect(self.rightEarUpAxisPositiveZToggled)

        self.rightEarUpAxisNegativeZ = wdg.QPushButton('- Z')
        self.rightEarUpAxisNegativeZ.setFixedWidth(50)
        self.rightEarUpAxisNegativeZ.setCheckable(True)
        earsPhysicsRightEarAimLyt.addWidget(self.rightEarUpAxisNegativeZ)
        self.rightEarUpAxisNegativeZ.toggled.connect(self.rightEarUpAxisNegativeZToggled)

        self.rightEarXFormOffsetSpinBox = wdg.QDoubleSpinBox()
        self.rightEarXFormOffsetSpinBox.setFixedWidth(90)
        self.rightEarXFormOffsetSpinBox.setFixedHeight(25)
        self.rightEarXFormOffsetSpinBox.setMinimum(1)
        self.rightEarXFormOffsetSpinBox.setMaximum(200)
        self.rightEarXFormOffsetSpinBox.setSingleStep(1.0)
        self.rightEarXFormOffsetSpinBox.setValue(20)
        earsPhysicsRightEarAimLyt.addWidget(self.rightEarXFormOffsetSpinBox)

        self.rightEarUpAxisGroup = wdg.QButtonGroup()
        self.rightEarUpAxisGroup.setExclusive(True)
        self.rightEarUpAxisGroup.addButton(self.rightEarUpAxisPositiveX)
        self.rightEarUpAxisGroup.addButton(self.rightEarUpAxisNegativeX)
        self.rightEarUpAxisGroup.addButton(self.rightEarUpAxisPositiveY)
        self.rightEarUpAxisGroup.addButton(self.rightEarUpAxisNegativeY)
        self.rightEarUpAxisGroup.addButton(self.rightEarUpAxisPositiveZ)
        self.rightEarUpAxisGroup.addButton(self.rightEarUpAxisNegativeZ)

        # Left Ear Aim Setup Widgets
        self.leftEarUpAxisLabel = wdg.QLabel('Left Ear Up Axis')
        earsPhysicsLeftEarAimLyt.addWidget(self.leftEarUpAxisLabel)

        self.leftEarUpAxisPositiveX = wdg.QPushButton('+ X')
        self.leftEarUpAxisPositiveX.setFixedWidth(50)
        self.leftEarUpAxisPositiveX.setCheckable(True)
        self.leftEarUpAxisPositiveX.setChecked(True)
        earsPhysicsLeftEarAimLyt.addWidget(self.leftEarUpAxisPositiveX)
        self.leftEarUpAxisPositiveX.toggled.connect(self.leftEarUpAxisPositiveXToggled)

        self.leftEarUpAxisNegativeX = wdg.QPushButton('- X')
        self.leftEarUpAxisNegativeX.setFixedWidth(50)
        self.leftEarUpAxisNegativeX.setCheckable(True)
        earsPhysicsLeftEarAimLyt.addWidget(self.leftEarUpAxisNegativeX)
        self.leftEarUpAxisNegativeX.toggled.connect(self.leftEarUpAxisNegativeXToggled)

        self.leftEarUpAxisPositiveY = wdg.QPushButton('+ Y')
        self.leftEarUpAxisPositiveY.setFixedWidth(50)
        self.leftEarUpAxisPositiveY.setCheckable(True)
        earsPhysicsLeftEarAimLyt.addWidget(self.leftEarUpAxisPositiveY)
        self.leftEarUpAxisPositiveY.toggled.connect(self.leftEarUpAxisPositiveYToggled)

        self.leftEarUpAxisNegativeY = wdg.QPushButton('- Y')
        self.leftEarUpAxisNegativeY.setFixedWidth(50)
        self.leftEarUpAxisNegativeY.setCheckable(True)
        earsPhysicsLeftEarAimLyt.addWidget(self.leftEarUpAxisNegativeY)
        self.leftEarUpAxisNegativeY.toggled.connect(self.leftEarUpAxisNegativeYToggled)

        self.leftEarUpAxisPositiveZ = wdg.QPushButton('+ Z')
        self.leftEarUpAxisPositiveZ.setFixedWidth(50)
        self.leftEarUpAxisPositiveZ.setCheckable(True)
        earsPhysicsLeftEarAimLyt.addWidget(self.leftEarUpAxisPositiveZ)
        self.leftEarUpAxisPositiveZ.toggled.connect(self.leftEarUpAxisPositiveZToggled)

        self.leftEarUpAxisNegativeZ = wdg.QPushButton('- Z')
        self.leftEarUpAxisNegativeZ.setFixedWidth(50)
        self.leftEarUpAxisNegativeZ.setCheckable(True)
        earsPhysicsLeftEarAimLyt.addWidget(self.leftEarUpAxisNegativeZ)
        self.leftEarUpAxisNegativeZ.toggled.connect(self.leftEarUpAxisNegativeZToggled)

        self.leftEarXFormOffsetSpinBox = wdg.QDoubleSpinBox()
        self.leftEarXFormOffsetSpinBox.setFixedWidth(90)
        self.leftEarXFormOffsetSpinBox.setFixedHeight(25)
        self.leftEarXFormOffsetSpinBox.setMinimum(1)
        self.leftEarXFormOffsetSpinBox.setMaximum(200)
        self.leftEarXFormOffsetSpinBox.setSingleStep(1.0)
        self.leftEarXFormOffsetSpinBox.setValue(20)
        earsPhysicsLeftEarAimLyt.addWidget(self.leftEarXFormOffsetSpinBox)

        self.leftEarUpAxisGroup = wdg.QButtonGroup()
        self.leftEarUpAxisGroup.setExclusive(True)
        self.leftEarUpAxisGroup.addButton(self.leftEarUpAxisPositiveX)
        self.leftEarUpAxisGroup.addButton(self.leftEarUpAxisNegativeX)
        self.leftEarUpAxisGroup.addButton(self.leftEarUpAxisPositiveY)
        self.leftEarUpAxisGroup.addButton(self.leftEarUpAxisNegativeY)
        self.leftEarUpAxisGroup.addButton(self.leftEarUpAxisPositiveZ)
        self.leftEarUpAxisGroup.addButton(self.leftEarUpAxisNegativeZ)

        # Goal Setup Widgets
        self.earsPhysicsGoalSmoothnessLabel = wdg.QLabel('Goal Smoothness: ')
        earsPhysicsGoalLyt.addWidget(self.earsPhysicsGoalSmoothnessLabel)

        self.earsPhysicsGoalSmoothnessSpinbox = wdg.QDoubleSpinBox()
        self.earsPhysicsGoalSmoothnessSpinbox.setFixedHeight(25)
        self.earsPhysicsGoalSmoothnessSpinbox.setMinimum(0.0)
        self.earsPhysicsGoalSmoothnessSpinbox.setMaximum(4.0)
        self.earsPhysicsGoalSmoothnessSpinbox.setSingleStep(0.1)
        self.earsPhysicsGoalSmoothnessSpinbox.setValue(2.0)
        earsPhysicsGoalLyt.addWidget(self.earsPhysicsGoalSmoothnessSpinbox)

        self.earsPhysicsGoalWeightLabel = wdg.QLabel('Goal Weight: ')
        earsPhysicsGoalLyt.addWidget(self.earsPhysicsGoalWeightLabel)

        self.earsPhysicsGoalWeightSpinbox = wdg.QDoubleSpinBox()
        self.earsPhysicsGoalWeightSpinbox.setFixedHeight(25)
        self.earsPhysicsGoalWeightSpinbox.setMinimum(0.0)
        self.earsPhysicsGoalWeightSpinbox.setMaximum(1.0)
        self.earsPhysicsGoalWeightSpinbox.setSingleStep(0.01)
        self.earsPhysicsGoalWeightSpinbox.setDecimals(2)
        self.earsPhysicsGoalWeightSpinbox.setValue(0.62)
        earsPhysicsGoalLyt.addWidget(self.earsPhysicsGoalWeightSpinbox)

        # Rotation Frames Offset Widgets
        self.earsRotationOffsetLabel = wdg.QLabel('Rotation Offset')
        earsRotationOffsetLyt.addWidget(self.earsRotationOffsetLabel)

        self.earsRotationOffset1fButton = wdg.QPushButton('1')
        self.earsRotationOffset1fButton.setCheckable(True)
        earsRotationOffsetLyt.addWidget(self.earsRotationOffset1fButton)
        self.earsRotationOffset1fButton.toggled.connect(self.earsRotationOffset1fButtonToggled)

        self.earsRotationOffset2fButton = wdg.QPushButton('2')
        self.earsRotationOffset2fButton.setCheckable(True)
        self.earsRotationOffset2fButton.setChecked(True)
        earsRotationOffsetLyt.addWidget(self.earsRotationOffset2fButton)
        self.earsRotationOffset2fButton.toggled.connect(self.earsRotationOffset2fButtonToggled)

        self.earsRotationOffset3fButton = wdg.QPushButton('3')
        self.earsRotationOffset3fButton.setCheckable(True)
        earsRotationOffsetLyt.addWidget(self.earsRotationOffset3fButton)
        self.earsRotationOffset3fButton.toggled.connect(self.earsRotationOffset3fButtonToggled)

        self.earsRotationOffset4fButton = wdg.QPushButton('4')
        self.earsRotationOffset4fButton.setCheckable(True)
        earsRotationOffsetLyt.addWidget(self.earsRotationOffset4fButton)
        self.earsRotationOffset4fButton.toggled.connect(self.earsRotationOffset4fButtonToggled)

        self.earsRotationOffsetGroup = wdg.QButtonGroup()
        self.earsRotationOffsetGroup.setExclusive(True)
        self.earsRotationOffsetGroup.addButton(self.earsRotationOffset1fButton)
        self.earsRotationOffsetGroup.addButton(self.earsRotationOffset2fButton)
        self.earsRotationOffsetGroup.addButton(self.earsRotationOffset3fButton)
        self.earsRotationOffsetGroup.addButton(self.earsRotationOffset4fButton)

        # Generate Widget
        self.generateEarsButton = wdg.QPushButton('GENERATE EARS OVERLAP')
        self.generateEarsButton.setFixedWidth(200)
        self.generateEarsButton.setFixedHeight(40)
        earsGenerateLyt.addWidget(self.generateEarsButton)
        self.generateEarsButton.pressed.connect(self.generateEarsButtonPressed)

        self.generateEarsRotationOffsetButton = wdg.QPushButton('GENERATE EARS ROTATION OFFSET')
        self.generateEarsRotationOffsetButton.setFixedWidth(200)
        self.generateEarsRotationOffsetButton.setFixedHeight(40)
        earsGenerateLyt.addWidget(self.generateEarsRotationOffsetButton)
        self.generateEarsRotationOffsetButton.pressed.connect(self.generateEarRotationOffsetButtonPressed)

        # Aim String Widgets
        # Target Axis Widgets
        targetAxisLabel = wdg.QLabel('Target Aim Axis  ')
        aimStringTargetAxisLyt.addWidget(targetAxisLabel)

        self.targetAxisPositiveXButton = wdg.QPushButton('+X')
        self.targetAxisPositiveXButton.setFixedWidth(50)
        self.targetAxisPositiveXButton.setCheckable(True)
        self.targetAxisPositiveXButton.setChecked(True)
        aimStringTargetAxisLyt.addWidget(self.targetAxisPositiveXButton)
        self.targetAxisPositiveXButton.toggled.connect(self.targetAxisPositiveXButtonToggled)

        self.targetAxisNegativeXButton = wdg.QPushButton('-X')
        self.targetAxisNegativeXButton.setFixedWidth(50)
        self.targetAxisNegativeXButton.setCheckable(True)
        aimStringTargetAxisLyt.addWidget(self.targetAxisNegativeXButton)
        self.targetAxisNegativeXButton.toggled.connect(self.targetAxisNegativeXButtonToggled)

        self.targetAxisPositiveYButton = wdg.QPushButton('+Y')
        self.targetAxisPositiveYButton.setFixedWidth(50)
        self.targetAxisPositiveYButton.setCheckable(True)
        aimStringTargetAxisLyt.addWidget(self.targetAxisPositiveYButton)
        self.targetAxisPositiveYButton.toggled.connect(self.targetAxisPositiveYButtonToggled)

        self.targetAxisNegativeYButton = wdg.QPushButton('-Y')
        self.targetAxisNegativeYButton.setFixedWidth(50)
        self.targetAxisNegativeYButton.setCheckable(True)
        aimStringTargetAxisLyt.addWidget(self.targetAxisNegativeYButton)
        self.targetAxisNegativeYButton.toggled.connect(self.targetAxisNegativeYButtonToggled)

        self.targetAxisPositiveZButton = wdg.QPushButton('+Z')
        self.targetAxisPositiveZButton.setFixedWidth(50)
        self.targetAxisPositiveZButton.setCheckable(True)
        aimStringTargetAxisLyt.addWidget(self.targetAxisPositiveZButton)
        self.targetAxisPositiveZButton.toggled.connect(self.targetAxisPositiveZButtonToggled)

        self.targetAxisNegativeZButton = wdg.QPushButton('-Z')
        self.targetAxisNegativeZButton.setFixedWidth(50)
        self.targetAxisNegativeZButton.setCheckable(True)
        aimStringTargetAxisLyt.addWidget(self.targetAxisNegativeZButton)
        self.targetAxisNegativeZButton.toggled.connect(self.targetAxisNegativeZButtonToggled)

        self.targetAxisXFormOffsetDoubleSpin = wdg.QDoubleSpinBox()
        self.targetAxisXFormOffsetDoubleSpin.setFixedWidth(90)
        self.targetAxisXFormOffsetDoubleSpin.setFixedHeight(25)
        self.targetAxisXFormOffsetDoubleSpin.setMinimum(1)
        self.targetAxisXFormOffsetDoubleSpin.setMaximum(200)
        self.targetAxisXFormOffsetDoubleSpin.setSingleStep(1.0)
        self.targetAxisXFormOffsetDoubleSpin.setValue(20)
        aimStringTargetAxisLyt.addWidget(self.targetAxisXFormOffsetDoubleSpin)

        self.targetAxisGroup = wdg.QButtonGroup()
        self.targetAxisGroup.setExclusive(True)
        self.targetAxisGroup.addButton(self.targetAxisPositiveXButton)
        self.targetAxisGroup.addButton(self.targetAxisNegativeXButton)
        self.targetAxisGroup.addButton(self.targetAxisPositiveYButton)
        self.targetAxisGroup.addButton(self.targetAxisNegativeYButton)
        self.targetAxisGroup.addButton(self.targetAxisPositiveZButton)
        self.targetAxisGroup.addButton(self.targetAxisNegativeZButton)

        # Roots Aim Axis Widgets
        rootsAxisLabel = wdg.QLabel('Roots Aim Axis  ')
        aimStringRootsAxisLyt.addWidget(rootsAxisLabel)

        self.rootsAxisPositiveXButton = wdg.QPushButton('+X')
        self.rootsAxisPositiveXButton.setFixedWidth(50)
        self.rootsAxisPositiveXButton.setCheckable(True)
        self.rootsAxisPositiveXButton.setChecked(True)
        aimStringRootsAxisLyt.addWidget(self.rootsAxisPositiveXButton)
        self.rootsAxisPositiveXButton.toggled.connect(self.rootsAxisPositiveXButtonToggled)

        self.rootsAxisNegativeXButton = wdg.QPushButton('-X')
        self.rootsAxisNegativeXButton.setFixedWidth(50)
        self.rootsAxisNegativeXButton.setCheckable(True)
        aimStringRootsAxisLyt.addWidget(self.rootsAxisNegativeXButton)
        self.rootsAxisNegativeXButton.toggled.connect(self.rootsAxisNegativeXButtonToggled)

        self.rootsAxisPositiveYButton = wdg.QPushButton('+Y')
        self.rootsAxisPositiveYButton.setFixedWidth(50)
        self.rootsAxisPositiveYButton.setCheckable(True)
        aimStringRootsAxisLyt.addWidget(self.rootsAxisPositiveYButton)
        self.rootsAxisPositiveYButton.toggled.connect(self.rootsAxisPositiveYButtonToggled)

        self.rootsAxisNegativeYButton = wdg.QPushButton('-Y')
        self.rootsAxisNegativeYButton.setFixedWidth(50)
        self.rootsAxisNegativeYButton.setCheckable(True)
        aimStringRootsAxisLyt.addWidget(self.rootsAxisNegativeYButton)
        self.rootsAxisNegativeYButton.toggled.connect(self.rootsAxisNegativeYButtonToggled)

        self.rootsAxisPositiveZButton = wdg.QPushButton('+Z')
        self.rootsAxisPositiveZButton.setFixedWidth(50)
        self.rootsAxisPositiveZButton.setCheckable(True)
        aimStringRootsAxisLyt.addWidget(self.rootsAxisPositiveZButton)
        self.rootsAxisPositiveZButton.toggled.connect(self.rootsAxisPositiveZButtonToggled)

        self.rootsAxisNegativeZButton = wdg.QPushButton('-Z')
        self.rootsAxisNegativeZButton.setFixedWidth(50)
        self.rootsAxisNegativeZButton.setCheckable(True)
        aimStringRootsAxisLyt.addWidget(self.rootsAxisNegativeZButton)
        self.rootsAxisNegativeZButton.toggled.connect(self.rootsAxisNegativeZButtonToggled)

        self.rootsAxisGroup = wdg.QButtonGroup()
        self.rootsAxisGroup.setExclusive(True)
        self.rootsAxisGroup.addButton(self.rootsAxisPositiveXButton)
        self.rootsAxisGroup.addButton(self.rootsAxisNegativeXButton)
        self.rootsAxisGroup.addButton(self.rootsAxisPositiveYButton)
        self.rootsAxisGroup.addButton(self.rootsAxisNegativeYButton)
        self.rootsAxisGroup.addButton(self.rootsAxisPositiveZButton)
        self.rootsAxisGroup.addButton(self.rootsAxisNegativeZButton)

        # Offset Widgets
        stringOffsetLabel = wdg.QLabel('Offset (Frames) ')
        aimStringOffsetLyt.addWidget(stringOffsetLabel)

        self.stringOffset1fButton = wdg.QPushButton('1')
        self.stringOffset1fButton.setCheckable(True)
        self.stringOffset1fButton.setChecked(True)
        self.stringOffset1fButton.setFixedWidth(100)
        aimStringOffsetLyt.addWidget(self.stringOffset1fButton)
        self.stringOffset1fButton.toggled.connect(self.stringOffset1fButtonToggled)

        self.stringOffset2fButton = wdg.QPushButton('2')
        self.stringOffset2fButton.setCheckable(True)
        self.stringOffset2fButton.setFixedWidth(100)
        aimStringOffsetLyt.addWidget(self.stringOffset2fButton)
        self.stringOffset2fButton.toggled.connect(self.stringOffset2fButtonToggled)

        self.stringOffset3fButton = wdg.QPushButton('3')
        self.stringOffset3fButton.setCheckable(True)
        self.stringOffset3fButton.setFixedWidth(100)
        aimStringOffsetLyt.addWidget(self.stringOffset3fButton)
        self.stringOffset3fButton.toggled.connect(self.stringOffset3fButtonToggled)

        self.stringOffset4fButton = wdg.QPushButton('4')
        self.stringOffset4fButton.setCheckable(True)
        self.stringOffset4fButton.setFixedWidth(100)
        aimStringOffsetLyt.addWidget(self.stringOffset4fButton)
        self.stringOffset4fButton.toggled.connect(self.stringOffset4fButtonToggled)

        self.stringOffsetGroup = wdg.QButtonGroup()
        self.stringOffsetGroup.setExclusive(True)
        self.stringOffsetGroup.addButton(self.stringOffset1fButton)
        self.stringOffsetGroup.addButton(self.stringOffset2fButton)
        self.stringOffsetGroup.addButton(self.stringOffset3fButton)
        self.stringOffsetGroup.addButton(self.stringOffset4fButton)

        # Aim String Generate Widgets
        self.stringGenerateAimSetupButton = wdg.QPushButton('GENERATE AIM SETUP')
        self.stringGenerateAimSetupButton.setFixedWidth(150)
        self.stringGenerateAimSetupButton.setFixedHeight(40)
        aimStringGenerateLyt.addWidget(self.stringGenerateAimSetupButton)
        self.stringGenerateAimSetupButton.pressed.connect(self.stringGenerateAimSetupButtonPressed)

        self.stringSelectControlsButton = wdg.QPushButton('SELECT CONTROLS')
        self.stringSelectControlsButton.setFixedWidth(150)
        self.stringSelectControlsButton.setFixedHeight(40)
        aimStringGenerateLyt.addWidget(self.stringSelectControlsButton)
        self.stringSelectControlsButton.pressed.connect(self.stringSelectControlsButtonPressed)

        self.stringGenerateBakeButton = wdg.QPushButton('BAKE TO CONTROLS')
        self.stringGenerateBakeButton.setFixedWidth(150)
        self.stringGenerateBakeButton.setFixedHeight(40)
        aimStringGenerateLyt.addWidget(self.stringGenerateBakeButton)
        self.stringGenerateBakeButton.pressed.connect(self.stringGenerateBakeButtonPressed)

        ##### BOTTOM LAYOUT WIDGETS #####
        # Notes Labels
        blankWdg = wdg.QWidget()
        blankWdg.setFixedHeight(10)
        instructionsLyt.addWidget(blankWdg)

    ############### ENGINE ###############
    ######################################
    ######################################

    ##### Menu Bar Signals #####
    def howToUseActionTriggered(self):
        msg = wdg.QMessageBox(self)
        msg.setWindowTitle('Ears Overlap - How To Use')
        msg.setText(
            'INSTRUCTIONS:\n\n'
            '1. Check the Up Axis for both Right and Left ear.\n'
            '2. Choose the amount of overlap on the Goal Smoothness and Goal Weight.\n'
            '3. Select FIRST the right ear, SECOND the left ear.\n'
            '4. Click Generate Ears Overlap button.\n'
            '5. Choose how many frames of offset do you need for the child controls.\n'
            '6. ONE EAR AT A TIME, choose the child controls in hierarchy order.\n'
            '7. Click the Generate Ears Rotation Offset button.\n')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setModal(False)
        msg.show()

    ##### Tab Signal #####
    def tabWdgCurrentChanged(self, index):
        currentTab = self.tabWdg.widget(index)

        if index == 0:
            self.setFixedSize(650, 410)

        if index == 1:
            self.setFixedSize(650, 330)

        if index == 2:
            self.setFixedSize(650, 420)

        if index == 3:
            self.setFixedSize(650, 385)

    ##### Aim Space Tab Signals #####
    # Axis Signals
    def positiveXAxisButtonToggled(self, checked):
        if checked:
            self.selectedAxis = '+X'

    def negativeXAxisButtonToggled(self, checked):
        if checked:
            self.selectedAxis = '-X'

    def positiveYAxisButtonToggled(self, checked):
        if checked:
            self.selectedAxis = '+Y'

    def negativeYAxisButtonToggled(self, checked):
        if checked:
            self.selectedAxis = '-Y'

    def positiveZButtonToggled(self, checked):
        if checked:
            self.selectedAxis = '+Z'

    def negativeZAxisButtonToggled(self, checked):
        if checked:
            self.selectedAxis = '-Z'

    # World Space Signals
    def worldSpaceConversionYesButtonToggled(self, checked):
        if checked:
            self.selectedWorldSpaceConversion = 'Yes'

    def worldSpaceConversionNoButtonToggled(self, checked):
        if checked:
            self.selectedWorldSpaceConversion = 'No'

    # Create Button Signal
    def createAimSetupButtonPressed(self):

        xformValue = self.xformOffsetSpinBox.value()
        currentNmp = cmds.namespaceInfo(cur=True)
        cmds.namespace(set=':')

        sel = cmds.ls(sl=True)
        if len(sel) == 0:
            # Reminds you to select something for this to work
            cmds.confirmDialog(title='Confirm', message='You need to select something first')
        else:
            # Makes a list (array) of your selected objects
            array = cmds.ls(sl=True)
            # For every item you have selected, do this for loop
            for item in array:
                # Redefines the item in the array as aimObj
                ctrl = item
                # Creates a locator with the selected object's name with _temp_aimspace_target appended
                rootAimLoc = cmds.spaceLocator(n=f"{ctrl}_temp_aimspace_root")
                offsetAimLoc = cmds.spaceLocator(n=f"{ctrl}_temp_aimspace_offset")
                targetAimLoc = cmds.spaceLocator(n=f"{ctrl}_temp_aimspace_target")

                cmds.parent(offsetAimLoc[0], rootAimLoc[0])

                # Sets size of locator
                cmds.setAttr(f"{targetAimLoc[0]}.localScaleX", 5)
                cmds.setAttr(f"{targetAimLoc[0]}.localScaleY", 5)
                cmds.setAttr(f"{targetAimLoc[0]}.localScaleZ", 5)

                # Constraints root to existing motion
                cmds.select(ctrl, r=True)
                cmds.select(rootAimLoc, tgl=True)
                cmds.pointConstraint()
                cmds.orientConstraint()

                # Select Objects
                cmds.select(ctrl, r=True)
                cmds.select(targetAimLoc, tgl=True)

                # Puts the target off in space based on the chosen axis
                # The offset values are arbitrary. Alter to fit your scene
                if self.selectedAxis == '+X':
                    cmds.pointConstraint()
                    cmds.orientConstraint()

                    cmds.select(targetAimLoc[0], r=True)
                    cmds.delete(cn=True)
                    cmds.xform(os=True, r=True, translation=(xformValue, 0, 0))

                else:

                    if self.selectedAxis == '+Y':
                        cmds.pointConstraint()
                        cmds.orientConstraint()

                        cmds.select(targetAimLoc[0], r=True)
                        cmds.delete(cn=True)
                        cmds.xform(os=True, r=True, translation=(0, xformValue, 0))

                    else:

                        if self.selectedAxis == '+Z':
                            cmds.pointConstraint()
                            cmds.orientConstraint()

                            cmds.select(targetAimLoc[0], r=True)
                            cmds.delete(cn=True)
                            cmds.xform(os=True, r=True, translation=(0, 0, xformValue))

                        else:

                            if self.selectedAxis == '-X':
                                cmds.pointConstraint()
                                cmds.orientConstraint()

                                cmds.select(targetAimLoc[0], r=True)
                                cmds.delete(cn=True)
                                cmds.xform(os=True, r=True, translation=(xformValue * -1, 0, 0))

                            else:

                                if self.selectedAxis == '-Y':
                                    cmds.pointConstraint()
                                    cmds.orientConstraint()

                                    cmds.select(targetAimLoc[0], r=True)
                                    cmds.delete(cn=True)
                                    cmds.xform(os=True, r=True, translation=(0, xformValue * -1, 0))

                                else:

                                    if self.selectedAxis == '-Z':
                                        cmds.pointConstraint()
                                        cmds.orientConstraint()

                                        cmds.select(targetAimLoc[0], r=True)
                                        cmds.delete(cn=True)
                                        cmds.xform(os=True, r=True, translation=(0, 0, xformValue * -1))

                cmds.select(ctrl, r=True)
                cmds.select(targetAimLoc[0], tgl=True)
                cmds.parentConstraint(mo=True)

                # Bakes the root and target. Then deletes constraints on them
                cmds.select(targetAimLoc[0], r=True)
                cmds.select(rootAimLoc[0], tgl=True)
                bake()

                # Setting different aim conditions depending on X Y Z choice
                cmds.select(targetAimLoc[0], r=True)
                cmds.select(offsetAimLoc[0], tgl=True)

                if self.selectedAxis == '+X':
                    cmds.aimConstraint(mo=True, w=1, aim=(1, 0, 0), u=(0, 0, 1), wut='objectRotation', wu=(0, 0, 1),
                                       wuo=rootAimLoc[0])
                else:
                    if self.selectedAxis == '+Y':
                        cmds.aimConstraint(mo=True, w=1, aim=(0, 1, 0), u=(0, 0, 1), wut='objectRotation', wu=(0, 0, 1),
                                           wuo=rootAimLoc[0])
                    else:
                        if self.selectedAxis == '+Z':
                            cmds.aimConstraint(mo=True, w=1, aim=(0, 0, 1), u=(0, 1, 0), wut='objectRotation',
                                               wu=(0, 1, 0), wuo=rootAimLoc[0])
                        else:
                            if self.selectedAxis == '-X':
                                cmds.aimConstraint(mo=True, w=1, aim=(-1, 0, 0), u=(0, 0, 1), wut='objectRotation',
                                                   wu=(0, 0, 1), wuo=rootAimLoc[0])
                            else:
                                if self.selectedAxis == '-Y':
                                    cmds.aimConstraint(mo=True, w=1, aim=(0, -1, 0), u=(0, 0, 1), wut='objectRotation',
                                                       wu=(0, 0, 1), wuo=rootAimLoc[0])
                                else:
                                    if self.selectedAxis == '-Z':
                                        cmds.aimConstraint(mo=True, w=1, aim=(0, 0, -1), u=(0, 1, 0),
                                                           wut='objectRotation', wu=(0, 1, 0), wuo=rootAimLoc[0])

                # World Space Conversion
                if self.selectedWorldSpaceConversion == 'No':
                    cmds.select(ctrl, r=True)
                    cmds.select(rootAimLoc[0], tgl=True)
                    cmds.pointConstraint()

                    cmds.select(offsetAimLoc[0], r=True)
                    cmds.select(ctrl, tgl=True)
                    cmds.orientConstraint()

                else:
                    cmds.select(rootAimLoc[0], r=True)
                    cmds.select(ctrl, tgl=True)
                    cmds.pointConstraint()

                    cmds.select(offsetAimLoc[0], r=True)
                    cmds.select(ctrl, tgl=True)
                    cmds.orientConstraint()

                cmds.select(targetAimLoc[0])
                if cmds.objExists(f"{currentNmp}:rig_layer"):
                    cmds.editDisplayLayerMembers(f"{currentNmp}:rig_layer", cmds.ls(sl=True), nr=True)

        # Restoring Original Namespace
        cmds.namespace(set=currentNmp)

    ##### Overlap Physics Signals #####
    def addPhysicsButtonPressed(self):
        goalSmoothnessValue = self.goalSmoothnessNumeric.value()
        goalWeightValue = self.goalWeightNumeric.value()
        addPhysics(goalSmoothnessValue, goalWeightValue)

    ##### Overlap Ears Signals #####
    # Right Ear Aim Signals
    def rightEarUpAxisPositiveXToggled(self, checked):
        if checked:
            self.rightEarSelectedAxis = '+X'

    def rightEarUpAxisNegativeXToggled(self, checked):
        if checked:
            self.rightEarSelectedAxis = '-X'

    def rightEarUpAxisPositiveYToggled(self, checked):
        if checked:
            self.rightEarSelectedAxis = '+Y'

    def rightEarUpAxisNegativeYToggled(self, checked):
        if checked:
            self.rightEarSelectedAxis = '-Y'

    def rightEarUpAxisPositiveZToggled(self, checked):
        if checked:
            self.rightEarSelectedAxis = '+Z'

    def rightEarUpAxisNegativeZToggled(self, checked):
        if checked:
            self.rightEarSelectedAxis = '-Z'

    # Left Ear Aim Signals
    def leftEarUpAxisPositiveXToggled(self, checked):
        if checked:
            self.leftEarSelectedAxis = '+X'

    def leftEarUpAxisNegativeXToggled(self, checked):
        if checked:
            self.leftEarSelectedAxis = '-X'

    def leftEarUpAxisPositiveYToggled(self, checked):
        if checked:
            self.leftEarSelectedAxis = '+Y'

    def leftEarUpAxisNegativeYToggled(self, checked):
        if checked:
            self.leftEarSelectedAxis = '-Y'

    def leftEarUpAxisPositiveZToggled(self, checked):
        if checked:
            self.leftEarSelectedAxis = '+Z'

    def leftEarUpAxisNegativeZToggled(self, checked):
        if checked:
            self.leftEarSelectedAxis = '-Z'

    # Generate Ears Button Signal
    def generateEarsButtonPressed(self):

        rightEarXFormValue = self.rightEarXFormOffsetSpinBox.value()
        leftEarXFormValue = self.leftEarXFormOffsetSpinBox.value()
        currentNmp = cmds.namespaceInfo(cur=True)
        cmds.namespace(set=':')

        sel = cmds.ls(sl=True)
        if len(sel) == 0 or len(sel) > 2:
            # Reminds you to select something for this to work
            cmds.confirmDialog(title='Confirm', message='You need to select something ONLY two controls')

        else:
            # Makes a list (array) of your selected objects
            array = cmds.ls(sl=True)

            ##########################################################
            ##### Aim Space Conversion for first object in array #####
            ##########################################################

            rightCtrl = array[0]
            # Creates a locator with the selected object's name with _temp_aimspace_target appended
            rightRootAimLoc = cmds.spaceLocator(n=f"{rightCtrl}_temp_aimspace_root")
            rightOffsetAimLoc = cmds.spaceLocator(n=f"{rightCtrl}_temp_aimspace_offset")
            rightTargetAimLoc = cmds.spaceLocator(n=f"{rightCtrl}_temp_aimspace_target")

            cmds.parent(rightOffsetAimLoc[0], rightRootAimLoc[0])

            # Sets size of locator
            cmds.setAttr(f"{rightTargetAimLoc[0]}.localScaleX", 5)
            cmds.setAttr(f"{rightTargetAimLoc[0]}.localScaleY", 5)
            cmds.setAttr(f"{rightTargetAimLoc[0]}.localScaleZ", 5)

            # Constraints root to existing motion
            cmds.select(rightCtrl, r=True)
            cmds.select(rightRootAimLoc, tgl=True)
            cmds.pointConstraint()
            cmds.orientConstraint()

            # Select Objects
            cmds.select(rightCtrl, r=True)
            cmds.select(rightTargetAimLoc, tgl=True)

            # Puts the target off in space based on the chosen axis
            # The offset values are arbitrary. Alter to fit your scene
            if self.rightEarSelectedAxis == '+X':
                cmds.pointConstraint()
                cmds.orientConstraint()

                cmds.select(rightTargetAimLoc[0], r=True)
                cmds.delete(cn=True)
                cmds.xform(os=True, r=True, translation=(rightEarXFormValue, 0, 0))

            else:

                if self.rightEarSelectedAxis == '+Y':
                    cmds.pointConstraint()
                    cmds.orientConstraint()

                    cmds.select(rightTargetAimLoc[0], r=True)
                    cmds.delete(cn=True)
                    cmds.xform(os=True, r=True, translation=(0, rightEarXFormValue, 0))

                else:

                    if self.rightEarSelectedAxis == '+Z':
                        cmds.pointConstraint()
                        cmds.orientConstraint()

                        cmds.select(rightTargetAimLoc[0], r=True)
                        cmds.delete(cn=True)
                        cmds.xform(os=True, r=True, translation=(0, 0, rightEarXFormValue))

                    else:

                        if self.rightEarSelectedAxis == '-X':
                            cmds.pointConstraint()
                            cmds.orientConstraint()

                            cmds.select(rightTargetAimLoc[0], r=True)
                            cmds.delete(cn=True)
                            cmds.xform(os=True, r=True, translation=(rightEarXFormValue * -1, 0, 0))

                        else:

                            if self.rightEarSelectedAxis == '-Y':
                                cmds.pointConstraint()
                                cmds.orientConstraint()

                                cmds.select(rightTargetAimLoc[0], r=True)
                                cmds.delete(cn=True)
                                cmds.xform(os=True, r=True, translation=(0, rightEarXFormValue * -1, 0))

                            else:

                                if self.rightEarSelectedAxis == '-Z':
                                    cmds.pointConstraint()
                                    cmds.orientConstraint()

                                    cmds.select(rightTargetAimLoc[0], r=True)
                                    cmds.delete(cn=True)
                                    cmds.xform(os=True, r=True, translation=(0, 0, rightEarXFormValue * -1))

            cmds.select(rightCtrl, r=True)
            cmds.select(rightTargetAimLoc[0], tgl=True)
            cmds.parentConstraint(mo=True)

            # Bakes the root and target. Then deletes constraints on them
            cmds.select(rightTargetAimLoc[0], r=True)
            cmds.select(rightRootAimLoc[0], tgl=True)
            bake()

            # Setting different aim conditions depending on X Y Z choice
            cmds.select(rightTargetAimLoc[0], r=True)
            cmds.select(rightOffsetAimLoc[0], tgl=True)

            if self.rightEarSelectedAxis == '+X':
                cmds.aimConstraint(mo=True, w=1, aim=(1, 0, 0), u=(0, 0, 1), wut='objectRotation', wu=(0, 0, 1),
                                   wuo=rightRootAimLoc[0])
            else:
                if self.rightEarSelectedAxis == '+Y':
                    cmds.aimConstraint(mo=True, w=1, aim=(0, 1, 0), u=(0, 0, 1), wut='objectRotation', wu=(0, 0, 1),
                                       wuo=rightRootAimLoc[0])
                else:
                    if self.rightEarSelectedAxis == '+Z':
                        cmds.aimConstraint(mo=True, w=1, aim=(0, 0, 1), u=(0, 1, 0), wut='objectRotation', wu=(0, 1, 0),
                                           wuo=rightRootAimLoc[0])
                    else:
                        if self.rightEarSelectedAxis == '-X':
                            cmds.aimConstraint(mo=True, w=1, aim=(-1, 0, 0), u=(0, 0, 1), wut='objectRotation',
                                               wu=(0, 0, 1), wuo=rightRootAimLoc[0])
                        else:
                            if self.rightEarSelectedAxis == '-Y':
                                cmds.aimConstraint(mo=True, w=1, aim=(0, -1, 0), u=(0, 0, 1), wut='objectRotation',
                                                   wu=(0, 0, 1), wuo=rightRootAimLoc[0])
                            else:
                                if self.rightEarSelectedAxis == '-Z':
                                    cmds.aimConstraint(mo=True, w=1, aim=(0, 0, -1), u=(0, 1, 0), wut='objectRotation',
                                                       wu=(0, 1, 0), wuo=rightRootAimLoc[0])

            cmds.select(rightRootAimLoc[0], r=True)
            cmds.select(rightCtrl, tgl=True)
            cmds.pointConstraint()

            cmds.select(rightOffsetAimLoc[0], r=True)
            cmds.select(rightCtrl, tgl=True)
            cmds.orientConstraint()

            cmds.select(rightTargetAimLoc[0])
            if cmds.objExists(f"{currentNmp}:rig_layer"):
                cmds.editDisplayLayerMembers(f"{currentNmp}:rig_layer", cmds.ls(sl=True), nr=True)

            ###########################################################
            ##### Aim Space Conversion for second object in array #####
            ###########################################################

            leftCtrl = array[1]
            # Creates a locator with the selected object's name with _temp_aimspace_target appended
            leftRootAimLoc = cmds.spaceLocator(n=f"{leftCtrl}_temp_aimspace_root")
            leftOffsetAimLoc = cmds.spaceLocator(n=f"{leftCtrl}_temp_aimspace_offset")
            leftTargetAimLoc = cmds.spaceLocator(n=f"{leftCtrl}_temp_aimspace_target")

            cmds.parent(leftOffsetAimLoc[0], leftRootAimLoc[0])

            # Sets size of locator
            cmds.setAttr(f"{leftTargetAimLoc[0]}.localScaleX", 5)
            cmds.setAttr(f"{leftTargetAimLoc[0]}.localScaleY", 5)
            cmds.setAttr(f"{leftTargetAimLoc[0]}.localScaleZ", 5)

            # Constraints root to existing motion
            cmds.select(leftCtrl, r=True)
            cmds.select(leftRootAimLoc, tgl=True)
            cmds.pointConstraint()
            cmds.orientConstraint()

            # Select Objects
            cmds.select(leftCtrl, r=True)
            cmds.select(leftTargetAimLoc, tgl=True)

            # Puts the target off in space based on the chosen axis
            # The offset values are arbitrary. Alter to fit your scene
            if self.leftEarSelectedAxis == '+X':
                cmds.pointConstraint()
                cmds.orientConstraint()

                cmds.select(leftTargetAimLoc[0], r=True)
                cmds.delete(cn=True)
                cmds.xform(os=True, r=True, translation=(leftEarXFormValue, 0, 0))

            else:

                if self.leftEarSelectedAxis == '+Y':
                    cmds.pointConstraint()
                    cmds.orientConstraint()

                    cmds.select(leftTargetAimLoc[0], r=True)
                    cmds.delete(cn=True)
                    cmds.xform(os=True, r=True, translation=(0, leftEarXFormValue, 0))

                else:

                    if self.leftEarSelectedAxis == '+Z':
                        cmds.pointConstraint()
                        cmds.orientConstraint()

                        cmds.select(leftTargetAimLoc[0], r=True)
                        cmds.delete(cn=True)
                        cmds.xform(os=True, r=True, translation=(0, 0, leftEarXFormValue))

                    else:

                        if self.leftEarSelectedAxis == '-X':
                            cmds.pointConstraint()
                            cmds.orientConstraint()

                            cmds.select(leftTargetAimLoc[0], r=True)
                            cmds.delete(cn=True)
                            cmds.xform(os=True, r=True, translation=(leftEarXFormValue * -1, 0, 0))

                        else:

                            if self.leftEarSelectedAxis == '-Y':
                                cmds.pointConstraint()
                                cmds.orientConstraint()

                                cmds.select(leftTargetAimLoc[0], r=True)
                                cmds.delete(cn=True)
                                cmds.xform(os=True, r=True, translation=(0, leftEarXFormValue * -1, 0))

                            else:

                                if self.leftEarSelectedAxis == '-Z':
                                    cmds.pointConstraint()
                                    cmds.orientConstraint()

                                    cmds.select(leftTargetAimLoc[0], r=True)
                                    cmds.delete(cn=True)
                                    cmds.xform(os=True, r=True, translation=(0, 0, leftEarXFormValue * -1))

            cmds.select(leftCtrl, r=True)
            cmds.select(leftTargetAimLoc[0], tgl=True)
            cmds.parentConstraint(mo=True)

            # Bakes the root and target. Then deletes constraints on them
            cmds.select(leftTargetAimLoc[0], r=True)
            cmds.select(leftRootAimLoc[0], tgl=True)
            bake()

            # Setting different aim conditions depending on X Y Z choice
            cmds.select(leftTargetAimLoc[0], r=True)
            cmds.select(leftOffsetAimLoc[0], tgl=True)

            if self.leftEarSelectedAxis == '+X':
                cmds.aimConstraint(mo=True, w=1, aim=(1, 0, 0), u=(0, 0, 1), wut='objectRotation', wu=(0, 0, 1),
                                   wuo=leftRootAimLoc[0])
            else:
                if self.leftEarSelectedAxis == '+Y':
                    cmds.aimConstraint(mo=True, w=1, aim=(0, 1, 0), u=(0, 0, 1), wut='objectRotation', wu=(0, 0, 1),
                                       wuo=leftRootAimLoc[0])
                else:
                    if self.leftEarSelectedAxis == '+Z':
                        cmds.aimConstraint(mo=True, w=1, aim=(0, 0, 1), u=(0, 1, 0), wut='objectRotation', wu=(0, 1, 0),
                                           wuo=leftRootAimLoc[0])
                    else:
                        if self.leftEarSelectedAxis == '-X':
                            cmds.aimConstraint(mo=True, w=1, aim=(-1, 0, 0), u=(0, 0, 1), wut='objectRotation',
                                               wu=(0, 0, 1), wuo=leftRootAimLoc[0])
                        else:
                            if self.leftEarSelectedAxis == '-Y':
                                cmds.aimConstraint(mo=True, w=1, aim=(0, -1, 0), u=(0, 0, 1), wut='objectRotation',
                                                   wu=(0, 0, 1), wuo=leftRootAimLoc[0])
                            else:
                                if self.leftEarSelectedAxis == '-Z':
                                    cmds.aimConstraint(mo=True, w=1, aim=(0, 0, -1), u=(0, 1, 0), wut='objectRotation',
                                                       wu=(0, 1, 0), wuo=leftRootAimLoc[0])

            cmds.select(leftRootAimLoc[0], r=True)
            cmds.select(leftCtrl, tgl=True)
            cmds.pointConstraint()

            cmds.select(leftOffsetAimLoc[0], r=True)
            cmds.select(leftCtrl, tgl=True)
            cmds.orientConstraint()

            cmds.select(leftTargetAimLoc[0])
            if cmds.objExists(f"{currentNmp}:rig_layer"):
                cmds.editDisplayLayerMembers(f"{currentNmp}:rig_layer", cmds.ls(sl=True), nr=True)

        # Creates locators setup for ears physics
        masterEarsPhysicsLoc = cmds.spaceLocator(n='masterEarsPhysicsLoc')

        cmds.select(rightTargetAimLoc, r=True)
        cmds.select(masterEarsPhysicsLoc, tgl=True)
        cmds.pointConstraint()

        cmds.select(leftTargetAimLoc, r=True)
        cmds.select(masterEarsPhysicsLoc, tgl=True)
        cmds.pointConstraint()

        cmds.select(masterEarsPhysicsLoc, r=True)
        bake()

        rightEarPhysicsLoc = cmds.spaceLocator(n='rightEarPhysicsLoc')
        cmds.parent(rightEarPhysicsLoc, masterEarsPhysicsLoc)

        leftEarPhysicsLoc = cmds.spaceLocator(n='leftEarPhysicsLoc')
        cmds.parent(leftEarPhysicsLoc, masterEarsPhysicsLoc)

        cmds.select(rightTargetAimLoc, r=True)
        cmds.select(rightEarPhysicsLoc, tgl=True)
        cmds.pointConstraint()

        cmds.select(leftTargetAimLoc, r=True)
        cmds.select(leftEarPhysicsLoc, tgl=True)
        cmds.pointConstraint()

        cmds.select(rightEarPhysicsLoc, r=True)
        cmds.select(leftEarPhysicsLoc, tgl=True)
        bake()

        cmds.select(rightEarPhysicsLoc, r=True)
        cmds.select(rightTargetAimLoc, tgl=True)
        cmds.pointConstraint()

        cmds.select(leftEarPhysicsLoc, r=True)
        cmds.select(leftTargetAimLoc, tgl=True)
        cmds.pointConstraint()

        # Particle Physics
        earsGoalSmoothnessValue = self.earsPhysicsGoalSmoothnessSpinbox.value()
        earsGoalWeightValue = self.earsPhysicsGoalWeightSpinbox.value()
        cmds.select(masterEarsPhysicsLoc, r=True)
        addPhysics(earsGoalSmoothnessValue, earsGoalWeightValue)

        # Restoring Original Namespace
        cmds.namespace(set=currentNmp)

    # Rotation Offset Signals
    def earsRotationOffset1fButtonToggled(self, checked):
        if checked:
            self.earsRotationOffsetValue = 1

    def earsRotationOffset2fButtonToggled(self, checked):
        if checked:
            self.earsRotationOffsetValue = 2

    def earsRotationOffset3fButtonToggled(self, checked):
        if checked:
            self.earsRotationOffsetValue = 3

    def earsRotationOffset4fButtonToggled(self, checked):
        if checked:
            self.earsRotationOffsetValue = 4

    def generateEarRotationOffsetButtonPressed(self):
        # Step 1: Create Locators at the same location of the selected controls
        ctrlList = []
        locList = []
        currentSel = cmds.ls(selection=True)

        for item in cmds.ls(selection=True):
            ctrlList.append(item)

        for ctrl in currentSel:
            semicolonIndex = ctrl.find(':')
            locNewName = f"{ctrl[semicolonIndex + 1:]}_loc"
            currentLoc = cmds.spaceLocator(name=locNewName)
            locList.append(currentLoc[0])

        listLength = len(ctrlList)

        for index in range(listLength):
            cmds.select(locList[index], r=True)
            cmds.select(ctrlList[index], tgl=True)
            cmds.matchTransform()

        # Step 2: Constrain locators to controls (orient only), bake them, reverse constraint
        for index in range(listLength):
            cmds.select(ctrlList[index], r=True)
            cmds.select(locList[index], tgl=True)
            cmds.parentConstraint()

        for loc in locList:
            cmds.select(loc, r=True)
            bake()

        for index in range(listLength):
            cmds.select(locList[index], r=True)
            cmds.select(ctrlList[index], tgl=True)
            cmds.orientConstraint()

        # Step 3: Offsetting keys depending on time factor
        timeFactorResponse = self.earsRotationOffsetValue

        timeFactorInitial = timeFactorResponse
        timeFactorProgressive = timeFactorResponse
        inputTime = timeFactorResponse

        cmds.select(cl=True)

        for ctrl in locList:
            cmds.select(ctrl, tgl=True)

        for item in range(len(locList)):
            cmds.keyframe(locList[item], edit=True, relative=True, timeChange=timeFactorProgressive)
            timeFactorProgressive = timeFactorInitial + inputTime
            timeFactorInitial = timeFactorProgressive

    ##### String Aim Signals #####
    # Target Aim Axis Signals
    def targetAxisPositiveXButtonToggled(self, checked):
        if checked:
            self.targetAimSelectedAxis = '+X'

    def targetAxisNegativeXButtonToggled(self, checked):
        if checked:
            self.targetAimSelectedAxis = '-X'

    def targetAxisPositiveYButtonToggled(self, checked):
        if checked:
            self.targetAimSelectedAxis = '+Y'

    def targetAxisNegativeYButtonToggled(self, checked):
        if checked:
            self.targetAimSelectedAxis = '-Y'

    def targetAxisPositiveZButtonToggled(self, checked):
        if checked:
            self.targetAimSelectedAxis = '+Z'

    def targetAxisNegativeZButtonToggled(self, checked):
        if checked:
            self.targetAimSelectedAxis = '-Z'

    # Roots Aim Axis Signals
    def rootsAxisPositiveXButtonToggled(self, checked):
        if checked:
            self.rootsAimSelectedAxis = '+X'

    def rootsAxisNegativeXButtonToggled(self, checked):
        if checked:
            self.rootsAimSelectedAxis = '-X'

    def rootsAxisPositiveYButtonToggled(self, checked):
        if checked:
            self.rootsAimSelectedAxis = '+Y'

    def rootsAxisNegativeYButtonToggled(self, checked):
        if checked:
            self.rootsAimSelectedAxis = '-Y'

    def rootsAxisPositiveZButtonToggled(self, checked):
        if checked:
            self.rootsAimSelectedAxis = '+Z'

    def rootsAxisNegativeZButtonToggled(self, checked):
        if checked:
            self.rootsAimSelectedAxis = '-Z'

    # Offset (Frames) Signals
    def stringOffset1fButtonToggled(self, checked):
        if checked:
            self.stringOffsetValue = 1

    def stringOffset2fButtonToggled(self, checked):
        if checked:
            self.stringOffsetValue = 2

    def stringOffset3fButtonToggled(self, checked):
        if checked:
            self.stringOffsetValue = 3

    def stringOffset4fButtonToggled(self, checked):
        if checked:
            self.stringOffsetValue = 4

    # String Aim Generate Buttons Signals
    def stringGenerateAimSetupButtonPressed(self):
        targetXFormOffsetValue = self.targetAxisXFormOffsetDoubleSpin.value()
        self.sel = cmds.ls(selection=True)

        # Create Locators for the hierarchy chain
        for ctrl in self.sel:
            cmds.spaceLocator(n=f"{ctrl}_root")
            cmds.spaceLocator(n=f"{ctrl}_offset")

        cmds.spaceLocator(n='string_target')

        # Parent offset locators to root locators
        for ctrl in range(len(self.sel)):
            cmds.parent(f"{self.sel[ctrl]}_offset", f"{self.sel[ctrl]}_root")

        # Constraint the root locators to the respective control
        for ctrl in range(len(self.sel)):
            cmds.select(self.sel[ctrl], r=True)
            cmds.select(f"{self.sel[ctrl]}_root", tgl=True)
            cmds.pointConstraint()
            cmds.orientConstraint()

        # Positions the string_target locator
        cmds.select('string_target', r=True)
        cmds.select(self.sel[-1], tgl=True)
        cmds.MatchTransform()
        cmds.select('string_target', r=True)

        if self.targetAimSelectedAxis == '+X':
            cmds.xform(os=True, r=True, translation=(targetXFormOffsetValue, 0, 0))

        else:
            if self.targetAimSelectedAxis == '-X':
                cmds.xform(os=True, r=True, translation=(targetXFormOffsetValue * -1, 0, 0))

            else:
                if self.targetAimSelectedAxis == '+Y':
                    cmds.xform(os=True, r=True, translation=(0, targetXFormOffsetValue, 0))

                else:
                    if self.targetAimSelectedAxis == '-Y':
                        cmds.xform(os=True, r=True, translation=(0, targetXFormOffsetValue * -1, 0))

                    else:
                        if self.targetAimSelectedAxis == '+Z':
                            cmds.xform(os=True, r=True, tranlastion=(0, 0, targetXFormOffsetValue))

                        else:
                            if self.targetAimSelectedAxis == '-Z':
                                cmds.xform(os=True, r=True, translation=(0, 0, targetXFormOffsetValue * -1))

        # Constraint string_target to follow last control of the chain
        cmds.select(self.sel[-1], r=True)
        cmds.select('string_target', tgl=True)
        cmds.parentConstraint(mo=True)

        # Bake root and target locators
        cmds.select('string_target', r=True)
        for ctrl in range(len(self.sel)):
            cmds.select(f"{self.sel[ctrl]}_root", tgl=True)
        bake()

        # Controls constrained to respective offset locators
        for ctrl in range(len(self.sel)):
            cmds.select(f"{self.sel[ctrl]}_offset", r=True)
            cmds.select(self.sel[ctrl], tgl=True)
            cmds.orientConstraint()

        # Aim Constraint Setup
        for ctrl in range(len(self.sel) - 1):
            cmds.select(f"{self.sel[ctrl + 1]}_root", r=True)
            cmds.select(f"{self.sel[ctrl]}_offset", tgl=True)
            aimSpace(f"{self.sel[ctrl]}_root", '+X')

        cmds.select('string_target', r=True)
        cmds.select(f"{self.sel[-1]}_offset", tgl=True)
        aimSpace(f"{self.sel[-1]}_root", self.rootsAimSelectedAxis)

        # Offset roots by a set of frames
        rootList = []
        for ctrl in range(len(self.sel)):
            currentCtrl = f"{self.sel[ctrl]}_root"
            rootList.append(currentCtrl)

        rootList.pop(0)
        rootList.append('string_target')

        timeFactorResponse = self.stringOffsetValue

        timeFactorInitial = timeFactorResponse
        timeFactorProgressive = timeFactorResponse
        inputTime = timeFactorResponse

        cmds.select(cl=True)

        for loc in rootList:
            cmds.select(loc, tgl=True)

        cmds.select('string_target', tgl=True)

        for item in range(len(rootList)):
            print(timeFactorProgressive)
            cmds.keyframe(rootList[item], edit=True, relative=True, timeChange=timeFactorProgressive)
            timeFactorProgressive = timeFactorInitial + inputTime
            timeFactorInitial = timeFactorProgressive

        cmds.select('string_target', r=True)
        for ctrl in range(len(self.sel)):
            cmds.select(f"{self.sel[ctrl]}_root", tgl=True)
        cmds.group(n='stringAimSetup_grp')

    def stringSelectControlsButtonPressed(self):
        cmds.select(cl=True)
        for ctrl in self.sel:
            cmds.select(ctrl, tgl=True)

    def stringGenerateBakeButtonPressed(self):
        cmds.select(cl=True)
        for ctrl in self.sel:
            cmds.select(ctrl, tgl=True)
        bake()
        cmds.delete('stringAimSetup_grp')


############################
# INTERFACE RUN
############################

def run():
    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = AnimOverlapGenerator(parent=getMayaWindow())
    MAIN_WINDOW.show()


if __name__ == '__main__':
    run()