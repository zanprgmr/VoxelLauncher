import _tkinter
import pickle
import shlex
import tkinter.messagebox as messagebox
import os
from webbrowser import open as webopen
import ctypes
import logging

import customtkinter as ctk
import minecraft_launcher_lib as mc
import requests

import utils

shared_data = {"jvmArguments": None}
windows_instances = []


def apply_shared_data(key, value):
    shared_data[key] = value
    logging.info(f"{key} applied")


# Function that launches the desired window and adds its instance into
# an array, for it to be accessed universally
def launch_windows(window=0, version_drop=None):
    # 1 -> Settings window
    # 2 -> Installer window
    # 3 -> Utilities
    if window == 1:
        windows_instances.append(settings_window())
    elif window == 2:
        windows_instances.append(installer_window())
    elif window == 3:
        windows_instances.append(utility_window(version_drop))


def settings_window():
    # Gets the JVM arguments, and saves them into the settings file
    def split_args_and_send(key, value):
        f_value = shlex.split(value)
        apply_shared_data(key, f_value)
        sett_window.destroy()

    sett_window = ctk.CTkToplevel()
    sett_window.title("Settings")
    sett_window.geometry("200x100")
    sett_window.lift()
    sett_window.attributes('-topmost', True)
    sett_window.after_idle(sett_window.attributes, '-topmost', False)

    theme_label = ctk.CTkLabel(sett_window, text="Java arguments:")
    theme_label.grid(row=0, column=0, padx=(30, 0))

    jvm_args = ctk.CTkEntry(sett_window, placeholder_text="Enter jvm arguments")
    jvm_args.grid(row=1, column=0, padx=(30, 0))

    # Updates the label if arguments are in the config file
    if shared_data["jvmArguments"]:
        jvm_args.insert(0, shared_data["jvmArguments"])

    apply_bt = ctk.CTkButton(sett_window, text="Apply",
                             command=lambda: split_args_and_send("jvmArguments", jvm_args.get()))
    apply_bt.grid(row=2, column=0, padx=(30, 0), pady=(5, 0))

    return sett_window


def installer_window():
    # Updates the version label whenever "Show snapshots" is pressed
    def update_versions():
        show_snapshots = snap_check.get()
        logging.info("Updating versions available")
        installer_drop.configure(values=utils.MinecraftLauncher.return_downloadable_versions(show_snapshots))

    def install_version():
        def install_and_notify():
            if fabric_check.get() == 0 and forge_check.get() == 0:
                mc.install.install_minecraft_version(installer_drop.get(), utils.MinecraftLauncher.get_dir())
                messagebox.showinfo("Installation Complete", f"Minecraft {installer_drop.get()}"
                                                             f" has been installed successfully!")
            # Install fabric
            elif fabric_check.get() == 1 and forge_check.get() == 0:
                try:
                    mc.fabric.install_fabric(installer_drop.get(), utils.MinecraftLauncher.get_dir())
                    messagebox.showinfo("Installation Complete", f"Minecraft {installer_drop.get()}"
                                                                 f" fabric has been installed successfully!")
                except Exception as e:
                    messagebox.showinfo("Error", f"Minecraft {installer_drop.get()}"
                                                 f" Fabric could not be installed: {e}")
            # Install forge
            elif fabric_check.get() == 0 and forge_check.get() == 1:
                forge_ver = mc.forge.find_forge_version(installer_drop.get())
                if not forge_ver:
                    messagebox.showinfo("No forge version", f"Minecraft {installer_drop.get()}"
                                                            f" is not compatible with Forge")
                else:
                    mc.forge.install_forge_version(forge_ver, utils.MinecraftLauncher.get_dir())
                    messagebox.showinfo("Installation Complete", f"Minecraft {installer_drop.get()}"
                                                                 f" forge has been installed successfully!")
            elif fabric_check.get() == 1 and forge_check.get() == 1:
                fabric_check.deselect()
                forge_check.deselect()
            logging.info("Installed selected version")
            update_versions()


        utils.ThreadingUtils.run_in_thread(install_and_notify)

    inst_window = ctk.CTkToplevel()
    inst_window.title("Installation window")
    inst_window.geometry("200x164")
    inst_window.lift()
    inst_window.attributes('-topmost', True)
    inst_window.after_idle(inst_window.attributes, '-topmost', False)

    snap_check = ctk.CTkCheckBox(inst_window, text="Show Snapshots", command=update_versions)
    snap_check.grid(row=1, column=0, padx=(35, 0), sticky="w")

    fabric_check = ctk.CTkCheckBox(inst_window, text="Install Fabric")
    fabric_check.grid(row=2, column=0, pady=(4, 0), padx=(35, 0), sticky="w")

    forge_check = ctk.CTkCheckBox(inst_window, text="Install Forge")
    forge_check.grid(row=3, column=0, pady=(4, 0), padx=(35, 0), sticky="w")

    installer_drop = ctk.CTkComboBox(inst_window,
                                     values=utils.MinecraftLauncher.return_downloadable_versions(snap_check.get()))
    installer_drop.grid(row=0, column=0, padx=25, pady=8)

    install_ver_bt = ctk.CTkButton(inst_window, text="Install Version", command=install_version)
    install_ver_bt.grid(row=4, column=0, pady=6)

    return inst_window


