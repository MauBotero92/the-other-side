# -------------------------------------------
#
#       Import modules
#
# -------------------------------------------

import maya.cmds as cmds
import maya.mel as mel
import string


# -------------------------------------------
#
#       Utility functions
#
# -------------------------------------------

def MBR_FBXExportOption(command, value):
    '''
    PURPOSE:        Minimize the mel.eval command to be more readable further along the code
    PROCEDURE:      > Use the mel.eval command to receive the parameters of the function
    PRESUMPTIONS:   None
    '''

    mel.eval(f"{command} -v {value}")


# -------------------------------------------
#
#       Low level functions
#
# -------------------------------------------

def MBR_TagForOrigin(node):
    '''
    PURPOSE:        Tag the given node with the origin attribute and set to True
    PROCEDURE:      > If the object exists and the attribute does not exists, add the origin bool and set to True
    PRESUMPTION:    None
    '''

    if cmds.objExists(node) and not cmds.objExists(f"{node}.origin"):
        cmds.addAttr(node, shortName='org', longName='origin', at='bool')
        cmds.setAttr(f"{node}.origin", True)


def MBR_TagForMeshExport(mesh):
    '''
    PURPOSE:        Add attributes to the mesh so exporter can find them
    PROCEDURE:      > If object exists and the attribute does not exists, add exportMeshes message attribute
    PRESUMPTIONS:   None
    '''

    if cmds.objExists(mesh) and not cmds.objExists(f"{mesh}.exportMeshes"):
        cmds.addAttr(mesh, shortName='xms', longName='exportMeshes', at='message')


def MBR_TagForExportNode(node):
    '''
    PURPOSE:        Add attribute to the node so exporter can find export definitions
    PROCEDURE:      > If the object exists and the attribute does not exists, add the exportNode message attribute
    PRESUMPTIONS:   None
    '''

    if cmds.objExists(node) and not cmds.objExists(f"{node}.exportNode"):
        cmds.addAttr(node, shortName='xnd', longName='exportNode', at='message')


def MBR_ReturnOrigin(ns):
    '''
    PURPOSE:        Return the origin of the given namespace
    PROCEDURE:      > If ns is not empty string, list all joints with the matching namespace, else list all joints
                    > For list of joints, look for origin attribute and if it is set to True. If found, return name
                      of joint, else return 'Error'
    PRESUMPTIONS:   > Origin attribute it is on a joint
                    > 'Error' is not a valid joint name
                    > Namespace does not include colon
    '''

    joints = []

    if ns:
        joints = cmds.ls((f"{ns}:*"), type='joint')
    else:
        joints = cmds.ls(type='joint')

    if len(joints):
        for cur_joint in joints:
            if cmds.objExists(f"{cur_joint}.origin") and cmds.getAttr(f"{cur_joint}.origin"):
                return cur_joint

    return 'Error'


def MBR_FindMeshWithBlendshapes(ns):
    '''
    PURPOSE:        Return the meshes connected to blendshapes nodes
    PROCEUDRE:      > Get a list of blendshapes nodes
                    > Follow those connections to the shape node
                    > Traverse up the hierarchy to find parent transform node
    PRESUMPTIONS:   > Character has a valid namespace
                    > Namespace does not have colon
                    > Only exporting polygonal meshes
    '''

    return_array = []

    blendshapes = cmds.ls((f"{ns}:*"), type='blendShape')

    for cur_blendshape in blendshapes:
        downstream_nodes = cmds.listHistory(cur_blendshape, future=True)
        for cur_node in downstream_nodes:
            if cmds.objectType(cur_node, isType='mesh'):
                parents = cmds.listRelatives(cur_node, parent=True)
                return_array.append(parents[0])

    return return_array


def MBR_TagForGarbage(node):
    '''
    PURPOSE:        Tag object for being garbage
    PROCEDURE:      > If node is valid object and attribute does not exists, add deleteMe attribute
    PRESUMPTIONS:   None
    '''

    if cmds.objExists(node) and not cmds.objExists(f"{node}.deleteMe"):
        cmds.addAttr(node, shortName='del', longName='deleteMe', at='bool')
        cmds.setAttr(f"{node}.deleteMe", True)


