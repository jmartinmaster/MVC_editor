# MVC Editor

A beautiful, dark-themed text editor written in Python using **PyQt6**, structured with the classic **Model-View-Controller (MVC)** architectural pattern.

## Features
- **Clean Architecture**: Separates the data (`DocumentModel`), user interface (`EditorView`), and application flow logic (`EditorController`).
- **Premium Aesthetics**: Features a custom-styled dark-mode interface with customized typography and tailored styling inspired by Catppuccin Mocha.
- **Cross-platform**: Written in Python and can be packaged as a standalone Windows executable.

## Setup & Running

### 1. Prerequisites
Ensure you have Python 3.8+ installed.

### 2. Install Dependencies
Install the required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Run the App
Launch the application:
```bash
python main.py
```

## Packaging with PyInstaller

To bundle the application into a standalone Windows executable, you can run PyInstaller.

### Single-file Executable (No console window)
```bash
pyinstaller --onefile --noconsole --name "MVC_Editor" main.py
```

Or simply run the provided helper script:
```bash
.\build.bat
```
The compiled output will be generated inside the `dist/` directory.
