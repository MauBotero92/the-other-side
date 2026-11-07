# Import Modules
from PySide6 import QtWidgets as wdg
from PySide6 import QtCore as core
from PySide6 import QtGui as gui
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds

############################
# VARIABLES
############################

MAIN_WINDOW = None
__version__ = '2.0'


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
    cmds.refresh(su=True)
    cmds.BakeSimulation()
    cmds.filterCurve = ()
    cmds.delete(sc=True)
    cmds.refresh(su=False)


def cycleToWorld():
    '''
    Creates a locator with an animation sample of the control translations
    and it is constrained to the main control to move forward the character.
    Order of selection: First feet (or object to be sampled), then orient control.
    '''
    userSel = cmds.ls(sl=True)
    driver = userSel[0]
    orientCtrl = userSel[1]

    currentTime = cmds.currentTime(q=True)
    firstFrame = cmds.playbackOptions(q=True, min=True)
    lastFrame = cmds.playbackOptions(q=True, max=True)

    # Create a locator and group it
    motionLoc = cmds.spaceLocator(n="motionLoc")
    motionOffset = cmds.group(n="motionOffset")

    cmds.select(motionOffset, r=True)
    cmds.select(driver, tgl=True)
    cmds.MatchTransform()

    # Constrain the locator to the driver control (usually a feet)
    cmds.select(driver, r=True)
    cmds.select(motionLoc, tgl=True)
    cmds.pointConstraint()

    # Bake locator and delete constraint
    cmds.select(motionLoc, r=True)
    bake()

    # Delete redundant or not essential keyframes
    cmds.cutKey(motionLoc, time=((int(currentTime+2)), int(lastFrame)))
    cmds.cutKey(motionLoc, time=((currentTime-1), firstFrame))
    cmds.keyTangent(itt="linear", ott="linear")

    # Reverse all the keys in time (not in value)
    if cmds.objExists("motionLoc_translateX") == True:
        cmds.keyframe("motionLoc_translateX", edit=True, r=True, o="over", tc=-2, t=((currentTime+1), (currentTime+1)))
    if cmds.objExists("motionLoc_translateY") == True:
        cmds.keyframe("motionLoc_translateY", edit=True, r=True, o="over", tc=-2, t=((currentTime+1), (currentTime+1)))
    if cmds.objExists("motionLoc_translateZ") == True:
        cmds.keyframe("motionLoc_translateZ", edit=True, r=True, o="over", tc=-2, t=((currentTime+1), (currentTime+1)))

    # Cycle the curves to infitiny with offset
    cmds.setInfinity(poi="cycleRelative")
    cmds.setInfinity(pri="cycleRelative")

    # Constrain locator to drive the main control
    cmds.select(motionLoc, r=True)
    cmds.select(orientCtrl, tgl=True)
    cmds.pointConstraint(mo=True)

    # Delete from memory any variable
    del userSel, driver, orientCtrl, motionLoc, motionOffset
    del currentTime, firstFrame, lastFrame


############################
# CYCLE TO WORLD CLASS
############################