def MBR_ClearGarbage():
    '''
    PURPOSE:        Removes all nodes tagged as garbage
    PROCEDURE:      > List all transforms in the scene
                    > Iterate through list anythin with 'deleteMe' attribute
    PRESUMPTIONS:   > The deleteMe attribute is name of the attribute signifying garbage
    '''

    transforms_list = cmds.ls(tr=True)

    for cur in transforms_list:
        if cmds.objExists(f"{cur}.deleteMe"):
            cmds.delete(cur)


# -------------------------------------------
#
#       Export settings node functions
#
# -------------------------------------------

def MBR_AddFBXNodeAttrs(fbx_export_node):
    '''
    PURPOSE:        To add the attributes to the export node to store our export settings
    PROCEDURE:      > For each attribute we want to add check if it exists, if it doesn't exists, add it
    PRESUMPTIONS:   > Assume fbxExportNode is a valid object
    '''

    if not cmds.attributeQuery('export', node=fbx_export_node, exists=True):
        cmds.addAttr(fbx_export_node, longName='export', at='bool')

    if not cmds.attributeQuery('moveToOrigin', node=fbx_export_node, exists=True):
        cmds.addAttr(fbx_export_node, longName='moveToOrigin', at='bool')

    if not cmds.attributeQuery('zeroOrigin', node=fbx_export_node, exists=True):
        cmds.addAttr(fbx_export_node, longName='zeroOrigin', at='bool')

    if not cmds.attributeQuery('exportName', node=fbx_export_node, exists=True):
        cmds.addAttr(fbx_export_node, longName='exportName', dt='string')

    if not cmds.attributeQuery('useSubRange', node=fbx_export_node, exists=True):
        cmds.addAttr(fbx_export_node, longName='useSubRange', at='bool')

    if not cmds.attributeQuery('startFrame', node=fbx_export_node, exists=True):
        cmds.addAttr(fbx_export_node, longName='startFrame', at='float')

    if not cmds.attributeQuery('endFrame', node=fbx_export_node, exists=True):
        cmds.addAttr(fbx_export_node, longName='endFrame', at='float')

    if not cmds.attributeQuery('exportMeshes', node=fbx_export_node, exists=True):
        cmds.addAttr(fbx_export_node, longName='exportMeshes', at='message')

    if not cmds.attributeQuery('exportNode', node=fbx_export_node, exists=True):
        cmds.addAttr(fbx_export_node, shortName='xnd', longName='exportNode', at='message')

    if not cmds.attributeQuery('animLayers', node=fbx_export_node, exists=True):
        cmds.addAttr(fbx_export_node, longName='animLayers', dt='string')


def MBR_CreateFBXExportNode(character_name):
    '''
    PURPOSE:        Create the export node to store our export settings
    PROCEDURE:      > Create an empty transform node, we will send it to AddFBXNodeAttrs to add the needed attributes
    PRESUMPTIONS:   None
    '''

    fbx_export_node = cmds.group(em=True, name=f"{character_name}FBXExportNode#")
    MBR_AddFBXNodeAttrs(fbx_export_node)
    cmds.setAttr(f"{fbx_export_node}.export", 1)

    return fbx_export_node


def MBR_ReturnFBXExportNodes(origin):
    '''
    PURPOSE:        Return all export nodes connected to given origin
    PROCEDURE:      > If origin is valid and has the exportNode attribute, return list of export nodes connected to it
    PRESUMPTIONS:   > Only export nodes are connected to exportNode attribute
    '''

    export_node_list = []

    if cmds.objExists(f"{origin}.exportNode"):
        export_node_list = cmds.listConnections(f"{origin}.exportNode")

    return export_node_list


def MBR_ConnectFBXExportNodeToOrigin(export_node, origin):
    '''
    PURPOSE:        Connect the FBX export node to the origin
    PROCEDURE:      > Check if attributes exist and nodes are valid, if they are connect attributes
    PRESUMPTIONS:   None
    '''

    if cmds.objExists(origin) and cmds.objExists(export_node):

        if not cmds.objExists(f"{origin}.exportNode"):
            MBR_TagForExportNode(origin)

        if not cmds.objExists(f"{export_node}.exportNode"):
            MBR_AddFBXNodeAttrs(fbx_export_node)

        cmds.connectAttr(f"{origin}.exportNode", f"{export_node}.exportNode")


