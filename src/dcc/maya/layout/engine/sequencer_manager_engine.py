# -------------------------------------------
#
#       Import Modules
#
# -------------------------------------------

import maya.cmds as cmds
from TOS_Pipeline.src.dcc.maya.utils.qt_compat import wdg
from TOS_Pipeline.src.dcc.maya.utils.maya_utils import mbr_util_add_handles_attribute

# -------------------------------------------
#
#       Export Config
#
# -------------------------------------------

__all__ = [
    'mbr_egn_create_cam_locs_with_handles',
    'mbr_egn_add_camera_handles',
    'mbr_egn_create_sequencer_shot_from_loc_handles',
    'mbr_egn_create_sequencer_shot_from_cam_handles',
    'mbr_egn_frame_timeline_to_sequencer_range',
    'mbr_egn_get_selected_sequence_shots_timeline_range',
    'mbr_egn_get_sequencer_shots',
    'mbr_egn_get_all_sequence_shots_timeline_range',
    'mbr_egn_get_bind_cameras',
    'mbr_egn_execute_playblast',
    'mbr_util_add_handles_attribute',
]

# -------------------------------------------
#
#       Engine Functions
#
# -------------------------------------------

'''
PURPOSE:        Create the locator's structure to drive the TTF camera and handles on the subOffset level
PROCEDURE:      > Get the camera name and store it in a variable
                > Create the spaceLocators with the right name and create the hierarchy. Set the Locator Scale to 0
                > Match transform of the locators hierarchy to the camera
                > Constrain the camera to follow the subOffset level
                > Add handles to the subOffset locator
ASSUMPTIONS:    A camera with namespace is selected
'''
def mbr_egn_create_cam_locs_with_handles():

    selection = cmds.ls(selection=True)

    if len(selection) == 0:
        wdg.QMessageBox.warning(None, 'Warning', 'You need to select a camera first')

    elif len(selection) >= 1:

        # Get camera shape node
        for idx in range(len(selection)):
            cam_transform = selection[idx]
            cam_shape = cmds.listRelatives(cam_transform, shapes=True, type='camera')[0]

            if cam_shape:

                # Get semicolon index
                colon_idx = cam_shape.find(':')
                cam_name = cam_shape[:colon_idx]

                # Creates locators for camera hierarchy
                loc_orbit = cmds.spaceLocator(name=f"{cam_name}_orbitCam")[0]
                loc_placement = cmds.spaceLocator(name=f"{cam_name}_placementCam")[0]
                loc_offset = cmds.spaceLocator(name=f"{cam_name}_offsetCam")[0]
                loc_sub_offset = cmds.spaceLocator(name=f"{cam_name}_subOffsetCam")[0]

                # Parents camera locators for correct hierarchy
                cmds.parent(loc_sub_offset, loc_offset)
                cmds.parent(loc_offset, loc_placement)
                cmds.parent(loc_placement, loc_orbit)

                # Match transform locator to camera
                cmds.select(cl=True)
                cmds.select(loc_orbit, add=True)
                cmds.select(cam_shape, add=True)
                mel.eval('MatchTranslation')
                mel.eval('MatchRotation')

                # Constrain the camera to the subOffset locator
                cmds.select(cl=True)
                cmds.select(loc_sub_offset, add=True)
                cmds.select(cam_transform, add=True)
                cmds.parentConstraint()

                # Add Handles to SubOffset Locator
                mbr_util_add_handles_attribute(loc_sub_offset)

            else:
                return

'''
PURPOSE:        Create start/end handles to selected camera
PROCEDURE:      > Store the selected camera in a variable
                > Check if the selected object is a camera, if not, raise an error
                > Add handles to selected camera
ASSUMPTIONS:    The selected object is 1) a camera, and 2) the renderCam
'''
def mbr_egn_add_camera_handles():

    # Store selection
    selection = cmds.ls(selection=True)

    if len(selection) == 0:
        wdg.QMessageBox.warning(None, 'Warning', 'You must select one camera first')
        return

    cam_transform = selection[0]
    cam_shape = cmds.listRelatives(cam_transform, shapes=True, type='camera')[0]

    # Add Handles to Selected Camera
    if cam_shape and len(selection) == 1:

        mbr_util_add_handles_attribute(cam_transform)

    # Raises an error if there is the selected object is different from a camera
    else:
        wdg.QMessageBox.warning(None, 'Warning', 'Your selection is not valid.\nYou must select one camera')

'''
PURPOSE:        Create a shot in Sequencer after current shot depending on the time range in the Locator handles
PROCEDURE:      > Get info from locator's handles (start and end frame)
                > Create shot in sequencer using the timeline range
ASSUMPTIONS:    User needs to have a locator with start/end frame handles selected
'''
def mbr_egn_create_sequencer_shot_from_loc_handles(cam_nmp, cam_transform):

    if cmds.attributeQuery('startFrame', node=f"{cam_nmp}_subOffsetCam", exists=True):
        start_frame = cmds.getAttr(f"{cam_nmp}_subOffsetCam.startFrame")
        end_frame = cmds.getAttr(f"{cam_nmp}_subOffsetCam.endFrame")
    else:
        wdg.QMessageBox.warning(None, 'Warning', 'Handles not found')

    cmds.shot(
        startTime=start_frame,
        endTime=end_frame,
        sequenceStartTime=start_frame,
        sequenceEndTime=end_frame,
        currentCamera=cam_transform
    )

