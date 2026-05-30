# Swiss Army Knife of Utilities

<p align="center">
  <b>A modular desktop application for building and running small utility tools from one clean interface.</b>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-blue">
  <img alt="PySide6" src="https://img.shields.io/badge/GUI-PySide6-green">
  <img alt="Status" src="https://img.shields.io/badge/status-prototype-orange">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey">
</p>

---

## Why this app?

Many everyday computer tasks are simple, but they are often annoying to do:

- resizing an image,
- converting files,
- merging documents,
- running small scripts,
- testing quick developer utilities,
- or automating repeated actions.

Usually, the user has to choose between online tools, command-line scripts, or installing many separate applications. Online tools can require uploads, internet access, and may create privacy or security concerns. Command-line tools are powerful, but not comfortable for every user.

**Swiss Army Knife of Utilities** solves this by providing one desktop application where utilities can be created, organized, executed, and shared through a visual interface.

The main idea is simple:

> Instead of building one fixed application for one task, this project provides a flexible GUI builder where each utility can have its own interface and its own script behind it.

---

## What is Swiss Army Knife of Utilities?

Swiss Army Knife of Utilities, also called **SAKU**, is a Python desktop application built with **PySide6**. It allows users to create small utility windows visually, link buttons to scripts, provide inputs through GUI widgets, and display the results directly inside the application.

The project works like a lightweight visual scripting environment:

1. Create a workspace.
2. Design its interface using drag-and-drop widgets.
3. Link a script to a button.
4. Run the tool from the GUI.
5. Save, organize, import, or export the workspace.

---

## Main Features

### Visual workspace builder

Create utility interfaces visually using drag-and-drop components.

Available components include:

- script trigger button,
- text input,
- text output,
- select/dropdown field,
- file input,
- folder input,
- output folder selector,
- normal console,
- interactive console,
- requirements/documentation link,
- labels.

### Edit Mode and Run Mode

The application has two main modes:

- **Edit Mode**: design the interface, move widgets, resize widgets, configure properties, and link scripts.
- **Run Mode**: lock the layout and use the interface like a normal application.

This separation makes the app easy to use both as a builder and as a finished utility launcher.

### Script execution engine

The app includes a script engine that executes scripts without freezing the GUI.

Supported script entry files:

| Language | Expected file name |
|---|---|
| Python | `main.py` |
| Java | `Main.java` |
| C | `Main.c` |
| C++ | `Main.cpp` |

Python scripts run directly. Java, C, and C++ scripts can be compiled before execution when the required compiler is installed.

### Real-time console output

The application captures script output and displays it in console widgets in real time. This makes it easier to understand what the script is doing without opening an external terminal.

### Input ordering

Input widgets can be ordered using an `arg_order` property. When a script is executed, the app collects input values, sorts them by order, and passes them to the script as command-line arguments.

### Workspace management

The dashboard allows users to:

- create workspaces,
- organize workspaces into groups,
- open existing workspaces,
- rename groups,
- move workspaces between groups,
- delete workspaces,
- import and export workspaces as ZIP files.

### Theme, zoom, and language support

The project includes:

- multiple themes,
- saved zoom settings,
- saved window geometry,
- multilingual interface support.

---

## Project Structure

```text
Swiss-Army-Knife-of-Utilities/
│
├── SAKU/
│   ├── main.py                       # Application entry point
│   ├── requirements.txt              # Python dependencies
│   ├── description.txt               # Architecture notes
│   │
│   ├── app/
│   │   ├── core/                     # Core logic
│   │   │   ├── group_manager.py      # Workspace group management
│   │   │   ├── package_manager.py    # Save/load/import/export logic
│   │   │   ├── script_engine.py      # Script execution engine
│   │   │   ├── theme_manager.py      # Theme handling
│   │   │   └── zoom_manager.py       # Zoom/window settings
│   │   │
│   │   ├── ui/                       # Main windows and canvas
│   │   │   ├── dashboard.py          # Startup dashboard
│   │   │   ├── dynamic_canvas.py     # Workspace editor and runner
│   │   │   └── edit_palette.py       # Widget palette
│   │   │
│   │   ├── widgets/                  # Reusable GUI components
│   │   ├── themes/                   # Theme JSON files
│   │   ├── assets/                   # Fonts and visual assets
│   │   └── translations.json         # UI translations
│   │
│   └── user_workspaces/              # Saved local workspaces
│
└── TEST SCRIPTS light weight/         # Example scripts for testing