def MBR_DeleteFBXExportNode(export_node):
    '''
    PURPOSE:        Delete given export node
    PROCEDURE:      > If object exists, delete
    PRESUMPTIONS:   None
    '''

    if cmds.objExists(export_node):
        cmds.delete(export_node)


# -------------------------------------------
#
#       Model export functions
#
# -------------------------------------------

def MBR_ConnectFBXExportNodeToMeshes(export_node, meshes):
    '''
    PURPOSE:        To connect meshes to the export node so the exporter can find them
    PROCEDURE:      > Check to make sure meshes and export_node is valid
                    > Check for attribute 'export_meshes', if no attribute, add it
                    > Connect attributes
    PRESUMPTION:    > export_node is an export node, and meshes is a list of transform nodes for polygon meshes
    '''

    if cmds.objExists(export_node):

        if not cmds.objExists(f"{export_node}.exportMeshes"):
            MBR_AddFBXNodeAttrs(export_node)

        for cur_mesh in meshes:
            if cmds.objExists(cur_mesh):
                if not cmds.objExists(f"{export_node}.exportMeshes"):
                    MBR_TagForMeshExport(cur_mesh)

                cmds.connectAttr(f"{export_node}.exportMeshes", f"{cur_mesh}.exportMeshes", force=True)


def MBR_DisconnectFBXExportNodeToMeshes(export_node, meshes):
    '''
    PURPOSE:        To disconnect the message attribute between export node and mesh
    PROCEDURE:      > Iterate through list of meshes and if mesh exists disconnect
    PRESUMPTION:    > That node and mesh are connected via exportMeshes message attr
    '''

    if cmds.objExists(export_node):
        for cur_mesh in meshes:
            if cmds.objExists(cur_mesh):
                cmds.disconnectAttr(f"{export_node}.exportMeshes", f"{cur_mesh}.exportMeshes")


def MBR_ReturnConnectedMeshes(export_node):
    '''
    PURPOSE:        Return a list of all meshes connected to the export node
    PROCEDURE:      > listConnections to export_meshes attribute
    PRESUMPTION:    > export_meshes attribute is used to connect to export meshes
                    > export_meshes is valid
    '''

    meshes = cmds.listConnections(f"{export_node}.exportMeshes", source=False, destination=True)
    return meshes


# -------------------------------------------
#
#       Animation export functions
#
# -------------------------------------------

def MBR_UnlockJointsTransforms(root):
    '''
    PURPOSE:        Unlock transforms attributes on all joints in hierarchy
    PROCEDURE:      > Create a list for the hierarchy and append in there all the joints
                    > For each item in the new list, unlock every transform attribute
    PRESUMPTIONS:   None
    '''

    hierarchy = cmds.listRelatives(root, ad=True, f=True)
    hierarchy.append(root)

    for cur in hierarchy:
        cmds.setAttr(f"{cur}.translateX", lock=False)
        cmds.setAttr(f"{cur}.translateY", lock=False)
        cmds.setAttr(f"{cur}.translateZ", lock=False)
        cmds.setAttr(f"{cur}.rotateX", lock=False)
        cmds.setAttr(f"{cur}.rotateY", lock=False)
        cmds.setAttr(f"{cur}.rotateZ", lock=False)
        cmds.setAttr(f"{cur}.scaleX", lock=False)
        cmds.setAttr(f"{cur}.scaleY", lock=False)
        cmds.setAttr(f"{cur}.scaleZ", lock=False)


def MBR_ConnectAttrs(src_node, dst_node, transform):
    '''
    PURPOSE:        To connect given node to another given node via specified transform
    PROCEDURE:      > Call connectAttr
    PRESUMPTIONS:   > Assume two nodes exist and transform type is valid
    '''

    cmds.connectAttr(f"{src_node}.{transform}X", f"{dst_node}.{transform}X")
    cmds.connectAttr(f"{src_node}.{transform}Y", f"{dst_node}.{transform}Y")
    cmds.connectAttr(f"{src_node}.{transform}Z", f"{dst_node}.{transform}Z")


