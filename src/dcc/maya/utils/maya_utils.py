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
]

# -------------------------------------
#
#       Functions
#
# -------------------------------------

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_file_reference(path, maya_type, namespace):
    cmds.file(path, r=True, type=maya_type, ns=namespace, op='v=0')

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_file_import(path, maya_type):
    cmds.file(path, i=True, type=maya_type, ns=':', op='v=0')

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_open_file(path):
    cmds.file(path, open=True, ignoreVersion=True, force=True)

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_get_namespaces():

    scene_nmp_list = cmds.namespaceInfo(listOnlyNamespaces=True)
    scene_nmp_filtered = [nmp for nmp in scene_nmp_list if nmp not in ('UI', 'shared')]

    return scene_nmp_filtered

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbt_util_bake_anim():

    cmds.BakeSimulation()
    cmds.filterCurve()
    cmds.delete(sc=True)
    mel.eval('generateAllUvTilePreviews')

'''
PURPOSE:        
PROCEDURE:      
ASSUMPTIONS:    
'''
def mbr_util_get_selected_object():

    selection = cmds.ls(selection=True)
    if len(selection) == 0 or len(selection) > 1:
        return None
    else:
        return selection[0]

'''
PURPOSE:        
PROCEDURE:      
ASSUMPTIONS:    
'''
def mbr_util_match_translation_to_obj(target, source):

    cmds.select(target, r=True)
    cmds.select(source, add=True)
    mel.eval('MatchTranslation')

'''
PURPOSE:        
PROCEDURE:      
ASSUMPTIONS:    
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
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_parent_constraint(source, target, offset=True):

    cmds.select(source, r=True)
    cmds.select(target, add=True)

    if offset:
        cur_cons = cmds.parentContraint(mo=True)[0]
    else:
        cur_cons = cmds.parentConstraint(mo=False)[0]

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_get_maya_extension(cur_file):

    if cur_file.endswith('.ma'):
        maya_file_ext = 'mayaAscii'
    elif cur_file.endswith('.mb'):
        maya_file_ext = 'mayaBinary'

    return maya_file_ext