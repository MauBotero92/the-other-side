# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import os
import platform
import ctypes
import string
import maya.cmds as cmds

# -------------------------------------------
#
#       Export Config
#
# -------------------------------------------

__all__ = [
    'mbr_util_list_directory_contents',
    'mbr_util_sorted_folders_list',
    'mbr_util_filtered_file_list',
    'mbr_util_find_file',
    'mbr_util_get_drive_label',
    'mbr_util_get_tos_root',
    'mbr_util_get_tos_path',
]

# -------------------------------------------
#
#       File System Functions
#
# -------------------------------------------

'''
PURPOSE:        Return a list of folders or files in a given directory
PROCEDURE:      > List all entries in the directory
                > Filter by whether each entry is a folder or a file, based on content_type
ASSUMPTIONS:    content_type is either 'folders' or 'files'
'''
def mbr_util_list_directory_contents(directory, content_type='folders'):

    entries = os.listdir(directory)

    if content_type == 'folders':
        return [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]

    elif content_type == 'files':
        return [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]

    else:
        raise ValueError(f"content_type must be either 'folders' or 'files', got '{content_type}'")

'''
PURPOSE:     Return a list of sorted folders in a given directory   
PROCEDURE:      
                
ASSUMPTIONS:    
'''
def mbr_util_sorted_folders_list(directory):

    function_list = mbr_util_list_directory_contents(directory, content_type='folders')
    dirs_filtered = [x for x in function_list if not x.startswith('.')]
    dirs_sorted = sorted(dirs_filtered, key=lambda x: x.replace('_', ' ').lower())

    return dirs_sorted

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_filtered_file_list(directory):

    files = mbr_util_list_directory_contents(directory, content_type='files')
    files_filtered = []

    for file in files:
        if file.endswith(('.mb', '.ma')):
            files_filtered.append(file)

    return files_filtered

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_find_file(filename, root_path):

    for dirpath, _, filenames in os.walk(root_path):
        if filename in filenames:
            return os.path.join(dirpath, filename)

    return None

'''
PURPOSE:        Gets the drive letter 
PROCEDURE:      > Allocate two empty buffers. One receiving the volume label, the other one the filesystem name
                > Gets the volume information and store it in a variable rc
ASSUMPTIONS:
'''
def mbr_util_get_drive_label(drive):

    volume_name_buffer = ctypes.create_unicode_buffer(1024)
    fs_name_buffer = ctypes.create_unicode_buffer(1024)

    rc = ctypes.windll.kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(drive),
        volume_name_buffer,
        ctypes.sizeof(volume_name_buffer),
        None,
        None,
        None,
        fs_name_buffer,
        ctypes.sizeof(fs_name_buffer)
    )

    if rc:
        return volume_name_buffer.value
    return ""

'''
PURPOSE:        Gets the root path for pCloud on the system
PROCEDURE:      > Gets the platform and stores it in a variable
                > Runs the platform logic to get the pCloud root depending if it is Windows, Mac, or Linux
ASSUMPTIONS:    There is no Linux machine on the team. Is either Windows or Mac
'''
def mbr_util_get_tos_root():

    system = platform.system()

    if system == 'Windows':
        drives = []

        for letter in string.ascii_uppercase:
            drive = f"{letter}:/"
            if os.path.exists(drive):
                label = mbr_util_get_drive_label(drive)
                drives.append(f"{drive}{label}")

        for drive in drives:
            if 'pCloud Drive' in drive:
                drive_letter = drive[:3]
            else:
                pass

        return f"{drive_letter}The Other Side"

    else:
        home = Path.home()

        return Path(f"{home}/pCloud Drive/The Other Side")

'''
PURPOSE:        Get TOS workspace path
PROCEDURE:      > Store the drive letter and the workspace in separate variables
                > If 'The Other Side' is in the current workspace, rebuild the string to match the system.
ASSUMPTIONS:    None
'''
def mbr_util_get_tos_path():

    # Stores the drive letter and the workspace
    tos_root = mbr_util_get_tos_root()
    drive = tos_root[:2]
    cur_wks = cmds.workspace(q=True, rd=True)

    # If The Other Side is in the current workspace, changes the drive letter and rebuilds the workspace string
    if 'The Other Side' in cur_wks:
        cur_wks_rel = cur_wks[2:]
        cur_wks_concat = f"{drive}{cur_wks_rel}"
        return cur_wks_concat
    else:
        return None