def MBR_CopyAndConnectSkeleton(origin):
    '''
    PURPOSE:        To copy the bind skeleton and connect the copy to the original bind
    PROCEDURE:      > Duplicate hierarchy
                    > Delete everything that is not a joint
                    > Unlock all the joints
                    > Connect the translates, rotates, and scales
                    > Parent copy to the world
                    > Add deleteMe attr
    PRESUMPTIONS:   > No joints are children of anything but other joints
    '''

    new_hierarchy = []

    if origin != "Error" and cmds.objExists(origin):
        dup_hierarchy = cmds.duplicate(origin)
        temp_hierarchy = cmds.listRelatives(dup_hierarchy[0], ad=True, f=True)

        for cur in temp_hierarchy:
            if cmds.objExists(cur):
                if cmds.objectType(cur) != 'joint':
                    cmds.delete(cur)

        MBR_UnlockJointsTransforms(dup_hierarchy[0])

        orig_hierarchy = cmds.listRelatives(origin, ad=True, type='joint')
        new_hierarchy = cmds.listRelatives(dup_hierarchy[0], ad=True, type='joint')

        orig_hierarchy.append(origin)
        new_hierarchy.append(dup_hierarchy[0])

        for index in range(len(orig_hierarchy)):
            MBR_ConnectAttrs(orig_hierarchy[index], new_hierarchy[index], 'translate')
            MBR_ConnectAttrs(orig_hierarchy[index], new_hierarchy[index], 'rotate')
            MBR_ConnectAttrs(orig_hierarchy[index], new_hierarchy[index], 'scale')

        cmds.parent(dup_hierarchy[0], world=True)
        MBR_TagForGarbage(dup_hierarchy[0])

    return new_hierarchy


def MBR_TransformToOrigin(origin, start_frame, end_frame, zero_origin):
    '''
    PURPOSE:        Translate export skeleton to origin. May or may not kill origin animation depending on input
    PROCEDURE:      > Bake the animation onto our origin
                    > Create an animLayer
                    > animLayer will be either additive or override depending on parameter we pass
                    > Add deleteMe attr to animLayer
                    > Move to origin
    PRESUMPTIONS:   > Origin is valid
                    > end frame is greater than start frame
                    > zero_origin is boolean
    '''

    cmds.bakeResults(
        origin,
        t=(start_frame, end_frame),
        at=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'],
        hi='none')

    cmds.select(cl=True)
    cmds.select(origin)

    new_anim_layer = ''

    if zero_origin:
        new_anim_layer = cmds.animLayer(aso=True, mute=False, solo=False, override=True, passthrough=True, lock=False)
        cmds.setAttr(f"{new_anim_layer}.rotationAccumulationMode", 0)
        cmds.setAttr(f"{new_anim_layer}.scaleAccumulationMode", 1)
    else:
        new_anim_layer = cmds.animLayer(aso=True, mute=False, solo=False, override=False, passthrough=False, lock=False)

    MBR_TagForGarbage(new_anim_layer)

    # Turn animLayer on
    cmds.animlayer(new_anim_layer, edit=True, weight=1)
    cmds.setKeyframe(f"{new_anim_layer}.weight")

    # Move origin animation to world origin
    cmds.setAttr(f"{origin}.translate", 0, 0, 0)
    cmds.setAttr(f"{origin}.rotate", 0, 0, 0)
    cmds.setKeyframe(origin, al=new_anim_layer, t=start_frame)


# -------------------------------------------
#
#       AnimLayers export functions
#
# -------------------------------------------

def MBR_SetAnimLayersSettings(export_node):
    '''
    PURPOSE:        Record the animLayer settings used in animation and store in the export_node as a string
    PROCEDURE:      > List all the animLayers. Query their mute and solo attributes
                    > List them in one single string
                    > Uses ; as sentinal value to split separate animLayers
                    > Uses , as sentinal value to split separate fields for animLayer
                    > Uses = as sentinal value to split separate attrs from their values in field
    PRESUMPTIONS:   None
    '''

    if not cmds.attributeQuery('animLayers', node=export_node, exists=True):
        MBR_AddFBXNodeAttrs(export_node)

    anim_layers = cmds.ls(type='animLayer')

    anim_layer_cmd_str = ''

    for cur_layer in animLayers:
        mute = cmds.animLayer(cur_layer, query=True, mute=True)
        solo = cmds.animLayer(cur_layer, query=True, solo=True)
        anim_layer_cmd_str += f"{cur_layer}, mute={str(mute)}, solo={str(solo)};"

    cmds.setAttr(f"{export_node}.animLayers", anim_layer_cmd_str, type='string')


