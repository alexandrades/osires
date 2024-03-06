import os
from plyer import filechooser

def choosefile(filters):
    cwd = os.getcwd()
    file_path = filechooser.open_file(filters=filters)
    os.chdir(cwd)

    return file_path