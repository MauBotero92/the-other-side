import os

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
PURPOSE:
PROCEDURE:
ASSUMPTIONS:
'''
def mbr_util_find_file(filename, root_path):

    for dirpath, _, filenames in os.walk(root_path):
        if filename in filenames:
            return os.path.join(dirpath, filename)

    return None