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
    'mbr_egn_pose_ik_fk_snap',
    'mbr_egn_pose_fk_ik_snap',
    'mbr_egn_anim_ik_fk_snap',
    'mbr_egn_anim_ik_fk_snap',
]

# -------------------------------------
#
#       Engine Functions
#
# -------------------------------------

'''
PURPOSE:        Matches the FK controls to where the IK controls are
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_pose_ik_fk_snap(char_nmp, limb_var, side_var):

    # Lists
    if limb_var == 'Arm' and side_var == 'Right':
        side = 'r'
        limb_part = ['upperarm', 'lowerarm', 'hand']

    elif limb_var == 'Arm' and side_var == 'Left':
        side = 'l'
        limb_part = ['upperarm', 'lowerarm', 'hand']

    elif limb_var == 'Leg' and side_var == 'Right':
        side = 'r'
        limb_part = ['thigh', 'knee', 'ankle']

    elif limb_var == 'Leg' and side_var == 'Left':
        side = 'l'
        limb_part = ['thigh', 'knee', 'ankle']

    # Limb Joints List List
    limb_rig_joint_list = []
    for item in range(3):
        limb_rig_joint_name = f"{char_nmp}:{side}_{limb_part[item]}"
        limb_rig_joint_list.append(limb_rig_joint_name)

    # Limb Controls List
    limb_rig_ctrls_list = []
    for item in range(3):
        limb_rig_ctrl_name = f"{char_nmp}:{side}_{limb_part[item]}_fk_ctrl"
        limb_rig_ctrls_list.append(limb_rig_ctrl_name)

        # Empty List for Locators
    limb_locs_list = []

    # Create three locators on chosen limb joints
    upper_loc = cmds.spaceLocator(n='upper_loc')
    lower_loc = cmds.spaceLocator(n='lower_loc')
    end_loc = cmds.spaceLocator(n='end_loc')

    limb_locs_list.append(upper_loc[0])
    limb_locs_list.append(lower_loc[0])
    limb_locs_list.append(end_loc[0])

    # Snap the three locators on chosen limb joints
    for item in range(3):
        cmds.select(limb_locs_list[item], r=True)
        cmds.select(limb_rig_joint_list[item], tgl=True)
        cmds.MatchTransform()

    # Constrain limb controls to locators
    for item in range(3):
        cmds.select(limb_locs_list[item], r=True)
        cmds.select(limb_rig_ctrls_list[item], tgl=True)
        cmds.orientConstraint()

    # Key limb controls
    for item in range(3):
        cmds.setKeyframe(limb_rig_ctrls_list[item])

    # Change attribute from IK to FK
    if cmds.attributeQuery('IkFk', node=f"{char_nmp}:{side}_{limb_part[-1]}_switch_ctrl", exists=True):
        cmds.setAttr(f"{char_nmp}:{side}_{limb_part[-1]}_switch_ctrl.IkFk", 1)

    elif cmds.attributeQuery('ikFkBlend', node=f"{char_nmp}:{side}_{limb_part[-1]}_switch_ctrl", exists=True):
        cmds.setAttr(f"{char_nmp}:{side}_{limb_part[-1]}_switch_ctrl.ikFkBlend", 0)

    else:
        return

    # Delete locators
    for item in range(3):
        cmds.delete(limb_locs_list[item])

    cmds.select(cl=True)

'''
PURPOSE:        Matches the IK controls to where the FK controls are
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_pose_fk_ik_snap(char_nmp, limb_var, side_var):

    # Lists
    if limb_var == 'Arm' and side_var == 'Right':
        side = 'r'
        limb_fk_names = ['upperarm', 'lowerarm', 'hand']
        limb_ik_names = ['hand_ikHandle', 'lowerarm_pv']

    elif limb_var == 'Arm' and side_var == 'Left':
        side = 'l'
        limb_fk_names = ['upperarm', 'lowerarm', 'hand']
        limb_ik_names = ['hand_ikHandle', 'lowerarm_pv']

    elif limb_var == 'Leg' and side_var == 'Right':
        side = 'r'
        limb_fk_names = ['thigh', 'knee', 'ankle']
        limb_ik_names = ['ankle_ikHandle', 'knee_pv']

    elif limb_var == 'Leg' and side_var == 'Left':
        side = 'l'
        limb_fk_names = ['thigh', 'knee', 'ankle']
        limb_ik_names = ['ankle_ikHandle', 'knee_pv']

    # Limb Joints List
    limb_rig_joint_list = []
    for item in range(3):
        limb_rig_joint_name = f"{char_nmp}:{side}_{limb_fk_names[item]}"
        limb_rig_joint_list.append(limb_rig_joint_name)

    # Limb FK Controls List
    limb_rig_fk_ctrls_list = []
    for item in range(3):
        limb_rig_fk_ctrl_name = f"{char_nmp}:{side}_{limb_fk_names[item]}_fk_ctrl"
        limb_rig_fk_ctrls_list.append(limb_rig_fk_ctrl_name)

    # Limb IK Controls List
    limb_rig_ik_ctrls_list = []
    for item in range(2):
        limb_rig_ik_ctrl_name = f"{char_nmp}:{side}_{limb_ik_names[item]}_ctrl"
        limb_rig_ik_ctrls_list.append(limb_rig_ik_ctrl_name)

    # Empty Lists for FK Joints and FK Locators
    limb_custom_fk_jnts = []
    limb_custom_fk_locs = []

    # Create chain of three joints
    cmds.select(cl=True)
    cmds.joint(n='upper_jnt')
    cmds.joint(n='lower_jnt')
    cmds.joint(n='end_jnt')

    limb_custom_fk_jnts.append('upper_jnt')
    limb_custom_fk_jnts.append('lower_jnt')
    limb_custom_fk_jnts.append('end_jnt')

    # Snap the three joints on chosen limb joints
    for item in range(3):
        cmds.select(limb_custom_fk_jnts[item], r=True)
        cmds.select(limb_rig_joint_list[item], tgl=True)
        cmds.MatchTransform()

    # Orienting Joints
    cmds.makeIdentity('upper_jnt', apply=True, r=True)
    cmds.makeIdentity('lower_jnt', apply=True, r=True)
    cmds.makeIdentity('end_jnt', apply=True, r=True)

    cmds.joint('upper_jnt', e=True, oj='xyz', sao='yup', ch=True, zso=True)

    # Create three locators on chosen limb joints
    upper_loc = cmds.spaceLocator(n='upper_loc')
    lower_loc = cmds.spaceLocator(n='lower_loc')
    end_loc = cmds.spaceLocator(n='end_loc')

    limb_custom_fk_locs.append(upper_loc[0])
    limb_custom_fk_locs.append(lower_loc[0])
    limb_custom_fk_locs.append(end_loc[0])

    # Snap the three locators on chosen limb joints
    for item in range(3):
        cmds.select(limb_custom_fk_locs[item], r=True)
        cmds.select(limb_custom_fk_jnts[item], tgl=True)
        cmds.MatchTransform()

    # Create IK Handle
    cmds.ikHandle(startJoint=limb_custom_fk_jnts[0], endEffector=limb_custom_fk_jnts[-1], solver='ikRPsolver')
    cmds.parent('ikHandle1', limb_custom_fk_locs[-1])

    # Pole Vector and other constraints
    cmds.select(limb_custom_fk_locs[1], r=True)
    cmds.select('ikHandle1', tgl=True)
    cmds.poleVectorConstraint()

    cmds.select(limb_custom_fk_locs[-1], r=True)
    cmds.select(limb_custom_fk_jnts[-1], tgl=True)
    cmds.orientConstraint()

    cmds.select(limb_custom_fk_locs[0], r=True)
    cmds.select(limb_custom_fk_jnts[0], tgl=True)
    cmds.pointConstraint()

    # Constraint controls to locators
    cmds.select('ikHandle1', r=True)
    cmds.select(limb_rig_ik_ctrls_list[0], tgl=True)
    cmds.parentConstraint()

    cmds.select(limb_custom_fk_locs[1], r=True)
    cmds.select(limb_rig_ik_ctrls_list[1], tgl=True)
    cmds.pointConstraint()

    # Key limb controls
    for item in range(2):
        cmds.setKeyframe(limb_rig_ik_ctrls_list[item])

    # Delete setup
    for item in range(3):
        cmds.delete(limb_custom_fk_locs[item])

    cmds.delete(limb_custom_fk_jnts[0])

    # Match transform IK control to the hand fk joint (Arm)
    if side == 'l' and limb_var == 'Arm':
        cmds.select(limb_rig_ik_ctrls_list[0], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[-1]}_fk", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[0], r=True, os=True, rotation=(-90, 0, 0))

        cmds.select(limb_rig_ik_ctrls_list[-1], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_fk", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[1], r=True, os=True, translation=(0, -40, 0))

    # Match transform Pole Vector to the lower fk joint (Arm)
    elif side == 'r' and limb_var == 'Arm':
        cmds.select(limb_rig_ik_ctrls_list[0], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[-1]}_fk", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[0], r=True, os=True, rotation=(90, 0, 0))

        cmds.select(limb_rig_ik_ctrls_list[-1], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_fk", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[1], r=True, os=True, translation=[0, 40, 0])

    # Match transform IK control to the hand fk joint (Leg)
    elif side == 'l' and limb_var == 'Leg':
        cmds.select(limb_rig_ik_ctrls_list[-1], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_fk", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[1], r=True, os=True, translation=(0, 0, 40))

    # Match transform Pole Vector to the lower fk joint (Leg)
    elif side == 'r' and limb_var == 'Leg':
        cmds.select(limb_rig_ik_ctrls_list[-1], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_ik", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[1], r=True, os=True, translation=(0, 0, -40))

    # Change attribute from IK to FK
    if cmds.attributeQuery('IkFk', node=f"{char_nmp}:{side}_{limb_fk_names[-1]}_switch_ctrl", exists=True):
        cmds.setAttr(f"{char_nmp}:{side}_{limb_fk_names[-1]}_switch_ctrl.IkFk", 0)

    elif cmds.attributeQuery('ikFkBlend', node=f"{char_nmp}:{side}_{limb_fk_names[-1]}_switch_ctrl", exists=True):
        cmds.setAttr(f"{char_nmp}:{side}_{limb_fk_names[-1]}_switch_ctrl.ikFkBlend", 1)

    else:
        print('It didnt do anything')

    # Key limb controls
    for item in range(2):
        cmds.setKeyframe(limb_rig_ik_ctrls_list[item])

    cmds.select(cl=True)

'''
PURPOSE:        Matches the FK controls to where the IK controls are
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_anim_ik_fk_snap(char_nmp, limb_var, side_var):

    # Variables
    timeline_start = int(cmds.playbackOptions(q=True, min=True))
    timeline_end = int(cmds.playbackOptions(q=True, max=True))

    # Lists
    if limb_var == 'Arm' and side_var == 'Right':
        side = 'r'
        limb_part = ['upperarm', 'lowerarm', 'hand']

    elif limb_var == 'Arm' and side_var == 'Left':
        side = 'l'
        limb_part = ['upperarm', 'lowerarm', 'hand']

    elif limb_var == 'Leg' and side_var == 'Right':
        side = 'r'
        limb_part = ['thigh', 'knee', 'ankle']

    elif limb_var == 'Leg' and side_var == 'Left':
        side = 'l'
        limb_part = ['thigh', 'knee', 'ankle']

    # Limb Joints List List
    limb_rig_joint_list = []
    for item in range(3):
        limb_rig_joint_name = f"{char_nmp}:{side}_{limb_part[item]}"
        limb_rig_joint_list.append(limb_rig_joint_name)

    # Limb Controls List
    limb_rig_ctrls_list = []
    for item in range(3):
        limb_rig_ctrl_name = f"{char_nmp}:{side}_{limb_part[item]}_fk_ctrl"
        limb_rig_ctrls_list.append(limb_rig_ctrl_name)

        # Empty List for Locators
    limb_locs_list = []

    # Create three locators on chosen limb joints
    upper_loc = cmds.spaceLocator(n='upper_loc')
    lower_loc = cmds.spaceLocator(n='lower_loc')
    end_loc = cmds.spaceLocator(n='end_loc')

    limb_locs_list.append(upper_loc[0])
    limb_locs_list.append(lower_loc[0])
    limb_locs_list.append(end_loc[0])

    # Snap the three locators on chosen limb joints
    for item in range(3):
        cmds.select(limb_rig_joint_list[item], r=True)
        cmds.select(limb_locs_list[item], tgl=True)
        cmds.parentConstraint()

    # Constrain limb controls to locators
    for item in range(3):
        cmds.select(limb_locs_list[item], r=True)
        cmds.select(limb_rig_ctrls_list[item], tgl=True)
        cmds.orientConstraint()

    # Key limb controls
    cmds.select(cl=True)
    for item in range(3):
        cmds.select(limb_rig_ctrls_list[item])
        bake()

    # Change attribute from IK to FK
    if cmds.attributeQuery('IkFk', node=f"{char_nmp}:{side}_{limb_part[-1]}_switch_ctrl", exists=True):
        cmds.setAttr(f"{char_nmp}:{side}_{limb_part[-1]}_switch_ctrl.IkFk", 1)
        cmds.cutKey(f"{char_nmp}:{side}_{limb_part[-1]}_switch_ctrl.IkFk", time=(timeline_start, timeline_end))

    elif cmds.attributeQuery('ikFkBlend', node=f"{char_nmp}:{side}_{limb_part[-1]}_switch_ctrl", exists=True):
        cmds.setAttr(f"{char_nmp}:{side}_{limb_part[-1]}_switch_ctrl.ikFkBlend", 0)
        cmds.cutKey(f"{char_nmp}:{side}_{limb_part[-1]}_switch_ctrl.ikFkBlend", time=(timeline_start, timeline_end))

    else:
        return

    # Delete locators
    for item in range(3):
        cmds.delete(limb_locs_list[item])

'''
PURPOSE:        Matches (mostly) the IK controls to where the FK controls are
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_anim_fk_ik_snap(char_nmp, limb_var, side_var):

    # Variables
    timeline_start = int(cmds.playbackOptions(q=True, min=True))
    timeline_end = int(cmds.playbackOptions(q=True, max=True))

    # Lists
    if limb_var == 'Arm' and side_var == 'Right':
        side = 'r'
        limb_fk_names = ['upperarm', 'lowerarm', 'hand']
        limb_ik_names = ['hand_ikHandle', 'lowerarm_pv']

    elif limb_var == 'Arm' and side_var == 'Left':
        side = 'l'
        limb_fk_names = ['upperarm', 'lowerarm', 'hand']
        limb_ik_names = ['hand_ikHandle', 'lowerarm_pv']

    elif limb_var == 'Leg' and side_var == 'Right':
        side = 'r'
        limb_fk_names = ['thigh', 'knee', 'ankle']
        limb_ik_names = ['ankle_ikHandle', 'knee_pv']

    elif limb_var == 'Leg' and side_var == 'Left':
        side = 'l'
        limb_fk_names = ['thigh', 'knee', 'ankle']
        limb_ik_names = ['ankle_ikHandle', 'knee_pv']

    # Limb Joints List List
    limb_rig_joint_list = []
    for item in range(3):
        limb_rig_joint_name = f"{char_nmp}:{side}_{limb_fk_names[item]}"
        limb_rig_joint_list.append(limb_rig_joint_name)

    # Limb FK Controls List
    limb_rig_fk_ctrls_list = []
    for item in range(3):
        limb_rig_fk_ctrl_name = f"{char_nmp}:{side}_{limb_fk_names[item]}_fk_ctrl"
        limb_rig_fk_ctrls_list.append(limb_rig_fk_ctrl_name)

        # Limb IK Controls List
    limb_rig_ik_ctrls_list = []
    for item in range(2):
        limb_rig_ik_ctrl_name = f"{char_nmp}:{side}_{limb_ik_names[item]}_ctrl"
        limb_rig_ik_ctrls_list.append(limb_rig_ik_ctrl_name)

    # Empty Lists for FK Joints and FK Locators
    limb_custom_fk_jnts = []
    limb_custom_fk_locs = []

    # Create chain of three joints
    cmds.select(cl=True)
    cmds.joint(n='upper_jnt')
    cmds.joint(n='lower_jnt')
    cmds.joint(n='end_jnt')

    limb_custom_fk_jnts.append('upper_jnt')
    limb_custom_fk_jnts.append('lower_jnt')
    limb_custom_fk_jnts.append('end_jnt')

    # Snap the three joints on chosen limb joints
    for item in range(3):
        cmds.select(limb_custom_fk_jnts[item], r=True)
        cmds.select(limb_rig_joint_list[item], tgl=True)
        cmds.MatchTransform()

    # Orienting Joints
    cmds.makeIdentity('upper_jnt', apply=True, r=True)
    cmds.makeIdentity('lower_jnt', apply=True, r=True)
    cmds.makeIdentity('end_jnt', apply=True, r=True)

    cmds.joint('upper_jnt', e=True, oj='xyz', sao='yup', ch=True, zso=True)

    # Create three locators on chosen limb joints
    upper_loc = cmds.spaceLocator(n='upper_loc')
    lower_loc = cmds.spaceLocator(n='lower_loc')
    end_loc = cmds.spaceLocator(n='end_loc')

    limb_custom_fk_locs.append(upper_loc[0])
    limb_custom_fk_locs.append(lower_loc[0])
    limb_custom_fk_locs.append(end_loc[0])

    # Snap the three locators on chosen limb joints
    for item in range(3):
        cmds.select(limb_rig_joint_list[item], r=True)
        cmds.select(limb_custom_fk_locs[item], tgl=True)
        cmds.parentConstraint()

    # Create IK Handle
    cmds.ikHandle(startJoint=limb_custom_fk_jnts[0], endEffector=limb_custom_fk_jnts[-1], solver='ikRPsolver')
    cmds.parent('ikHandle1', limb_custom_fk_locs[-1])

    # Bake Locators
    for item in range(3):
        cmds.select(limb_custom_fk_locs[item], r=True)
        bake()
        cmds.delete(limb_custom_fk_locs[item], constraints=True)

    # Pole Vector and other constraints
    cmds.select(limb_custom_fk_locs[1], r=True)
    cmds.select('ikHandle1', tgl=True)
    cmds.poleVectorConstraint()

    cmds.select(limb_custom_fk_locs[-1], r=True)
    cmds.select(limb_custom_fk_jnts[-1], tgl=True)
    cmds.orientConstraint()

    cmds.select(limb_custom_fk_locs[0], r=True)
    cmds.select(limb_custom_fk_jnts[0], tgl=True)
    cmds.pointConstraint()

    # Constraint controls to locators
    cmds.select('ikHandle1', r=True)
    cmds.select(limb_rig_ik_ctrls_list[0], tgl=True)
    cmds.parentConstraint()

    cmds.select(limb_custom_fk_locs[1], r=True)
    cmds.select(limb_rig_ik_ctrls_list[1], tgl=True)
    cmds.pointConstraint()

    # Bake Controls
    for item in range(2):
        cmds.select(limb_rig_ik_ctrls_list[item], r=True)
        bake()

    # Delete setup
    for item in range(3):
        cmds.delete(limb_custom_fk_locs[item])

    cmds.delete(limb_custom_fk_jnts[0])

    # Match transform IK control to the hand fk joint (Arm)
    if side == 'l' and limb_var == 'Arm':
        cmds.select(limb_rig_ik_ctrls_list[0], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[-1]}_fk", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[0], r=True, os=True, rotation=(-90, 0, 0))

        cmds.select(limb_rig_ik_ctrls_list[-1], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_fk", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[1], r=True, os=True, translation=(0, -40, 0))

    # Match transform Pole Vector to the lower fk joint (Arm)
    elif side == 'r' and limb_var == 'Arm':
        cmds.select(limb_rig_ik_ctrls_list[0], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[-1]}_fk", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[0], r=True, os=True, rotation=(90, 0, 0))

        cmds.select(limb_rig_ik_ctrls_list[-1], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_fk", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[1], r=True, os=True, translation=[0, 40, 0])

    # Match transform IK control to the hand fk joint (Leg)
    elif side == 'l' and limb_var == 'Leg':
        cmds.select(limb_rig_ik_ctrls_list[-1], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_fk", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[1], r=True, os=True, translation=(0, 0, 40))

    # Match transform Pole Vector to the lower fk joint (Leg)
    elif side == 'r' and limb_var == 'Leg':
        cmds.select(limb_rig_ik_ctrls_list[-1], r=True)
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_ik", tgl=True)
        cmds.MatchTransform()
        cmds.xform(limb_rig_ik_ctrls_list[1], r=True, os=True, translation=(0, 0, -40))

    # Constraint controls to snap joints
    if side == 'l' and limb_var == 'Arm':
        # Constraint IK control to the hand fk joint
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[-1]}_fk", r=True)
        cmds.select(limb_rig_ik_ctrls_list[0], tgl=True)
        cmds.parentConstraint(mo=True)

        # Constraint Pole Vector to the lower fk joint
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_fk", r=True)
        cmds.select(limb_rig_ik_ctrls_list[-1], tgl=True)
        cmds.parentConstraint(mo=True)

    elif side == 'r' and limb_var == 'Arm':
        # Constraint IK control to the hand fk joint
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[-1]}_fk", r=True)
        cmds.select(limb_rig_ik_ctrls_list[0], tgl=True)
        cmds.parentConstraint(mo=True)

        # Constraint Pole Vector to the lower fk joint
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_fk", r=True)
        cmds.select(limb_rig_ik_ctrls_list[-1], tgl=True)
        cmds.parentConstraint(mo=True)

    elif side == 'l' and limb_var == 'Leg':
        # Constraint Pole Vector to the lower fk joint
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_ik", r=True)
        cmds.select(limb_rig_ik_ctrls_list[-1], tgl=True)
        cmds.parentConstraint(mo=True)

    elif side == 'r' and limb_var == 'Leg':
        # Constraint Pole Vector to the lower fk joint
        cmds.select(f"{char_nmp}:{side}_{limb_fk_names[1]}_ik", r=True)
        cmds.select(limb_rig_ik_ctrls_list[-1], tgl=True)
        cmds.parentConstraint(mo=True)

    # Bake Controls
    for item in range(2):
        cmds.select(limb_rig_ik_ctrls_list[item], r=True)
        bake()

    # Change attribute from IK to FK
    if cmds.attributeQuery('IkFk', node=f"{char_nmp}:{side}_{limb_fk_names[-1]}_switch_ctrl", exists=True):
        cmds.setAttr(f"{char_nmp}:{side}_{limb_fk_names[-1]}_switch_ctrl.IkFk", 0)
        cmds.cutKey(f"{char_nmp}:{side}_{limb_fk_names[-1]}_switch_ctrl.IkFk", time=(timeline_start, timeline_end))

    elif cmds.attributeQuery('ikFkBlend', node=f"{char_nmp}:{side}_{limb_fk_names[-1]}_switch_ctrl", exists=True):
        cmds.setAttr(f"{char_nmp}:{side}_{limb_fk_names[-1]}_switch_ctrl.ikFkBlend", 1)
        cmds.cutKey(f"{char_nmp}:{side}_{limb_fk_names[-1]}_switch_ctrl.ikFkBlend", time=(timeline_start, timeline_end))
    else:
        print('It didnt do anything')