# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

from TOS_Pipeline.src.core.fs_utils import *
from TOS_Pipeline.src.dcc.maya.utils.qt_helpers import *

# -------------------------------------------
#
#       Export Config
#
# -------------------------------------------

__all__ = [
    'mbr_egn_fill_first_combo',
    'mbr_egn_combo_changed',
]

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_fill_first_combo(path, combo):

    lvl_01_folder_list = ['-'] + mbr_util_list_directory_contents(path, content_type='folders')
    combo.blockSignals(True)
    combo.addItems(lvl_01_folder_list)
    combo.blockSignals(False)

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_egn_combo_changed(combos_list, lvl_text, lvl_dir, lvl_value, file_widget):

    if lvl_value != 5:
        # Preventing unwanted changes on combo boxes
        mbr_helper_block_signals(combos_list[lvl_value:])

        # Clear Combos and List
        mbr_helper_clear_combos(combos_list[lvl_value:])
        file_widget.clear()

        # Guard check if user picks '-'
        if lvl_text == '-':
            mbr_helper_set_disabled(combos_list[lvl_value:])
            mbr_helper_unlock_signals(combos_list[lvl_value:])
            return

        # Adding folders on the next combox box
        lvl_dirs_sorted = mbr_util_sorted_folders_list(lvl_dir)

        if len(lvl_dirs_sorted) > 0:
            mbr_helper_fill_next_combo(lvl_dirs_sorted, combos_list[lvl_value])
            mbr_helper_set_disabled(combos_list[lvl_value+1:])

        # Adding files on the file list
        lvl_files_filtered = mbr_util_filtered_file_list(lvl_dir)
        mbr_helper_fill_file_list(lvl_files_filtered, file_widget)

        # Reactivating signals on combo boxes
        mbr_helper_unlock_signals(combos_list[lvl_value:])

    elif lvl_value == 5:
        # Preventing unwanted changes on combo boxes
        mbr_helper_block_signals(combos_list[lvl_value:])

        # Clear List
        file_widget.clear()

        # Guard check if user picks '-'
        if lvl_text == '-':
            mbr_helper_set_disabled(combos_list[lvl_value:])
            mbr_helper_unlock_signals(combos_list[lvl_value:])
            return

        # Adding files on the file list
        lvl_files_filtered = mbr_util_filtered_file_list(lvl_dir)
        mbr_helper_fill_file_list(lvl_files_filtered, file_widget)

        # Reactivating signals on combo boxes
        mbr_helper_unlock_signals(combos_list[lvl_value:])