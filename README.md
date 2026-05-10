            

**Graphenium Manager**

A GUI post-install setup tool for vanilla Arch Linux. Install drivers, desktop environments, packages, and AUR/Flatpak helpers without touching the terminal.

Built with Python + PySide6.

---

Why i made this

i know that Installing drivers and packages on Arch after a fresh install is super hard.. it means running 20+ pacman commands by hand. Terminal-only scripts are fine, but most people want to click, review, and apply.

Graphenium Manager gives you a GUI to pick what you want, see the exact commands it’ll run, and apply them. Includes a dry-run mode so you can generate the script without executing anything.

*Made for use right after installing Arch Linux.*

Features

- *Desktop Environments*: GNOME, KDE, XFCE, Hyprland
- *GPU Drivers*: Nvidia, AMD, Intel auto-detection
- *Packages*: Firefox, Git, Flatpak, Htop, VLC, etc
- *AUR & Flatpak*: Install `paru` and enable Flathub in one click
- *Dry Run Mode*: Generate `~/graphenium_commands.sh` without running anything
- *Config Save/Load*: Remembers your selections at `~/.config/graphenium/config.json`



Installation

From AUR

****

paru -S graphenium-manager-git

****

From Source


git clone https://github.com/Abdul-abu/arch-graphenium-manager

cd graphenium-manager

makepkg -si

****

Then launch it from your app menu or run:
graphenium-manager


_Note_: Run as your normal user, not with sudo. The app uses `pkexec` for privileged commands.

Usage

1. Launch the app
2. Select your desktop, drivers, and packages
3. Check the "Review" tab to see the commands
4. Enable "Dry run" if you want to inspect the script first
5. Hit "Start Installation" and reboot when done

Warning

This tool is for fresh Arch Linux installs only. Don’t run it on EndeavourOS, Manjaro, or other Arch derivatives. It will break things.



****



**Contributing**

Contributions are welcome. To contribute:

1. Fork the repo and clone it locally
2. Set up Arch Linux in a VM using VirtualBox, QEMU, or Boxes
3. Install `python-pyside6`, clone the repo, and run the program
4. Test your changes in the VM using dry-run mode
5. Record a video or GIF of your test run and submit it with your pull request
