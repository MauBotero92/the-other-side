# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

import platform
import string
import ctypes
import sys
import os
from pathlib import Path
import importlib

# -------------------------------------
#
#       Functions
#
# -------------------------------------

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

# -------------------------------------
#
#       Variables and Append
#
# -------------------------------------

tos_root_path = mbr_util_get_tos_root()
tos_scripts_path = f"{tos_root_path}/Production/Assets/Scripts/"
sys.path.append(tos_scripts_path)

# -------------------------------------
#
#       Execute
#
# -------------------------------------

import TOS_Pipeline.src.dcc.maya.layout.ui.windows.camera_framer_window as cf
importlib.reload(cf)
cf.run()