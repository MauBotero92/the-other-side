'''
PURPOSE:        Copy (mirror) the pipeline scripts from the local dev folder to the
                production P: drive, without ever letting git or pip touch P: directly.
PROCEDURE:      > Define the source (dev, e.g. F:) and destination (production, e.g. P:) paths
                > Call Windows' robocopy in mirror mode, excluding .git, .venv, and cache folders
                > Print a simple success/failure summary
ASSUMPTIONS:    Running on Windows, in a PyCharm Run Configuration or terminal with access to
                both the source and destination paths.
'''

import subprocess
import sys

# -------------------------------------
#
#       Configuration - edit these two paths for your setup
#
# -------------------------------------

SOURCE_DIR = r"F:/10_maya_projects/MBR INC/assets/py/TOS_Pipeline/src"
DEST_DIR = r"P:/The Other Side/Production/Assets/Scripts/TOS_Pipeline/src"

# Folders to exclude from the copy - add more names here if needed
EXCLUDE_DIRS = [".venv", ".git", "__pycache__", ".idea"]

# Files to exclude from the copy
EXCLUDE_FILES = ["*.pyc"]

'''
PURPOSE:        Mirror source_dir into dest_dir using robocopy, skipping dev-only folders
PROCEDURE:      > Build the robocopy command with /MIR and the exclusion lists
                > Run it and capture the exit code
                > Report success or failure based on robocopy's exit code conventions
ASSUMPTIONS:    robocopy is available (built into Windows by default)
'''

def publish_to_production(source_dir=SOURCE_DIR, dest_dir=DEST_DIR):

    cmd = [
        "robocopy",
        source_dir,
        dest_dir,
        "/MIR",  # mirror: copy new/changed files, remove files deleted from source
        "/XD", *EXCLUDE_DIRS,  # exclude these directories anywhere in the tree
        "/XF", *EXCLUDE_FILES,  # exclude these file patterns
        "/R:2",  # retry twice on a locked/failed file
        "/W:2",  # wait 2 seconds between retries
    ]

    print(f"Publishing:\n  from: {source_dir}\n  to:   {dest_dir}\n")

    result = subprocess.run(cmd)

    # robocopy uses exit codes 0-7 as "success" (with varying detail), 8+ means real errors
    if result.returncode < 8:
        print("\nPublish complete.")
        return True
    else:
        print(f"\nPublish failed. Robocopy exit code: {result.returncode}")
        return False


if __name__ == "__main__":
    success = publish_to_production()
    sys.exit(0 if success else 1)