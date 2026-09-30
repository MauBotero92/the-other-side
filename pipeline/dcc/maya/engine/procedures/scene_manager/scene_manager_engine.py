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
    'mbr_egn_clean_initial_idx',
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
def mbr_egn_clean_initial_idx(obj, flag_name, combo, user_list):

    if not getattr(obj, flag_name):
        return
    setattr(obj, flag_name, False)

    current_index = combo.currentIndex()

    user_list.pop(0)

    combo.blockSignals(True)
    combo.clear()
    combo.addItems(user_list)

    if current_index > 0:
        combo.setCurrentIndex(current_index - 1)

    combo.blockSignals(False)