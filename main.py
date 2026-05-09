import sys
import json
import importlib.resources
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QTabWidget, QCheckBox, QProgressBar,
    QMessageBox
)
from PySide6.QtCore import QThread
from graphenium.backend.runner import CommandRunner
from graphenium.backend.system import SystemDetector

CONFIG_PATH = Path.home() / ".config/graphenium/config.json"

class WorkerThread(QThread):
    def __init__(self, runner, commands):
        super().__init__()
        self.runner = runner
        self.commands = commands

    def run(self):
        for cmd in self.commands:
            self.runner.run_command(cmd)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphenium Manager")
        self.setMinimumSize(800, 600)

        self.packages_data = self.load_packages()
        self.detector = SystemDetector()
        self.selected = {
            "desktop": None,
            "drivers": [],
            "packages": [],
            "aur": False,
            "flatpak": False,
            "dry_run": False
        }

        self.setup_ui()
        self.load_config()
        self.detect_system()

    def load_packages(self):
        with importlib.resources.open_text("graphenium", "packages.json") as f:
            return json.load(f)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.tabs = QTabWidget()

        self.tabs.addTab(self.create_welcome_tab(), "Welcome")
        self.tabs.addTab(self.create_desktop_tab(), "Desktop")
        self.tabs.addTab(self.create_drivers_tab(), "Drivers")
        self.tabs.addTab(self.create_packages_tab(), "Packages")
        self.tabs.addTab(self.create_aur_tab(), "AUR & Flatpak")
        self.tabs.addTab(self.create_review_tab(), "Review")
        self.tabs.addTab(self.create_install_tab(), "Install")

        layout.addWidget(self.tabs)

    def create_welcome_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<h2>Welcome to Graphenium Manager</h2>"))
        l.addWidget(QLabel("Post-install setup for vanilla Arch Linux.\n"
                          "Select options, review commands, then apply.\n\n"
                          "<b>WARNING:</b> Run on fresh Arch installs only."))
        l.addStretch()
        return w

    def create_desktop_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<h3>Select Desktop Environment</h3>"))

        self.de_checkboxes = {}
        for de in ["gnome", "kde", "xfce", "hyprland"]:
            cb = QCheckBox(de.capitalize())
            cb.toggled.connect(lambda checked, d=de: self.select_desktop(d, checked))
            self.de_checkboxes[de] = cb
            l.addWidget(cb)
        l.addStretch()
        return w

    def select_desktop(self, de, checked):
        if checked:
            for other, cb in self.de_checkboxes.items():
                if other!= de:
                    cb.setChecked(False)
            self.selected["desktop"] = de
        else:
            self.selected["desktop"] = None

    def create_drivers_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<h3>Graphics Drivers</h3>"))

        self.driver_checkboxes = {}
        for drv in ["nvidia", "amd", "intel"]:
            cb = QCheckBox(drv.upper())
            cb.toggled.connect(lambda checked, d=drv: self.toggle_driver(d, checked))
            self.driver_checkboxes[drv] = cb
            l.addWidget(cb)
        l.addStretch()
        return w

    def toggle_driver(self, drv, checked):
        if checked:
            if drv not in self.selected["drivers"]:
                self.selected["drivers"].append(drv)
        else:
            if drv in self.selected["drivers"]:
                self.selected["drivers"].remove(drv)

    def create_packages_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<h3>Extra Packages</h3>"))

        self.pkg_checkboxes = {}
        for pkg in ["flatpak", "firefox", "git", "neofetch", "htop", "vlc"]:
            cb = QCheckBox(pkg)
            cb.toggled.connect(lambda checked, p=pkg: self.toggle_package(p, checked))
            self.pkg_checkboxes[pkg] = cb
            l.addWidget(cb)
        l.addStretch()
        return w

    def toggle_package(self, pkg, checked):
        if checked:
            if pkg not in self.selected["packages"]:
                self.selected["packages"].append(pkg)
        else:
            if pkg in self.selected["packages"]:
                self.selected["packages"].remove(pkg)

    def create_aur_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<h3>AUR & Flatpak</h3>"))

        self.aur_cb = QCheckBox("Install paru AUR helper")
        self.aur_cb.toggled.connect(lambda checked: self.selected.update({"aur": checked}))

        self.flatpak_cb = QCheckBox("Enable Flatpak + Flathub")
        self.flatpak_cb.toggled.connect(lambda checked: self.selected.update({"flatpak": checked}))

        self.dry_cb = QCheckBox("Dry run - generate script only, don't execute")
        self.dry_cb.toggled.connect(lambda checked: self.selected.update({"dry_run": checked}))

        l.addWidget(self.aur_cb)
        l.addWidget(self.flatpak_cb)
        l.addWidget(self.dry_cb)
        l.addStretch()
        return w

    def create_review_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        self.review_text = QTextEdit()
        self.review_text.setReadOnly(True)
        l.addWidget(QLabel("<h3>Review Commands</h3>"))
        l.addWidget(self.review_text)

        btn = QPushButton("Generate Command List")
        btn.clicked.connect(self.generate_commands)
        l.addWidget(btn)
        return w

    def generate_commands(self):
        cmds = self.build_commands()
        text = "\n".join([" ".join(c) for c in cmds])
        self.review_text.setText(text)

    def create_install_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #1e1e1e; color: #d4d4d4; font-family: monospace;")

        self.progress = QProgressBar()

        self.install_btn = QPushButton("Start Installation")
        self.install_btn.clicked.connect(self.start_install)

        l.addWidget(QLabel("<h3>Installation Log</h3>"))
        l.addWidget(self.log)
        l.addWidget(self.progress)
        l.addWidget(self.install_btn)
        return w

    def build_commands(self):
        cmds = []

        if not self.detector.check_internet():
            cmds.append(["echo", "ERROR: No internet connection detected"])

        cmds.append(["sudo", "pacman", "-Syu", "--noconfirm"])

        if self.selected["desktop"]:
            pkgs = self.packages_data["desktops"][self.selected["desktop"]]
            cmds.append(["sudo", "pacman", "-S", "--noconfirm"] + pkgs)

            dm_cmds = {
                "gnome": ["sudo", "systemctl", "enable", "gdm"],
                "kde": ["sudo", "systemctl", "enable", "sddm"],
                "xfce": ["sudo", "systemctl", "enable", "lightdm"]
            }
            if self.selected["desktop"] in dm_cmds:
                cmds.append(dm_cmds[self.selected["desktop"]])

        for drv in self.selected["drivers"]:
            cmds.append(["sudo", "pacman", "-S", "--noconfirm"] + self.packages_data["drivers"][drv])

        if self.selected["packages"]:
            cmds.append(["sudo", "pacman", "-S", "--noconfirm"] + self.selected["packages"])

        if self.selected["flatpak"]:
            cmds.append(["sudo", "pacman", "-S", "--noconfirm", "flatpak"])
            cmds.append(["flatpak", "remote-add", "--if-not-exists", "flathub",
                         "https://flathub.org/repo/flathub.flatpakrepo"])

        if self.selected["aur"]:
            cmds.append(["sudo", "pacman", "-S", "--noconfirm", "base-devel", "git"])
            cmds.append(["git", "clone", "https://aur.archlinux.org/paru.git", "/tmp/paru"])
            cmds.append(["bash", "-c", "cd /tmp/paru && makepkg -si --noconfirm"])
            cmds.append(["rm", "-rf", "/tmp/paru"])

        cmds.extend([
            ["sudo", "systemctl", "enable", "bluetooth"],
            ["sudo", "systemctl", "enable", "ufw"]
        ])

        return cmds

    def start_install(self):
        if not any([self.selected["desktop"], self.selected["drivers"],
                   self.selected["packages"], self.selected["aur"], self.selected["flatpak"]]):
            QMessageBox.warning(self, "Warning", "Select at least one option")
            return

        self.save_config()
        cmds = self.build_commands()

        if self.selected["dry_run"]:
            script_path = Path.home() / "graphenium_commands.sh"
            with open(script_path, 'w') as f:
                f.write("#!/bin/bash\n")
                for cmd in cmds:
                    f.write(" ".join(cmd) + "\n")
            self.log.setText(f"Dry run complete.\nScript saved to: {script_path}\nRun it with: bash {script_path}")
            return

        self.install_btn.setEnabled(False)
        self.log.clear()

        self.runner = CommandRunner()
        self.runner.output_signal.connect(self.log.append)
        self.runner.finished_signal.connect(self.on_cmd_finished)

        self.cmd_queue = cmds
        self.current_cmd = 0
        self.progress.setMaximum(len(cmds))
        self.run_next_command()

    def run_next_command(self):
        if self.current_cmd < len(self.cmd_queue):
            self.progress.setValue(self.current_cmd)
            self.runner.run_command(self.cmd_queue[self.current_cmd])
        else:
            self.log.append("\nAll done! Reboot recommended.")
            self.install_btn.setEnabled(True)
            self.progress.setValue(self.progress.maximum())

    def on_cmd_finished(self, code):
        if code!= 0:
            self.log.append(f"\nCommand failed with code {code}. Stopping.")
            self.install_btn.setEnabled(True)
            return
        self.current_cmd += 1
        self.run_next_command()

    def detect_system(self):
        gpu = self.detector.detect_gpu()
        internet = self.detector.check_internet()
        self.log.append(f"Detected GPU: {gpu}") if hasattr(self, 'log') else None
        self.log.append(f"Internet: {'OK' if internet else 'NO CONNECTION'}") if hasattr(self, 'log') else None

    def save_config(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.selected, f)

    def load_config(self):
        if not CONFIG_PATH.exists():
            return
        try:
            with open(CONFIG_PATH) as f:
                data = json.load(f)
                self.selected.update(data)

                if data.get("desktop"):
                    self.de_checkboxes[data["desktop"]].setChecked(True)
                for drv in data.get("drivers", []):
                    if drv in self.driver_checkboxes:
                        self.driver_checkboxes[drv].setChecked(True)
                for pkg in data.get("packages", []):
                    if pkg in self.pkg_checkboxes:
                        self.pkg_checkboxes[pkg].setChecked(True)
                self.aur_cb.setChecked(data.get("aur", False))
                self.flatpak_cb.setChecked(data.get("flatpak", False))
                self.dry_cb.setChecked(data.get("dry_run", False))
        except:
            pass

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()