def utility_window(version_drop):
    utility_win = ctk.CTkToplevel()
    utility_win.title("Utilities")
    utility_win.geometry("200x200")
    utility_win.attributes('-topmost', True)
    utility_win.after_idle(utility_win.attributes, '-topmost', False)
    utility_win.after(50, utility_win.lift)

    backup_bt = ctk.CTkButton(utility_win, text="Backup worlds into desktop", width=190,
                              command=utils.MinecraftLauncher.backup_worlds)
    backup_bt.grid(row=0, column=0, pady=(10, 0), padx=(5, 0))

    repair_ver_btn = ctk.CTkButton(utility_win, text="Repair version", width=190,
                                   command=lambda: utils.MinecraftLauncher.repair_version(version_drop))
    repair_ver_btn.grid(row=1, column=0, padx=(5, 0), pady=(5, 0))

    cfg_label = ctk.CTkLabel(utility_win, text="Manage minecraft configuration")
    cfg_label.grid(row=2, column=0, pady=(10, 0))

    export_cfg_bt = ctk.CTkButton(utility_win, text="Export", width=95,
                                  command=utils.MinecraftLauncher.export_mc_config)
    export_cfg_bt.grid(row=3, column=0, padx=(5, 0), sticky="w")
    import_cfg_bt = ctk.CTkButton(utility_win, text="Import", width=95,
                                  command=utils.MinecraftLauncher.import_mc_config)
    import_cfg_bt.grid(row=3, column=0, sticky="e")

    install_mr_bt = ctk.CTkButton(utility_win, text="Install .mrpack", width=190,
                                  command=utils.MinecraftLauncher.install_mrpack)
    install_mr_bt.grid(row=4, column=0, pady=(15, 0), padx=(5, 0))
    return utility_win


# Function that parses the news data from the api and adds it to the frame on the main window
def append_news(news_frame, news_data):
    def open_article(url):
        webopen(url)

    # Index means the number of news shown
    # Changing it to a number greater than 30 may cause the launcher to be slower
    for index, news in enumerate(news_data["entries"]):
        if index >= 20:
            break
        title = news["title"]
        subtitle = news["text"]
        article_url = news["readMoreLink"]

        title_label = ctk.CTkLabel(news_frame, text=title, font=("Arial", 16, "bold"), wraplength=320)
        title_label.pack()

        subtitle_label = ctk.CTkLabel(news_frame, text=subtitle, font=("Arial", 12), wraplength=380)
        subtitle_label.pack()

        read_more_button = ctk.CTkButton(news_frame, text="Read More",
                                         command=lambda url=article_url: open_article(url))
        read_more_button.pack()

        spacer = ctk.CTkLabel(news_frame, text="", height=20)
        spacer.pack()


