# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import maya.cmds as cmds
import maya.mel as mel

# -------------------------------------
#
#       Export Config
#
# -------------------------------------

__all__ = [
    'mbr_util_file_reference',
    'mbr_util_file_import',
    'mbr_util_open_file',
    'mbr_util_get_namespaces',
    'mbt_util_bake_anim',
    'mbr_util_get_selected_object',
    'mbr_util_get_camera_namespaces',
    'mbr_util_match_translation_to_obj',
    'mbr_util_parent_constraint',
    'mbr_util_get_maya_extension',
    'mbr_util_reopen_cur_file',
]

# -------------------------------------
#
#       Functions
#
# -------------------------------------

'''
PURPOSE:        Simplifies the reference command 
PROCEDURE:      > Pass function arguments as variables on the file command
ASSUMPTIONS:    None
'''
def mbr_util_file_reference(path, maya_type, namespace):
    cmds.file(path, r=True, type=maya_type, ns=namespace, op='v=0')

'''
PURPOSE:        Simplifies the import command
PROCEDURE:      > Pass function arguments as variables on the file command
ASSUMPTIONS:    None
'''
def mbr_util_file_import(path, maya_type):
    cmds.file(path, i=True, type=maya_type, ns=':', op='v=0')

'''
PURPOSE:        Simplifies the open command
PROCEDURE:      > Pass function argument as variable on the file command
ASSUMPTIONS:    None
'''
def mbr_util_open_file(path):
    cmds.file(path, open=True, ignoreVersion=True, force=True)

'''
PURPOSE:        Gets the namespaces on the scene, excluding the default ones
PROCEDURE:      > Create a list with all the namespaces
                > Filter the list by removing the default namespaces
                > Return the filtered list of namespaces
ASSUMPTIONS:    None
'''
def mbr_util_get_namespaces():

    scene_nmp_list = cmds.namespaceInfo(listOnlyNamespaces=True)
    scene_nmp_filtered = [nmp for nmp in scene_nmp_list if nmp not in ('UI', 'shared')]

    return scene_nmp_filtered

'''
PURPOSE:        Custom bake command
PROCEDURE:      > Bake simulation command
                > Applies the euler filter
                > Delete static curves
                > Regenerate UV Tiles as a texture fix
ASSUMPTIONS:    None
'''
def mbt_util_bake_anim():

    cmds.BakeSimulation()
    cmds.filterCurve()
    cmds.delete(sc=True)
    mel.eval('generateAllUvTilePreviews')

'''
PURPOSE:        Get selected object
PROCEDURE:      > Creates a variable that stores the selection
                > Checks if the selection is empty. If it is return None, else return the selection string
ASSUMPTIONS:    None
'''
def mbr_util_get_selected_object():

    selection = cmds.ls(selection=True)
    if len(selection) == 0 or len(selection) > 1:
        return None
    else:
        return selection[0]

'''
PURPOSE:        Match transformation to object
PROCEDURE:      > Select the target
                > Select the source
                > Apply match transformation command
ASSUMPTIONS:    None
'''
def mbr_util_match_translation_to_obj(target, source):

    cmds.select(target, r=True)
    cmds.select(source, add=True)
    mel.eval('MatchTranslation')

'''
PURPOSE:        Get camera namespaces
PROCEDURE:      > Get the camera transforms of the cameras with a namespace
                > Get the namespaces of the animCam nodes and store them in an empty list
ASSUMPTIONS:    The camera naming conventions is as follows: {namespace}:animCam
'''
def mbr_util_get_camera_namespaces():

    # Get the camera transforms of the cameras that have a namespace (animCams only)
    cam_shapes = cmds.ls(type='camera')
    cam_shapes_ns = [shape for shape in cam_shapes if ':' in shape]
    cam_transforms = cmds.listRelatives(cam_shapes_ns, parent=True) or []
    cam_transforms_anim = [cam for cam in cam_transforms if 'animCam' in cam]

    # Get the namespaces and store them in an empty list
    cam_ns = []
    for cam in cam_transforms_anim:
        idx = cam.find(':')
        ns = cam[:idx]
        cam_ns.append(ns)

    return cam_ns

'''
PURPOSE:        Simplification of the parent constraint command
PROCEDURE:      > Select the source
                > Select the target
                > Apply the parent constraint depending if the argument offset is True or False
                > Return the cur_cons
ASSUMPTIONS:    None
'''
def mbr_util_parent_constraint(source, target, offset=True):

    cmds.select(source, r=True)
    cmds.select(target, add=True)

    if offset:
        cur_cons = cmds.parentContraint(mo=True)[0]
    else:
        cur_cons = cmds.parentConstraint(mo=False)[0]

    return cur_cons

'''
PURPOSE:        Get Maya file extension
PROCEDURE:      > If file ends with .ma, declare the variable as a mayaAscii. If it ends with .mb, declare it as a
                mayaBinary
                > Return the variable
ASSUMPTIONS:
'''
def mbr_util_get_maya_extension(cur_file):

    if cur_file.endswith('.ma'):
        maya_file_ext = 'mayaAscii'
    elif cur_file.endswith('.mb'):
        maya_file_ext = 'mayaBinary'

    return maya_file_ext

'''
PURPOSE:        Add camera handles attribute
PROCEDURE:      > Create the startFrame attribute and make it visible on the Channel Box
                > Create the endFrame attribute and make it visible on the Channel Box
                > Get the start and end frame in the timeline and set the new attributes to these values
ASSUMPTIONS:    The camera doesn't have an startFrame and endFrame attributes
'''
def mbr_util_add_handles_attribute(node):

    cmds.addAttr(node, longName='startFrame', attributeType='long', keyable=False)
    cmds.setAttr(f"{node}.startFrame", channelBox=True)

    cmds.addAttr(node, longName='endFrame', attributeType='long', keyable=False)
    cmds.setAttr(f"{node}.endFrame", channelBox=True)

    start_frame = cmds.playbackOptions(q=True, min=True)
    end_frame = cmds.playbackOptions(q=True, max=True)

    cmds.setAttr(f"{node}.startFrame", start_frame)
    cmds.setAttr(f"{node}.endFrame", end_frame)

'''
PURPOSE:        Reopen current scene
PROCEDURE:      > Declare a variable with the current file
                > Force save current file
                > Create a blank Maya scene
                > Open the scene path on the cur_file variable
ASSUMPTIONS:    None
'''
def mbr_util_reopen_cur_file():

    cur_file = cmds.file(q=True, sceneName=True)

    if cur_file:
        cmds.file(save=True, force=True)
        cmds.file(new=True, force=True)
        cmds.file(cur_file, open=True, force=True)
    else:
        return