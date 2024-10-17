import _tkinter
import os
import platform
import shutil
import sys
import tkinter.filedialog
from os.path import exists
from pathlib import Path
from pickle import dump
from subprocess import run
import tkinter.simpledialog
import minecraft_launcher_lib as mc
import tkinter
from tkinter import messagebox
from threading import Thread
from PIL import Image
from typing import List
import logging


logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


class FileManagement:
    @staticmethod
    def pyinstaller_find(relative_path: str) -> str:
        # Helper to find a file in a PyInstaller bundle
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @staticmethod
    def get_config_dir() -> str:
        # Return the directory where configuration files are stored based on OS
        if platform.system() == 'Windows':
            appdata_path = os.path.join(os.getenv('APPDATA'), 'VoxelLauncher')
        elif platform.system() == 'Darwin':  # macOS
            appdata_path = os.path.join(os.getenv('HOME'), 'Library', 'Application Support', 'VoxelLauncher')
        else:
            appdata_path = os.path.join(os.getenv('HOME'), '.config', 'VoxelLauncher')
        os.makedirs(appdata_path, exist_ok=True)

        return os.path.join(appdata_path, "config.pickle")

    @staticmethod
    def create_file_if_not_exists(filename: str):
        # Create a file if it doesn't already exist
        if not exists(filename):
            logging.info(f"File created at {filename}")
            Path(filename).touch()

    @staticmethod
    def save_config(config_file: str, name: tkinter.StringVar, version: tkinter.StringVar, shared_data: dict):
        # Save user configuration using pickle
        with open(config_file, "wb") as config_read:
            dump([name.get(), version.get(), shared_data], config_read)
        logging.info("Config saved")

    @staticmethod
    def load_asset(file_name):
        try:
            return Image.open(f"assets/{file_name}")
        except FileNotFoundError:
            return Image.open(FileManagement.pyinstaller_find(file_name))


class MinecraftLauncher:
    @staticmethod
    def get_dir(custom_dir: bool = False) -> str:
        # Get Minecraft directory or prompt user for a custom directory
        return tkinter.filedialog.askdirectory() if custom_dir else mc.utils.get_minecraft_directory()

    @staticmethod
    def execute_mc(app: tkinter.Tk, name_tx, version_drop,
                   shared_data: dict, config_file: str, windows: List[tkinter.Toplevel]):
        # Execute Minecraft with user settings
        logging.info("Executing minecraft")
        if not name_tx.get():
            messagebox.showwarning("Error", "Please enter your Minecraft name.")
            name_tx.focus_force()
            return

        options = {
            "username": name_tx.get(),
            "uuid": "59ac9ba1-2c3c-4c99-b7ba-7258525068b4",
            "token": "token",
            "jvmArguments": shared_data["jvmArguments"],
            "launcherName": "Voxel Launcher",
            "launcherVersion": "1.3"
        }

        FileManagement.save_config(config_file, name_tx, version_drop, shared_data)
        minecraft_command = mc.command.get_minecraft_command(version_drop.get(), MinecraftLauncher.get_dir(), options)

        # Hide all windows
        app.withdraw()
        for window in windows:
            try:
                window.withdraw()
            except _tkinter.TclError:
                pass
        logging.info("Windows hidden")


        logging.info("Mc command executed")
        # Run Minecraft
        run(minecraft_command)

        # Restore windows
        app.deiconify()
        for window in windows:
            try:
                window.deiconify()
            except _tkinter.TclError:
                pass
        logging.info("Windows restored")


    @staticmethod
    def return_downloadable_versions(show_snapshots):
        # Return a list of available Minecraft versions, optionally including snapshots
        versions = mc.utils.get_version_list()
        return [ver["id"] for ver in versions if show_snapshots or ver["type"] == "release"]


    @staticmethod
    def return_installed_versions() -> List[str]:
        # Return a list of installed Minecraft versions
        versions = mc.utils.get_installed_versions(MinecraftLauncher.get_dir())
        return [ver["id"] for ver in versions]


    @staticmethod
    def repair_version(version_drop: tkinter.StringVar):
        # Repair selected Minecraft version

        def repair_logic():
            mc.install.install_minecraft_version(version_drop.get(), MinecraftLauncher.get_dir())
            messagebox.showinfo("Version repaired", f"Version {version_drop.get()} has been repaired successfully")

        logging.info(f"Starting version repairing, ver: {version_drop.get()}")
        ThreadingUtils.run_in_thread(repair_logic)



    @staticmethod
    def backup_worlds():
        # Backup Minecraft worlds

        def backup_funct():
            messagebox.showinfo("Important",
                                "This process can take from 1-10 min depending on your worlds and their file size")
            home_dir = Path.home()
            worlds_dir = os.path.join(MinecraftLauncher.get_dir(), "saves")
            zip_file = home_dir / "Desktop" / "minecraft_worlds_backup.zip"
            logging.info("Starting world backup")
            shutil.make_archive(str(zip_file).replace('.zip', ''), 'zip', worlds_dir)
            messagebox.showinfo("Completed", f"Worlds backed up at {zip_file}")
            logging.info("World backup finished")

        ThreadingUtils.run_in_thread(backup_funct)

    @staticmethod
    def export_mc_config():
        # Export Minecraft configuration to the desktop
        desktop_path = Path.home() / "Desktop"
        shutil.copy2(os.path.join(MinecraftLauncher.get_dir(), "options.txt"), desktop_path)
        messagebox.showinfo("Configuration saved", f"Saved at {desktop_path}")

    @staticmethod
    def import_mc_config():
        # Import Minecraft configuration from a file
        src_file = tkinter.filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        shutil.copy2(src_file, os.path.join(MinecraftLauncher.get_dir(), "options.txt"))
        messagebox.showinfo("Done", "Configuration imported successfully")

    @staticmethod
    def install_mrpack():
        # Install a .mrpack modpack

        def install_mrpack_funct():
            if modpack_directory:
                mc.mrpack.install_mrpack(pack_dir, MinecraftLauncher.get_dir(), modpack_directory=modpack_directory)
            else:
                mc.mrpack.install_mrpack(pack_dir, MinecraftLauncher.get_dir())

            mrpack_info = mc.mrpack.get_mrpack_information(pack_dir)
            tkinter.Tk().after(0, lambda: messagebox.showinfo(f"{mrpack_info['name']} installed",
                                                              f"Successfully installed: {mrpack_info['name']}\n"
                                                              f"Minecraft Version: {mrpack_info['minecraftVersion']}"))

        pack_dir = tkinter.filedialog.askopenfilename(filetypes=[("Modpack file", "*.mrpack")])

        if not pack_dir:
            messagebox.showwarning("No File Selected", "No modpack file was selected.")
            return

        modpack_directory = tkinter.filedialog.askdirectory() if messagebox.askyesno("Install Location",
                                                                                     "Do you want to install the modpack into a specific directory?") else None

        ThreadingUtils.run_in_thread(install_mrpack_funct)


class ThreadingUtils:
    @staticmethod
    def run_in_thread(func):
        logging.info(f"Threading function: {func}")
        thread = Thread(target=func)
        thread.start()