def main_window():

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    config_file = utils.FileManagement.get_config_dir()
    utils.FileManagement.create_file_if_not_exists(config_file)

    ctk.set_default_color_theme("green")
    ctk.set_appearance_mode("dark")

    app = ctk.CTk()
    app.title("VoxelLauncher")
    app.geometry("610x300")

    # Icons (Window and Taskbar)
    appid = "zanprgmr.VoxelLauncher.Launcher.app"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    try:
        app.iconbitmap("assets/pris-marine.ico")

    except FileNotFoundError:
        app.iconbitmap(utils.FileManagement.pyinstaller_find("pris-marine.ico"))
    except _tkinter.TclError:
        pass  # Unknown error that may pop on the .exe bundle



    app.resizable(False, False)
    app.grid_rowconfigure(0, weight=1)


    folder_img = utils.FileManagement.load_asset("folder.png")
    gear_img = utils.FileManagement.load_asset("gear.png")
    light_img = utils.FileManagement.load_asset("light.png")

    logging.info("Assets and properties loaded")

    launch_bt = ctk.CTkButton(app, text="Launch",
                              command=lambda: utils.MinecraftLauncher.execute_mc(app, name_tx, version_drop,
                                                                                 shared_data, config_file,
                                                                                 windows_instances),
                              width=200,
                              height=60, font=(None, 20))
    launch_bt.grid(row=0, column=0, pady=(10, 0), padx=(10, 0))

    version_drop = ctk.CTkComboBox(app, values=utils.MinecraftLauncher.return_installed_versions(), width=200)
    version_drop.grid(row=1, column=0, padx=(10, 0), pady=(10, 0))

    name_tx = ctk.CTkEntry(app, placeholder_text="Username", width=120)
    name_tx.grid(row=2, column=0, sticky="w", padx=(10, 0), pady=(120, 0))

    sett_window_bt = ctk.CTkButton(app, text="", image=ctk.CTkImage(gear_img),
                                   command=lambda: launch_windows(1), width=35)
    sett_window_bt.grid(row=2, column=0, pady=(120, 0), padx=(95, 0))

    open_dir_bt = ctk.CTkButton(app, text="", image=ctk.CTkImage(folder_img), width=35,
                                command=lambda: os.startfile(utils.MinecraftLauncher.get_dir()))
    open_dir_bt.grid(row=2, column=0, sticky="e", pady=(120, 0))

    install_win_bt = ctk.CTkButton(app, text="Installations window", command=lambda: launch_windows(2), width=160)
    install_win_bt.grid(row=3, column=0, padx=(10, 0), pady=(10, 10), sticky="w")

    utility_win_bt = ctk.CTkButton(app, text="", image=ctk.CTkImage(light_img), width=35,
                                   command=lambda: launch_windows(3, version_drop))
    utility_win_bt.grid(row=3, column=0, sticky="w", padx=(174, 0))

    scrollable_frame = ctk.CTkScrollableFrame(app, width=360)
    scrollable_frame.grid(row=0, column=2, rowspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

    logging.info("Graphic elements loaded")

    try:

        news_data = requests.get("https://launchercontent.mojang.com/news.json").json()
        # 0.10s faster but may cause errors if the window is closed too early (Testing)
        # threading.Thread(target=lambda:  append_news(scrollable_frame, news_data)).start()
        append_news(scrollable_frame, news_data)
        logging.info("News loaded")

    except requests.RequestException as e:
        def offline_msg():
            messagebox.showwarning("No internet", f"Could not connect to the internet: {e}")
            utils.ThreadingUtils.run_in_thread(offline_msg)
            logging.info("No internet")

    try:
        with open(config_file, "rb") as config_read:
            config = pickle.load(config_read)
            name_tx.insert(0, config[0])
            version_drop.set(config[1])
            if config[2]:
                shared_data.update(config[2])
        logging.info("Config loaded")
    except (TypeError, EOFError, FileNotFoundError) as e:
        logging.error(f"Config NOT LOADED, error: {e}")
        pass

    return app


if __name__ == "__main__":
    main_window().mainloop()
