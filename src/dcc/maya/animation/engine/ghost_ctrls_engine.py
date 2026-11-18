# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import maya.cmds as cmds

# -------------------------------------
#
#       Export Config
#
# -------------------------------------

__all__ = [
    'mbr_egn_ghost_ctrls,'
]

# -------------------------------------
#
#       Engine Functions
#
# -------------------------------------

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_ghost_ctrls():

    # Get the current selection
    selection = cmds.ls(selection=True)

    if not selection:
        print("Please select at least one control/object.")
    else:
        count = 0

    for obj in selection:
        # Check Always Draw On Top on the selected object
        if cmds.attributeQuery('alwaysDrawOnTop', node=obj, exists=True):
            try:
                cmds.setAttr(f"{obj}.alwaysDrawOnTop", 0)
                count += 1
            except Exception as e:
                print(f"Could not modify {obj}: {e}")

        else:
            # Check the object's shapes
            shapes = cmds.listRelatives(
                obj, shapes=True, fullPath=True
            ) or []

            for shape in shapes:
                if cmds.attributeQuery('alwaysDrawOnTop', node=shape, exists=True):
                    try:
                        cmds.setAttr(f"{shape}.alwaysDrawOnTop", 0)
                        count += 1
                    except Exception as e:
                        print(f"Could not modify {shape}: {e}")

    print(f"Disabled 'Always Draw On Top' for {count} object(s).")