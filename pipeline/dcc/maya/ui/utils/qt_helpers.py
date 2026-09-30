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
]

# -------------------------------------------
#
#       Functions
#
# -------------------------------------------

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_helper_block_signals(user_list):

    for widget in user_list:
        widget.blockSignals(True)

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_helper_unlock_signals(user_list):

    for widget in user_list:
        widget.blockSignals(False)

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_helper_set_enabled(user_list):

    for widget in user_list:
        widget.setEnabled(True)

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_helper_set_disabled(user_list):

    for widget in user_list:
        widget.setEnabled(False)

'''
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_helper_clear_combos(user_list):

    for widget in user_list:
        widget.clear()