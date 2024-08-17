import tkinter.filedialog
import minecraft_launcher_lib as mc
from os.path import exists
from pickle import dump
from subprocess import run
from tkinter import messagebox


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


def return_installed_versions():
    ver_list = []
    for ver in mc.utils.get_installed_versions(get_dir()):
        ver_list.append(ver["id"])

    return ver_list


def create_file_if_not_exists(filename):
    if not exists(filename):
        try:
            with open(filename, 'x') as file:
                pass
        except FileExistsError:
            pass


def save_config(config_file, name, version, shared_data):
    with open(config_file, "wb") as config_read:
        dump([name.get(), version.get(), shared_data], config_read)



def execute_mc(app, name_tx, version_drop, inst_window, sett_window, shared_data, config_file):

    options = {
    "username": name_tx.get(),
    "uuid": "59ac9ba1-2c3c-4c99-b7ba-7258525068b4",
    "token": "token",
    "jvmArguments": shared_data["jvmArguments"],
    "launcherName": "Voxel Launcher",
    "launcherVersion": "1.2"
}

    if name_tx.get() == "":
        messagebox.showwarning("Error", "Please enter your Minecraft name.")
        name_tx.focus_force()
    else:
        save_config(config_file, name_tx, version_drop, shared_data)
        minecraft_command = mc.command.get_minecraft_command(version_drop.get(), get_dir(), options)
        if "inst_window" in globals() and inst_window.winfo_exists():
            inst_window.withdraw()
        if "sett_window" in globals() and sett_window.winfo_exists():
            sett_window.withdraw()
        app.withdraw()
        extract_path = f"get_dir()/versions/{version_drop.get()}/natives"
        mc.natives.extract_natives(version_drop.get(), get_dir(), extract_path)
        run(minecraft_command)
        if "inst_window" in globals() and inst_window.winfo_exists():
            inst_window.deiconify()
        if "sett_window" in globals() and sett_window.winfo_exists():
            sett_window.deiconify()
        app.deiconify()
