# -------------------------------------
#
#       Import Modules
#
# -------------------------------------

pass

# -------------------------------------------
#
#       Export Config
#
# -------------------------------------------

__all__ = [
    'mbr_helper_block_signals',
    'mbr_helper_unlock_signals',
    'mbr_helper_set_enabled',
    'mbr_helper_set_enabled',
    'mbr_helper_set_disabled',
    'mbr_helper_clear_combos',
    'mbr_helper_fill_next_combo',
    'mbr_helper_fill_file_list',
]

# -------------------------------------------
#
#       Functions
#
# -------------------------------------------

'''
PURPOSE:        Simplify the blockSignals command in Qt
PROCEDURE:      > Loop through the user list and apply the blockSignals command
ASSUMPTIONS:    None
'''
def mbr_helper_block_signals(user_list):

    for widget in user_list:
        widget.blockSignals(True)

'''
PURPOSE:        Simplify the unlockSignals command in Qt
PROCEDURE:      > Loop through the user list and apply the unlockSignals command
ASSUMPTIONS:    None
'''
def mbr_helper_unlock_signals(user_list):

    for widget in user_list:
        widget.blockSignals(False)

'''
PURPOSE:        Simplify the setEnabled command in Qt
PROCEDURE:      > Loop through the user list and apply the setEnabled command
ASSUMPTIONS:    None
'''
def mbr_helper_set_enabled(user_list):

    for widget in user_list:
        widget.setEnabled(True)

'''
PURPOSE:        Simplify the setDisabled command in Qt
PROCEDURE:      Loop through the user list and apply the setDisabled command
ASSUMPTIONS:    None
'''
def mbr_helper_set_disabled(user_list):

    for widget in user_list:
        widget.setEnabled(False)

'''
PURPOSE:        Simplify the clear command in Qt
PROCEDURE:      Loop through the user list and apply the clear command
ASSUMPTIONS:    None
'''
def mbr_helper_clear_combos(user_list):

    for widget in user_list:
        widget.clear()

'''
PURPOSE:        Fill a combo box with a default value and an user list 
PROCEDURE:      > Add the '-' character as a default first item in the combo box the user set
                > Add the user list to the combo box
                > Enable the combo box
ASSUMPTIONS:    None
'''
def mbr_helper_fill_next_combo(user_list, combo):

    combo.addItem('-')
    combo.addItems(user_list)

    # Settings Defaults
    combo.setEnabled(True)

'''
PURPOSE:        Fill a file widget with an user list
PROCEDURE:      > If the user list is empty, disable the list widget. Else, enable the list widget and add the user list
                items to the list widget 
ASSUMPTIONS:    None
'''
def mbr_helper_fill_file_list(files_list, file_widget):

    if len(files_list) == 0:
        file_widget.setEnabled(False)
    else:
        file_widget.setEnabled(True)
        file_widget.addItems(files_list)

