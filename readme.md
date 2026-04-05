# 🚀 System Optimizer Pro

Welcome to **System Optimizer Pro**, a modern, lightweight, and fast system cleaning utility for Windows. Built with Python and `customtkinter`, this tool features a sleek dark-mode UI and helps you free up disk space, manage installed applications, and clear browser data securely.

Developed by **KARIO** ([@ilickft](https://github.com/ilickft)).

---

## ✨ Features

### 🧹 1. System Temp Cleaner
Safely scans and removes temporary junk files that clog up your system storage. Includes a real-time progress bar and space-saved calculation.
* Targets user `%TEMP%` directory.
* Targets `C:\Windows\Temp`.
* Targets `C:\Windows\Prefetch`.
* *Note: Requires Administrator privileges to fully clean Prefetch and Windows Temp directories.*

### 🗑️ 2. Program Uninstaller
A responsive, easy-to-read list of all installed programs on your machine.
* Reads directly from the Windows Registry (including WOW6432Node) for maximum accuracy.
* Safely triggers the software's official uninstaller strings.

### 🌐 3. Universal Browser Cleaner
Clear out cache, cookies, and history across multiple browsers and profiles simultaneously. 
* **Supported Browsers:** Google Chrome, Microsoft Edge, Brave, Mozilla Firefox, Opera, and Opera GX.
* **Smart Profile Detection:** Automatically detects and cleans multiple active user profiles (e.g., "Default", "Profile 1", "Profile 2") in Chromium-based browsers, a feature many standard cleaners miss.

---

## 🛠️ Installation & Usage

### Running the Executable
If you downloaded the pre-compiled release:
1. Download the latest `.exe` from the [Releases](../../releases) tab.
2. Right-click the executable and select **"Run as Administrator"** (Highly recommended for the Uninstaller and Temp Cleaner to work correctly).

### Running from Source
If you want to run or modify the Python code directly:

1. Ensure you have Python 3.8+ installed.
2. Install the required UI library:
   ```bash
   pip install customtkinter