def MBR_SetAnimLayersFromSettings(export_node):
    '''
    PURPOSE:        Set the animLayers based on the string value in the export_node
    PROCEDURE:      > Use pre-defined sentinal values to split the string for separate animLayers
                    and parse out the attributes and their values, then set
    PRESUMPTIONS:   > Uses ; as sentinal value to split separate animLayers
                    > Uses , as sentinal value to split separate fields for animLayer
                    > Uses = as sentinal value to split separate attrs from their values in field
                    > Order is Layer, mute, solo
    '''

    if cmds.objExists(export_node) and not cmds.objExists(f"{export_node}.animLayers"):
        anim_layers_root_string = cmds.getAttr(f"{export_node}.animLayers", asString=True)

        if anim_layers_root_string:
            anim_layer_entries = anim_layers_root_string.split(';')

            for cur_entry in anim_layer_entries:
                if cur_entry:
                    fields = cur_entry.split(',')

                    anim_layer_field = fields[0]
                    cur_mute_field = fields[1]
                    cur_solo_field = fields[2]

                    mute_field_str = cur_mute_field.split('=')
                    solo_field_str = cur_solo_field.split('=')

                    # Convert strings to bool value
                    mute_field_bool = True
                    solo_field_bool = True

                    if mute_field_str[1] != True:
                        mute_field_bool = False

                    if solo_field_str[1] != True:
                        solo_field_bool = False

                    cmds.animLayer(anim_layer_field, edit=True, mute=mute_field_bool, solo=solo_field_bool)


def MBR_ClearAnimLayerSettings(export_node):
    '''
    PURPOSE:        Clear the animLayer settings on the export node
    PROCEDURE:      > Set the export_node.animLayers attribute to an empty string
    PRESUMPTIONS:   None
    '''

    cmds.setAttr(f"{export_node}.animLayers", '', type='string')


# -------------------------------------------
#
#       Export functions
#
# -------------------------------------------

def MBR_SetFBXExportOptionsAnimation(start, end):
    '''
    PURPOSE:
    PROCEDURE:
    PRESUMPTIONS:
    '''

    MBR_FBXExportOption('FBXExportAnimationOnly', 0)
    MBR_FBXExportOption('FBXExportBakeComplexAnimation', 1)
    MBR_FBXExportOption('FBXExportBakeComplexStart', start)
    MBR_FBXExportOption('FBXExportBakeComplexEnd', end)
    MBR_FBXExportOption('FBXExportBakeResampleAnimation', 1)
    MBR_FBXExportOption('FBXExportConstraints', 0)
    MBR_FBXExportOption('FBXExportInputConnections', 0)
    MBR_FBXExportOption('FBXExportShapes', 1)
    MBR_FBXExportOption('FBXExportSmoothMesh', 1)


def MBR_SetFBXExportOptionsModel():
    '''
    PURPOSE:
    PROCEDURE:
    PRESUMPTIONS:
    '''

    MBR_FBXExportOption('FBXExportSkins', 1)
    MBR_FBXExportOption('FBXExportShapes', 1)
    MBR_FBXExportOption('FBXExportSmoothingGroups', 1)
    MBR_FBXExportOption('FBXExportSmoothMesh', 1)
    MBR_FBXExportOption('FBXExportAnimationOnly', 0)
    MBR_FBXExportOption('FBXExportBakeComplexAnimation', 0)
    MBR_FBXExportOption('FBXExportBakeComplexStart', 0)
    MBR_FBXExportOption('FBXExportBakeComplexEnd', 0)
    MBR_FBXExportOption('FBXExportBakeResampleAnimation', 1)
    MBR_FBXExportOption('FBXExportConstraints', 0)
    MBR_FBXExportOption('FBXExportInputConnections', 0)