# Main class for the Cycle to World
class CycleToWorld(wdg.QMainWindow):

    ############### INIT FUNCTION ###############
    #############################################
    #############################################

    def __init__(self, parent=None):
        super(CycleToWorld, self).__init__(parent)

        self.setWindowTitle(f"Cycle To World {__version__}")
        self.setFixedSize(610, 360)

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
        mainLyt.setContentsMargins(40,30,40,0)


        ##### MAIN LAYOUT SECTIONS - Sections Layouts #####
        # Title Layout #
        titleLyt = wdg.QVBoxLayout()
        titleLyt.setAlignment(core.Qt.AlignCenter)
        mainLyt.addLayout(titleLyt)

        # Upper Layout #
        upperLyt = wdg.QVBoxLayout()
        upperLyt.setContentsMargins(0,20,0,15)
        mainLyt.addLayout(upperLyt)

        # Bottom Layout #
        bottomLyt = wdg.QVBoxLayout()
        mainLyt.addLayout(bottomLyt)


        ##### UPPER LAYOUT SECTIONS - Tool Buttons Layouts #####
        # Create Setup Layout #
        createSetupLyt = wdg.QHBoxLayout()
        upperLyt.addLayout(createSetupLyt)

        # Bake Options Layout #
        bakeOptionsLyt = wdg.QHBoxLayout()
        upperLyt.addLayout(bakeOptionsLyt)


        ##### BOTTOM LAYOUT SECTIONS - Instructions Layouts #####
        # Instructions Layout
        instructionsLyt = wdg.QVBoxLayout()
        bottomLyt.addLayout(instructionsLyt)


        ############### WIDGETS ################
        ########################################

        ##### TITLE LAYOUT WIDGETS #####
        # Cycle To World Label
        cycleToWorldLabel = wdg.QLabel('Cycle To World')
        cycleToWorldLabel.setStyleSheet("font-size: 20px;")
        cycleToWorldLabel.setAlignment(core.Qt.AlignCenter)
        titleLyt.addWidget(cycleToWorldLabel)

        # Author Label
        authorLabel = wdg.QLabel('Author: Mauricio Botero Ruiz')
        authorLabel.setStyleSheet("font-size: 12px;")
        authorLabel.setAlignment(core.Qt.AlignCenter)
        titleLyt.addWidget(authorLabel)


        ##### UPPER LAYOUT WIDGETS #####
        # Create Setup Button
        self.createSetupButton = wdg.QPushButton('Create Setup')
        createSetupLyt.addWidget(self.createSetupButton)
        self.createSetupButton.pressed.connect(self.createSetupButtonPressed)

        # Bake Main Ctrl Button
        self.bakeMainCtrlButton = wdg.QPushButton('Bake Main Control')
        bakeOptionsLyt.addWidget(self.bakeMainCtrlButton)
        self.bakeMainCtrlButton.pressed.connect(self.bakeMainCtrlButtonPressed)

        # Bake World Controls Button
        self.bakeWorldCtrlsButton = wdg.QPushButton('Bake World Controls')
        bakeOptionsLyt.addWidget(self.bakeWorldCtrlsButton)
        self.bakeWorldCtrlsButton.pressed.connect(self.bakeWorldCtrlsButtonPressed)


        ##### BOTTOM LAYOUT WIDGETS #####


        # Notes Labels
        note01Label = wdg.QLabel('NOTE: In order to work, you must select the foot while in contact on the ground in a linear motion.')
        note01Label.setStyleSheet("font-size: 11px;")
        instructionsLyt.addWidget(note01Label)

        note02Label = wdg.QLabel("Also, don't have your playhead on the first frame, at the very least have on the second frame")
        note02Label.setStyleSheet("font-size: 11px;")
        instructionsLyt.addWidget(note02Label)

        spaceLabel = wdg.QLabel("")
        instructionsLyt.addWidget(spaceLabel)

        # Instructions Title Label
        instructionsTitleLabel = wdg.QLabel('Instructions:')
        instructionsTitleLabel.setStyleSheet("font-size: 14px;")
        instructionsLyt.addWidget(instructionsTitleLabel)

        # First Step Label
        firstStepLabel = wdg.QLabel('1. Select first the foot (or another driver), and then the main control.')
        firstStepLabel.setStyleSheet("font-size: 11px;")
        instructionsLyt.addWidget(firstStepLabel)

        # Second Step label
        secondStepLabel = wdg.QLabel('2. Click "Bake Main Control" if you want the main control to move along with your character.')
        secondStepLabel.setStyleSheet("font-size: 11px;")
        instructionsLyt.addWidget(secondStepLabel)

        # Third Step Label
        thirdStepLabel = wdg.QLabel('3. Click Bake World Controls if you want the main control to be reset at the origin.')
        thirdStepLabel.setStyleSheet("font-size: 11px;")
        instructionsLyt.addWidget(thirdStepLabel)

        # Fourth Step Label
        fourthStepLabel = wdg.QLabel('4. If you choose Bake World Controls, choose first the world space controls and the main control last.')
        fourthStepLabel.setStyleSheet("font-size: 11px;")
        instructionsLyt.addWidget(fourthStepLabel)


    ############### ENGINE ###############
    ######################################
    ######################################

    def createSetupButtonPressed(self):
        cycleToWorld()

    def bakeMainCtrlButtonPressed(self):
        mainCtrlSel = cmds.ls(sl=True)
        mainCtrl = mainCtrlSel[0]
        bake()

    def bakeWorldCtrlsButtonPressed(self):
        worldCtrlsSel = cmds.ls(sl=True)
        worldCtrlsList = worldCtrlsSel[:-1]
        worldMainCtrlList = worldCtrlsSel[-1]

        # Create locators for world space controls
        locList = []
        for ctrl in range(len(worldCtrlsList)):
            locItem = cmds.spaceLocator(n=f"loc_{worldCtrlsList[ctrl]}")
            locList.append(locItem[0])

        # Snap the locators to the control position in world space
        for item in range(0, len(worldCtrlsList)):
            cmds.select(locList[item], r=True)
            cmds.select(worldCtrlsList[item], tgl=True)
            cmds.MatchTransform()

        # Constrain the locators to the controls
        consList = []
        print(consList)
        print(worldCtrlsList)
        for item in range(0, len(worldCtrlsList)):
            cmds.select(worldCtrlsList[item], r=True)
            cmds.select(locList[item], tgl=True)
            print(item)

            if cmds.getAttr(f"{worldCtrlsList[item]}.rx", lock=True) or cmds.getAttr(f"{worldCtrlsList[item]}.rx", keyable=True):
            # If rotations are hidden or locked using only the rx attribute
                consToLoc01 = cmds.pointConstraint()
                consList.append(consToLoc01[0])

            elif cmds.getAttr(f"{worldCtrlsList[item]}.tx", lock=True) or cmds.getAttr(f"{worldCtrlsList[item]}.tx", keyable=True):
            # If translations are hidden or locked using only the tx attribute
                consToLoc01 = cmds.orientConstraint()
                consList.append(consToLoc01[0])

            else:
                consToLocParent01 = cmds.pointConstraint()
                consToLocParent02 = cmds.orientConstraint()
                consList.append(consToLocParent01[0])
                consList.append(consToLocParent02[0])

        # Bake the locators and delete the constraints (BUG HERE)
        for loc in locList:
            cmds.select(loc, r=True)
            bake()

        for cons in consList:
            cmds.delete(cons)

        # Locators drives the controls
        for item in range(0, len(worldCtrlsList)):
            cmds.select(locList[item], r=True)
            cmds.select(worldCtrlsList[item], tgl=True)

            if cmds.getAttr(f"{worldCtrlsList[item]}.rx", lock=True) or cmds.getAttr(f"{worldCtrlsList[item]}.rx", keyable=True):
                consToControl01 = cmds.pointConstraint()
                consList.append(consToControl01[0])

            elif cmds.getAttr(f"{worldCtrlsList[item]}.tx", lock=True) or cmds.getAttr(f"{worldCtrlsList[item]}.tx", keyable=True):
                consToControl01 = cmds.orientConstraint()
                consList.append(consToControl_01[0])

            else:
                consToControlParent01 = cmds.pointConstraint()
                consToControlParent02 = cmds.orientConstraint()
                consList.append(consToControlParent01[0])
                consList.append(consToControlParent02[0])

        # Zero out main control
        cmds.select(worldCtrlsList[-1], r=True)
        cmds.setAttr(f"{worldCtrlsList[-1]}.tx", 0)
        cmds.setAttr(f"{worldCtrlsList[-1]}.ty", 0)
        cmds.setAttr(f"{worldCtrlsList[-1]}.tz", 0)
        cmds.setAttr(f"{worldCtrlsList[-1]}.rx", 0)
        cmds.setAttr(f"{worldCtrlsList[-1]}.ry", 0)
        cmds.setAttr(f"{worldCtrlsList[-1]}.rz", 0)

        cmds.delete('motionOffset')

        # Select world space controls and bake them
        for item in worldCtrlsList[:-1]:
            cmds.select(cl=True)
            cmds.select(item, r=True)
            bake()

        # Delete locators
        for loc in locList:
            cmds.delete(loc)





############################
# INTERFACE RUN
############################

def run():
    global MAIN_WINDOW
    if not MAIN_WINDOW or not cmds.window(q=True, exists=True):
        MAIN_WINDOW = CycleToWorld(parent=getMayaWindow())
    MAIN_WINDOW.show()

if __name__ == '__main__':
    run()
