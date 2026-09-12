import maya.cmds as cmds

version = cmds.about(version=True)

if version in ('2023', '2024'):
    from PySide2 import QtWidgets as wdg
    from PySide2 import QtCore as core
    from PySide2 import QtGui as gui
    from shiboken2 import wrapInstance
elif version in ('2025', '2026'):
    from PySide6 import QtWidgets as wdg
    from PySide6 import QtCore as core
    from PySide6 import QtGui as gui
    from shiboken6 import wrapInstance
else:
    raise RunTimeError(f"Unsupported Maya version for Qt compatibility: {version}")