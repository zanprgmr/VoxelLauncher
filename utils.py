import tkinter.filedialog
import minecraft_launcher_lib as mc


def get_dir(custom_dir=False):
    if custom_dir:
        dir = tkinter.filedialog.askdirectory()
    else:
        dir = mc.utils.get_minecraft_directory()

    return dir


def return_downloadable_versions(show_snapshots=False):
    ver_list = []
    if show_snapshots:
        for ver in mc.utils.get_version_list():
            ver_list.append(ver["id"])
    else:
        for ver in mc.utils.get_version_list():
            if ver["type"] == "release":
                ver_list.append(ver["id"])

    return ver_list


# TODO: implement the possibility to use a custom directory
# Maybe use a constant
def return_installed_versions():
    ver_list = []
    for ver in mc.utils.get_installed_versions(get_dir()):
        ver_list.append(ver["id"])

    return ver_list


