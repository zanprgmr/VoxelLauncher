from webbrowser import open as webopen
from PIL import Image
import customtkinter as ctk
import utils
import minecraft_launcher_lib as mc
import tkinter.messagebox as messagebox
import threading
from os import startfile
import shlex
import pickle

config_file = "config.pickle"
shared_data = {"jvmArguments": None}


def apply_shared_data(key, value):
    shared_data[key] = value


def settings_window():
    def split_args_and_send(key, value):
        f_value = shlex.split(value)
        apply_shared_data(key, f_value)
        sett_window.destroy()

    sett_window = ctk.CTkToplevel()
    sett_window.title("Settings")
    sett_window.geometry("200x120")
    sett_window.lift()
    sett_window.attributes('-topmost', True)
    sett_window.after_idle(sett_window.attributes, '-topmost', False)

    theme_label = ctk.CTkLabel(sett_window, text="Java arguments:")
    theme_label.grid(row=0, column=0, padx=(10, 0))

    jvm_args = ctk.CTkEntry(sett_window, placeholder_text="Enter jvm arguments")
    jvm_args.grid(row=1, column=0, padx=(10, 0))

    if shared_data["jvmArguments"]:
        jvm_args.insert(0, shared_data["jvmArguments"])

    apply_bt = ctk.CTkButton(
        sett_window,
        text="Apply",
        command=lambda: split_args_and_send("jvmArguments", jvm_args.get())
    )
    apply_bt.grid(row=2, column=0, padx=(10, 0))

    return sett_window


def installer_window():

    def update_versions():
        show_snapshots = snap_check.get()
        installer_drop.configure(values=utils.return_downloadable_versions(show_snapshots))

    def install_version():
        def install_and_notify():
            if fabric_check.get() == 0 and forge_check.get() == 0:
                mc.install.install_minecraft_version(installer_drop.get(), utils.get_dir())
                messagebox.showinfo("Installation Complete", f"Minecraft {installer_drop.get()}"
                                                             f" has been installed successfully!")
            elif fabric_check.get() == 1 and forge_check.get() == 1:
               fabric_check.deselect()
               forge_check.deselect()
            elif fabric_check.get() == 1 and forge_check.get() == 0:
                try:
                    mc.fabric.install_fabric(installer_drop.get(), utils.get_dir())
                    messagebox.showinfo("Installation Complete", f"Minecraft {installer_drop.get()}"
                                                                 f" fabric has been installed successfully!")
                except Exception as e:
                    messagebox.showinfo("Error", f"Minecraft {installer_drop.get()}"
                                                                 f" Fabric could not be installed: {e}")
            elif fabric_check.get() == 0 and forge_check.get() == 1:
                forge_ver = mc.forge.find_forge_version(installer_drop.get())
                if not forge_ver:
                    messagebox.showinfo("No forge version", f"Minecraft {installer_drop.get()}"
                                                                 f" is not compatible with Forge")
                else:
                    mc.forge.install_forge_version(forge_ver, utils.get_dir())

        install_thread = threading.Thread(target=install_and_notify)
        install_thread.start()


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

    installer_drop = ctk.CTkComboBox(inst_window, values=utils.return_downloadable_versions(snap_check.get()))
    installer_drop.grid(row=0, column=0, padx=25, pady=8)

    install_ver_bt = ctk.CTkButton(inst_window, text="Install Version", command=install_version)
    install_ver_bt.grid(row=4, column=0, pady=6)

    return inst_window


def append_news(news_frame, news_data):

    def open_article(url):
        webopen(url)

    i = 0
    for news in news_data:
        i += 1
        title = news["default_tile"]["title"]
        subtitle = news["default_tile"]["sub_header"]
        image_url = "https://minecraft.net" + news["default_tile"]["image"]["imageURL"]
        article_url = "https://minecraft.net" + news["article_url"]

        title_label = ctk.CTkLabel(news_frame, text=title, font=("Arial", 16, "bold"))
        title_label.pack()

        subtitle_label = ctk.CTkLabel(news_frame, text=subtitle, font=("Arial", 12))
        subtitle_label.pack()

        read_more_button = ctk.CTkButton(news_frame, text="Read More", command=lambda url=article_url: open_article(url))
        read_more_button.pack()

        spacer = ctk.CTkLabel(news_frame, text="", height=20)
        spacer.pack()


def main_window():
    utils.create_file_if_not_exists(config_file)
    ctk.set_default_color_theme("green")
    ctk.set_appearance_mode("dark")

    app = ctk.CTk()
    app.title("VoxelLauncher")
    app.geometry("610x300")

    app.resizable(False, False)
    app.grid_rowconfigure(0, weight=1)


    launch_bt = ctk.CTkButton(app, text="Launch", command=lambda: utils.execute_mc(app, name_tx, version_drop, installer_window, settings_window, shared_data, config_file), width=200, height=60, font=(None, 20))
    launch_bt.grid(row=0, column=0, pady=(10, 0), padx=(10, 0))

    version_drop = ctk.CTkComboBox(app, values=utils.return_installed_versions(), width=200)
    version_drop.grid(row=1, column=0, padx=(10, 0), pady=(10, 0))

    name_tx = ctk.CTkEntry(app, placeholder_text="Username", width=120)
    name_tx.grid(row=2, column=0, sticky="w",padx=(10, 0), pady=(120, 0))




    try:
        folder_img = Image.open("./images/folder.png")
    # Added for compatibility with PyInstaller
    except FileNotFoundError:
        folder_img = Image.open("folder.png")

    try:
        gear_img = Image.open("./images/gear.png")
    # Added for compatibility with PyInstaller
    except FileNotFoundError:
        gear_img = Image.open("gear.png")

    sett_window_button = ctk.CTkButton(app, text="", image=ctk.CTkImage(gear_img), command=settings_window, width=35)
    sett_window_button.grid(row=2, column=0, pady=(120, 0), padx=(95, 0))

    open_dir_bt = ctk.CTkButton(app, text="", image=ctk.CTkImage(folder_img), width=35, command=lambda: startfile(utils.get_dir()))
    open_dir_bt.grid(row=2, column=0, sticky="e", pady=(120, 0))

    install_win_bt = ctk.CTkButton(app, text="Installations window", command=installer_window, width=200)
    install_win_bt.grid(row=3, column=0, padx=(10, 0), pady=(10, 10))

    scrollable_frame = ctk.CTkScrollableFrame(app, width=360)
    scrollable_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

    news_data = mc.utils.get_minecraft_news()["article_grid"]
    append_news(scrollable_frame, news_data)

    try:
        with open(config_file, "rb") as config_read:
            config = pickle.load(config_read)
            name_tx.insert(0, config[0])
            version_drop.set(config[1])
            if config[2]:
                shared_data.update(config[2])
    except (TypeError, EOFError, FileNotFoundError):
        pass

    except (TypeError, EOFError):
        pass


    # TODO : Add the possibility to remove a version
    return app


def main():
    main_window().mainloop()


if __name__ == "__main__":
    main()