'''
PURPOSE:        Create shot in Sequencer after current shot depending on the time range in the Camera handles
PROCEDURE:      ? Get info from camera's handles (start and end frame)
ASSUMPTIONS:    User needs to have a camera with start/end frame handles selected
'''
def mbr_egn_create_sequencer_shot_from_cam_handles(cam_transform):

    if cmds.attributeQuery('startFrame', node=cam_transform, exists=True):
        start_frame = cmds.getAttr(f"{cam_transform}.startFrame")
        end_frame = cmds.getAttr(f"{cam_transform}.endFrame")
    else:
        wdg.QMessageBox.warning(None, 'Warning', 'Handles not found')

    cmds.shot(
        startTime=start_frame,
        endTime=end_frame,
        sequenceStartTime=start_frame,
        sequenceEndTime=end_frame,
        currentCamera=cam_transform
    )

'''
PURPOSE:        Frame the timeline to selected sequencer clips
PROCEDURE:      > Store selected shots in the sequencer in a list
                > Check if there is either 1 or more shots selected. If one is selected frame to only that time range,
                if more than 1 is selected, take the start frame from the first item and the end frame of the last item
ASSUMPTIONS:    To be safe, the integer of the last shot has to be higher than the other shots
'''
def mbr_egn_frame_timeline_to_sequencer_range():

    shots = sorted(cmds.ls(selection=True, type='shot'))

    if len(shots) == 1:

        start = cmds.shot(shots[0], q=True, startTime=True)
        end = cmds.shot(shots[0], q=True, endTime=True)

        cmds.playbackOptions(minTime=start, maxTime=end)

    elif len(shots) > 1:
        start = cmds.shot(shots[0], q=True, startTime=True)
        end = cmds.shot(shots[-1], q=True, endTime=True)

        cmds.playbackOptions(minTime=start, maxTime=end)

    else:
        wdg.QMessageBox.warning(None, 'Warning', 'You need to select at least one shot in Sequencer')

'''
PURPOSE:        Return a list of start/end time ranges of all shots in Sequencer
PROCEDURE:      > Get all shots from sequencer, sort them alphabetically, and store the pairs of start/end in a list
                > Return the list of pairs
ASSUMPTIONS:    There is at least one shot in Sequencer
'''
def mbr_egn_get_selected_sequence_shots_timeline_range():

    shots = sorted(cmds.ls(selection=True, type='shot'))

    shots_time_ranges_list = []

    for shot in shots:
        start = cmds.shot(shot, q=True, startTime=True)
        end = cmds.shot(shot, q=True, endTime=True)

        time_range_list = [start, end]

        shots_time_ranges_list.append(time_range_list)

    return shots_time_ranges_list

'''
PURPOSE:        Get a list with sequencer shots
PROCEDURE:      > Create a list with all sequencer shots
                > Return a list of sequencer shots
ASSUMPTIONS:    None
'''
def mbr_egn_get_sequencer_shots():

    shots = cmds.ls(type='shot')
    shots = sorted(shots, key=lambda s: cmds.getAttr(f"{s}.sequenceStartFrame"))
    return shots

'''
PURPOSE:        Return a list of start/end time ranges of all shots in Sequencer
PROCEDURE:      > Get all shots from sequencer, sort them alphabetically, and store the pairs of start/end in a list
                > Return the list of pairs
ASSUMPTIONS:    There is at least one shot in Sequencer
'''
def mbr_egn_get_all_sequence_shots_timeline_range():

    shots = mbr_egn_get_sequencer_shots()

    shots_time_ranges_list = []

    for shot in shots:
        start = cmds.shot(shot, q=True, startTime=True)
        end = cmds.shot(shot, q=True, endTime=True)

        time_range_list = [start, end]

        shots_time_ranges_list.append(time_range_list)

    return shots_time_ranges_list

'''
PURPOSE:        Get a list of the bind cameras to the sequencer shots
PROCEDURE:      > Get the list from the mbr_egn_get_sequencer_shots function
                > Append to a new empty list the camera transforms in the same order of the function list
                > Return a list with the camera transforms
ASSUMPTIONS:    None
'''
def mbr_egn_get_bind_cameras():

    shots = mbr_egn_get_sequencer_shots()

    cam_list = []

    for shot in shots:
        cur_cam = cmds.listConnections(f"{shot}.currentCamera")[0]
        cam_list.append(cur_cam)

    return cam_list

'''
PURPOSE:        Playblast shot
PROCEDURE:      > Execute a playblast with the set options
ASSUMPTIONS:    None
'''
def mbr_egn_execute_playblast(start_time, end_time, filename, seq):

        cmds.playblast(
            startTime=start_time,
            endTime=end_time,
            sequenceTime=seq,
            format='qt',
            compression='H.264',
            filename=filename,
            widthHeight=(1280, 720),
            percent=100,
            viewer=False,
            forceOverwrite=True,
        )
