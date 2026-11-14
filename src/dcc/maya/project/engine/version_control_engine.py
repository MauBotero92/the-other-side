# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

from TOS_Pipeline.src.core.fs_utils import *

import os
import maya.cmds as cmds

# -------------------------------------------
#
#       Export Config
#
# -------------------------------------------

__all__ = [
    'mbr_egn_version_up_scene',
    'mbr_egn_subversion_up_scene',
    'mbr_egn_publish_scene'
]

# -------------------------------------------
#
#       Engine Functions
#
# -------------------------------------------

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_version_up_scene():

    # Get the current path of the file that is open and separates the path and the file name
    scene_full_name = cmds.file(q=True, sceneName=True)

    # Get the path of the directory, and the name of the file
    scene_file_name = os.path.basename(scene_full_name)
    scene_path_name = os.path.dirname(scene_full_name)

    # Isolate the version integers
    scene_file_l_index = scene_file_name.find('_', 9)
    scene_file_r_index = scene_file_name.rfind('_')

    scene_file_v = scene_file_name[scene_file_l_index+2:scene_file_r_index]
    scene_file_v_first_str = scene_file_v[0]
    scene_file_v_second_str = scene_file_v[1]
    scene_file_v_third_str = scene_file_v[2]

    # Versions up logic
    if scene_file_v_third_str != '9':
        scene_file_v_third_int = int(scene_file_v_third_str)
        scene_file_v_third_int += 1
        scene_file_v_new = f"{scene_file_v_first_str}{scene_file_v_second_str}{str(scene_file_v_third_int)}"

    elif scene_file_v_third_str == '9' and scene_file_v_second_str != '9':
        scene_file_v_second_int = int(scene_file_v_second_str)
        scene_file_v_second_int += 1
        scene_file_v_new = f"{scene_file_v_first_str}{str(scene_file_v_second_int)}0"

    elif scene_file_v_third_str == '9' and scene_file_v_second_str == '9':
        scene_file_v_first_int = int(scene_file_v_first_str)
        scene_file_v_first_int += 1
        scene_file_v_new = f"{str(scene_file_v_first_int)}00"

    # Rebuild scene file string
    scene_file_name_sliced = scene_file_name[:scene_file_l_index]
    scene_file_new_name = f"{scene_file_name_sliced}_v{scene_file_v_new}_00.ma"
    scene_path_new = f"{scene_path_name}/{scene_file_new_name}"

    # Checks if the new version already exists
    scene_v_new_first_str = scene_file_v_new[0]
    scene_v_new_second_str = scene_file_v_new[1]
    scene_v_new_third_str = scene_file_v_new[2]

    while os.path.exists(scene_path_new):
        scene_v_new_first_str = scene_file_v_new[0]
        scene_v_new_second_str = scene_file_v_new[1]
        scene_v_new_third_str = scene_file_v_new[2]

        if scene_v_new_third_str != '9':
            scene_v_new_third_int = int(scene_v_new_third_str)
            scene_v_new_third_int += 1
            scene_file_v_new = f"{scene_v_new_first_str}{scene_v_new_second_str}{str(scene_v_new_third_int)}"

        elif scene_v_new_third_str == '9' and scene_v_new_second_str != '9':
            scene_v_new_second_int = int(scene_v_new_second_str)
            scene_v_new_second_int += 1
            scene_file_v_new = f"{scene_v_new_first_str}{str(scene_v_new_second_int)}0"

        elif scene_v_new_third_str == '9' and scene_v_new_second_str == '9':
            scene_v_new_first_int = int(scene_v_new_first_str)
            scene_v_new_first_int += 1
            scene_file_v_new = f"{str(scene_v_new_first_int)}00"

        # Rebuild scene file string
        scene_file_name_sliced = scene_file_name[:scene_file_l_index]
        scene_file_new_name = f"{scene_file_name_sliced}_v{scene_file_v_new}_00.ma"
        scene_path_new = f"{scene_path_name}/{scene_file_new_name}"

    # Save the scene with the new name
    cmds.file(save=True, force=True, type='mayaAscii')
    cmds.file(rename=scene_path_new)
    cmds.file(save=True, force=True, type='mayaAscii')

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_subversion_up_scene():

    # Get the current path of the file that is open and separates the path and the file name
    scene_full_name = cmds.file(q=True, sceneName=True)

    # Get the path of the directory, and the name of the file
    scene_file_name = os.path.basename(scene_full_name)
    scene_path_name = os.path.dirname(scene_full_name)

    # Naming Convention Check Guard
    naming_layout_sample = 'T400_000_Layout_v001_00'
    naming_anim_sample = 'T400_000_Animation_v001_00'
    naming_lighting_sample = 'T400_000_Lighting_v001_00'

    naming_layout_length = len(naming_layout_sample)
    naming_anim_length = len(naming_anim_sample)
    naming_lighting_length = len(naming_lighting_sample)

    # Guard check for regular files
    if scene_file_name[0] != 'T':
        # Message Box - Warns the user that the current file doesn't follow the short naming convention
        warning_msg = wdg.QMessageBox()
        warning_msg.setWindowTitle('Warning')
        warning_msg.setText(
            "Your scene doesn't follow the naming conventions. You would like to save a copy with the naming conventions?")
        warning_msg.setIcon(wdg.QMessageBox.Question)

        warning_msg_accept_btn = warning_msg.addButton('Yes', wdg.QMessageBox.AcceptRole)
        warning_msg_decline_btn = warning_msg.addButton('No', wdg.QMessageBox.RejectRole)

        warning_msg.exec()
        warning_msg_clicked = warning_msg.clickedButton()

        if warning_msg_clicked == warning_msg_accept_btn:
            # Saves the file following the new naming conventions
            if 'layout' in scene_full_name:
                if len(scene_file_name[:-3]) != naming_layout_length:
                    if not scene_file_name[:-3].endswith('_00'):
                        new_version_path = f"{scene_path_name}/{scene_file_name[:-3]}_00.ma"
                        delete_unknown_nodes()
                        cmds.file(rename=new_version_path)
                        cmds.file(save=True, force=True, type='mayaAscii')

                        # Re-assign variables
                        scene_full_name = cmds.file(q=True, sceneName=True)
                        scene_file_name = os.path.basename(scene_full_name)
                        scene_path_name = os.path.dirname(scene_full_name)
                        return

            if 'anim' in scene_full_name:
                if len(sceme_file_name[:-3]) != naming_anim_sample:
                    if not scene_file_name[:-3].endswith('_00'):
                        new_version_path = f"{scene_path_name}/{scene_file_name[:-3]}_00.ma"
                        delete_unknown_nodes()
                        cmds.file(rename=new_version_path)
                        cmds.file(save=True, force=True, type='mayaAscii')

                        # Re-assign variables
                        scene_full_name = cmds.file(q=True, sceneName=True)
                        scene_file_name = os.path.basename(scene_full_name)
                        scene_path_name = os.path.dirname(scene_full_name)
                        return

            if 'shading' in scene_full_name:
                if len(scene_file_name[:-3]) != naming_lighting_sample:
                    if not scene_file_name[:-3].endswith('_00'):
                        new_version_path = f"{scene_path_name}/{scene_file_name[:-3]}_00.ma"
                        delete_unknown_nodes()
                        cmds.file(rename=new_version_path)
                        cmds.file(save=True, force=True, type='mayaAscii')

                        # Re-assign variables
                        scene_full_name = cmds.file(q=True, sceneName=True)
                        scene_file_name = os.path.basename(scene_full_name)
                        scene_path_name = os.path.dirname(scene_full_name)
                        return

        elif warning_msg_clicked == warning_msg_decline_btn:
            return

    # Isolate the subversion integers
    scene_file_uc_index = scene_file_name.rfind('_')
    scene_file_sv = scene_file_name[scene_file_uc_index + 1:-3]
    scene_file_sv_first_str = scene_file_sv[0]
    scene_file_sv_second_str = scene_file_sv[1]

    # Subversions up
    if scene_file_sv_second_str != '9':
        scene_file_sv_second_int = int(scene_file_sv_second_str)
        scene_file_sv_second_int += 1
        scene_file_sv_new = f"{scene_file_sv_first_str}{str(scene_file_sv_second_int)}"

    elif scene_file_sv_second_str == '9':
        scene_file_sv_first_int = int(scene_file_sv_first_str)
        scene_file_sv_first_int += 1
        scene_file_sv_new = f"{str(scene_file_sv_first_int)}0"

    # Rebuild scene file string
    scene_file_name_sliced = scene_file_name[:scene_file_uc_index]
    scene_file_new_name = f"{scene_file_name_sliced}_{scene_file_sv_new}.ma"
    scene_path_new = f"{scene_path_name}/{scene_file_new_name}"

    # Checks if the new subversion already exists
    scene_sv_new_first_str = scene_file_sv_new[0]
    scene_sv_new_second_str = scene_file_sv_new[1]

    while os.path.exists(scene_path_new):
        scene_sv_new_first_str = scene_file_sv_new[0]
        scene_sv_new_second_str = scene_file_sv_new[1]

        if scene_sv_new_second_str != '9':
            scene_sv_new_second_int = int(scene_sv_new_second_str)
            scene_sv_new_second_int += 1
            scene_file_sv_new = f"{scene_sv_new_first_str}{str(scene_sv_new_second_int)}"

        elif scene_sv_new_second_str == '9':
            scene_sv_new_first_int = int(scene_sv_new_first_str)
            scene_sv_new_first_int += 1
            scene_file_sv_new = f"{str(scene_sv_new_first_int)}0"

        # Rebuild scene file string
        scene_file_name_sliced = scene_file_name[:scene_file_uc_index]
        scene_file_new_name = f"{scene_file_name_sliced}_{scene_file_sv_new}.ma"
        scene_path_new = f"{scene_path_name}/{scene_file_new_name}"

    # Save the scene with the new name
    cmds.file(save=True, force=True, type='mayaAscii')
    cmds.file(rename=scene_path_new)
    cmds.file(save=True, force=True, type='mayaAscii')

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_publish_scene():

    scene_full_name = cmds.file(q=True, sceneName=True)
    scene_file_name = os.path.basename(scene_full_name)
    scene_path_name = os.path.dirname(scene_full_name)

    scene_shot_folder = scene_path_name.rsplit('/', 1)[0]
    shot_number = os.path.basename(scene_shot_folder)
    shot_number_upper_case = shot_number.upper()

    published_shot_name = f"{scene_shot_folder}/{shot_number_upper_case}.ma"
    # files_in_current_shot_folder = list_files_in_dir(scene_shot_folder)
    files_in_current_shot_folder = mbr_util_list_directory_contents(scene_shot_folder, content_type='files')

    last_sep_index = published_shot_name.rfind('/')
    published_shot_name_sliced = published_shot_name[last_sep_index + 1:]

    # Save file copy
    if published_shot_name_sliced in files_in_current_shot_folder:
        publish_response = cmds.confirmDialog(
            m='WARNING: There is already a published shot, do you want to overwrite it?', b=['Yes', 'No', 'Exit'])

        if publish_response == 'Yes':
            # Publish shot
            cmds.file(rename=f"{scene_shot_folder}/{shot_number_upper_case}.ma")
            cmds.file(save=True)

            # Return to session
            cmds.file(rename=f"{scene_path_name}/{scene_file_name}")
            cmds.file(save=True)

            cmds.confirmDialog(m='Shot published successfully!')

        else:
            cmds.confirmDialog(m='Operation Cancelled')
            return

    else:
        # Publish shot
        cmds.file(rename=f"{scene_shot_folder}/{shot_number_upper_case}.ma")
        cmds.file(save=True)

        # Return to session
        cmds.file(rename=f"{scene_path_name}/{scene_file_name}")
        cmds.file(save=True)

        cmds.confirmDialog(m='Shot published successfully!')