def MBR_ExportFBX(export_node):
    '''
    PURPOSE:
    PROCEDURE:
    PRESUMPTIONS:
    '''

    cur_wks = cmds.workspace(q=True, rd=True)
    file_name = cmds.getAttr(f"{export_node}.exportName")

    if file_name:
        new_fbx = cur_wks + file_name
        cmds.file(new_fbx, force=True, type='FBX export', pr=True, es=True)
    else:
        cmds.warning(f"No Valid Export Filename for Export Node {export_node}\n")


def MBR_ExportFBXAnimation(character_name, export_node):
    '''
    PURPOSE:
    PROCEDURE:
    PRESUMPTIONS:
    '''

    MBR_ClearGarbage()
    characters = []

    if character_name:
        characters.append(character_name)
    else:
        reference = cmds.file(reference=1, q=True)
        for cur_ref in references:
            characters.append(cmds.file(cur_ref, namespace=1, q=True))

    for cur_character in characters:

        # Get the meshes with blendshapes
        meshes = MBR_FindMeshWithBlendshapes(cur_character)

        # Get origin
        origin = MBR_ReturnOrigin(cur_character)

        export_nodes = []

        if export_node:
            export_nodes.append(export_node)
        else:
            export_nodes = MBR_ReturnFBXExportNodes(origin)

        for cur_export_node in export_nodes:
            if cmds.getAttr(f"{cur_export_node}.export") and origin != 'Error':
                export_rig = MBR_CopyAndConnectSkeleton(origin)

                start_frame = cmds.playbackOptions(q=True, minTime=1)
                end_frame = cmds.playbackOptions(q=True, maxTime=1)

                sub_anim_check = cmds.getAttr(f"{cur_export_node}.useSubRange")

                if sub_anim_check:
                    start_frame = cmds.getAttr(f"{cur_export_node}.startFrame")
                    end_frame = cmds.geteAttr(f"{cur_export_node}.endFrame")

                if cmds.getAttr(f"{cur_export_node}.moveToOrigin"):
                    new_origin = cmds.listConnections(f"{origin}.translateX", source=False, d=True)
                    zero_origin_flag = cmds.getAttr(f"{cur_export_node}.zeroOrigin")
                    MBR_TransformToOrigin(new_origin[0], start_frame, end_frame, zero_origin_flag)

                cmds.select(clear=True)
                cmds.select(export_rig, add=True)
                cmds.select(meshes, add=True)

                MBR_SetAnimLayersFromSettings(cur_export_node)

                MBR_SetFBXExportOptionsAnimation(start_frame, end_frame)
                MBR_ExportFBX(cur_export_node)

            MBR_ClearGarbage()


def MBR_ExportFBXCharacter(export_node):
    '''
    PURPOSE:
    PROCEDURE:
    PRESUMPTIONS:
    '''

    origin = MBR_ReturnOrigin('')
    export_nodes = []

    if export_node:
        export_nodes.append(export_node)
    else:
        export_nodes = MBR_ReturnFBXExportNodes(origin)

    parent_node = cmds.listRelatives(origin, parent=True, fullPath=True)

    if parent_node:
        cmds.parent(origin, world=True)

    for cur_export_node in export_nodes:
        if cmds.getAttr(f"{cur_export_node}.export"):
            MBR_SetFBXExportOptionsModel()

            cmds.select(clear=True)

            meshes = MBR_ReturnConnectedMeshes(cur_export_node)
            cmds.select(origin, add=True)
            cmds.select(meshes, add=True)

            MBR_ExportFBX(cur_export_node)

        if parent_node:
            cmds.parent(origin, parent_node[0])


selection = cmds.ls(selection=True)[0]
Return_Origin('JOINT')

'''
global proc MBR_SetFBXExportOptionsAnimation(int $start, int $end)
{
    FBXExportAnimationOnly -v 0;
    FBXExportBakeComplexAnimation -v 1;
    FBXExportBakeComplexStart -v $start;
    FBXExportBakeComplexEnd -v $end;
    FBXExportBakeResampleAnimation -v 1;
    FBXExportConstraints -v 0;
    FBXExportInputConnections -v 0;
    FBXExportShapes -v 1;
    FBXExportSmoothMesh -v 1;
}
'''