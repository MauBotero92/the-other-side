# -------------------------------------------
#
#       Import Modules
#
# -------------------------------------------

import maya.cmds as cmds

# -------------------------------------------
#
#       Export Config
#
# -------------------------------------------

__all__ = [
    'mbr_egn_shot_tree_create_nulls',
    'mbr_egn_shot_tree_delete_unused_nulls',
    'mbr_egn_shot_tree_window',
]

# -------------------------------------------
#
#       Functions
#
# -------------------------------------------

'''
PURPOSE:        Create null groups for shot organization
PROCEDURE:      > Create nulls and name them accordingly
                > Set the color of each group
ASSUMPTIONS:    None
'''
def mbr_egn_shot_tree_create_nulls():

    null_list = ['CAM', 'CHAR', 'CRE', 'PROPS', 'SET', 'MISC', 'LIGHTS', 'VEH', 'VFX']

    for null in null_list:

        if not cmds.objExists(null):

            cmds.group(empty=True, name=null)
            cmds.setAttr(f"{null}.useOutlinerColor", True)

            if null == 'CAM':
                cmds.setAttr('CAM.outlinerColor', 1, 0, 0, type='double3')

            elif null == 'CHAR':
                cmds.setAttr('CHAR.outlinerColor', 1, .622, .078, type='double3')

            elif null == 'PROPS':
                cmds.setAttr('PROPS.outlinerColor', 1, 1, 0, type='double3')

            elif null == 'CRE':
                cmds.setAttr('CRE.outlinerColor', 0, 1, 0, type='double3')

            elif null == 'SET':
                cmds.setAttr('SET.outlinerColor', 0, 1, 1, type='double3')

            elif null == 'MISC':
                cmds.setAttr('MISC.outlinerColor', 1, 1, 1, type='double3')

            elif null == 'LIGHTS':
                cmds.setAttr('LIGHTS.outlinerColor', .896, .896, .281, type='double3')

            elif null == 'VEH':
                cmds.setAttr('VEH.outlinerColor', 1, 0, 1, type='double3')

            elif null == 'VFX':
                cmds.setAttr('VFX.outlinerColor', .549, .215, 1, type='double3')
'''
PURPOSE:        Clear unused nulls
PROCEDURE:      > Set list with the names of the nulls
                > Delete the nulls that doesn't have any children
ASSUMPTIONS:    None
'''
def mbr_egn_shot_tree_delete_unused_nulls():

        null_list = ['CAM', 'CHAR', 'CRE', 'PROPS', 'SET', 'MISC', 'LIGHTS', 'VEH', 'VFX']

        for null in null_list:

            if cmds.objExists(null):

                children = cmds.listRelatives(null, children=True)

                if not children:
                    cmds.select(cl=True)
                    cmds.select(null, add=True)
                    cmds.delete()

'''
PURPOSE:        Confirm dialog with the two options for shot tree creation
PROCEDURE:      > Pops up a window asking the user if he wants to either create nulls or delete the unused nulls
                > Trigger the create_nulls function if user click the creation button, or delete_unused_nulls if user 
                clicks on delete nulls
ASSUMPTIONS:    None
'''
def mbr_egn_shot_tree_window():

    response = cmds.confirmDialog(t='Shot Tree', m='Select one option', b=[
        'Create Shot Tree',
        'Delete Unused Nulls',
        'Exit'
    ])

    if response == 'Create Shot Tree':
        mbr_egn_shot_tree_create_nulls()

    elif response == 'Delete Unused Nulls':
        mbr_egn_shot_tree_delete_unused_nulls()

    elif response == 'Exit':
        return