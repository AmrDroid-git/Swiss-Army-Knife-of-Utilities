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
| -------- | ------------------ |
| Python   | `main.py`          |
| Java     | `Main.java`        |
| C        | `Main.c`           |
| C++      | `Main.cpp`         |

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
```

---

## Requirements

### Required

- Python 3.10 or newer recommended
- `pip`
- PySide6
- markdown

### Optional, depending on the scripts you want to run

- Java JDK, if you want to run Java utilities
- GCC, if you want to run C utilities
- G++, if you want to run C++ utilities
- Extra Python packages required by custom scripts, for example `Pillow`, `yt-dlp`, `img2pdf`, etc.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Swiss-Army-Knife-of-Utilities.git
cd Swiss-Army-Knife-of-Utilities/SAKU
```

Replace `YOUR_USERNAME` with your GitHub username if needed.

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

On Linux/macOS, you may need:

```bash
python3 main.py
```

> Important: run the app from inside the `SAKU/` folder so that workspace files are saved in the correct place.

---

## How to Use the Application

### 1. Open the dashboard

When the application starts, the dashboard displays the available workspace groups and utility windows.

From the dashboard, you can:

- create a new workspace,
- create a new group,
- open a workspace,
- import a ZIP workspace,
- export a workspace,
- change appearance settings,
- change language,
- adjust zoom.

### 2. Create a workspace

Use:

```text
File > New Window
```

Give the workspace a name. The app will create a new editable utility window.

### 3. Enter Design Mode

Click the **Design Mode** button.

A widget palette appears on the side of the window. Drag widgets from the palette into the canvas.

### 4. Build the interface

For example, a simple utility interface may contain:

- a label explaining the tool,
- one or more input fields,
- a button to run the script,
- an output field,
- a console widget.

You can move and resize widgets directly on the canvas.

### 5. Link a script

Right-click the script button and link/import the script folder.

The script folder should contain one of the supported entry files:

```text
main.py
Main.java
Main.c
Main.cpp
```

### 6. Configure input order

Right-click input widgets and set their argument order if needed.

For example:

| Widget            | arg_order | Sent to script as |
| ----------------- | --------: | ----------------- |
| First text input  |         0 | first argument    |
| Second text input |         1 | second argument   |
| File input        |         2 | third argument    |

### 7. Run the utility

Disable **Design Mode** to switch to Run Mode, fill in the inputs, and click the script button.

The script output will appear in the console or output widgets.

### 8. Save the workspace

Click **Save Project** to save the current canvas layout and widget configuration.

---

## Creating a Custom Utility Script

A Python utility can receive the values from the GUI through command-line arguments.

Example:

```python
# main.py
import sys

name = sys.argv[1]
print(f"Hello, {name}!")
```

If your canvas has one text input with `arg_order = 0`, the value entered by the user will be passed to `sys.argv[1]`.

For scripts that generate files, the engine detects newly created files and can move them to the selected output folder.

---

## Example Workflow

Example: creating a simple addition tool.

1. Create a new workspace called `Addition_Tool`.
2. Enable Design Mode.
3. Add two text input widgets.
4. Add one output text widget.
5. Add a script button.
6. Add a console widget.
7. Link a Python script named `main.py`.
8. Set the first input order to `0`.
9. Set the second input order to `1`.
10. Save the project.
11. Disable Design Mode and run the tool.

Example script:

```python
# main.py
import sys

a = float(sys.argv[1])
b = float(sys.argv[2])

print(a + b)
```

---

## Import and Export

Workspaces can be exported as ZIP files and imported later.

This allows users to:

- share utilities with others,
- back up their tools,
- move utilities between computers,
- create a reusable library of personal tools.

---

## Current Prototype Scope

This version focuses mainly on validating the architecture of the application:

- a functional PySide6 desktop interface,
- a dashboard for workspace management,
- a dynamic canvas,
- reusable GUI widgets,
- JSON-based saving and loading,
- script execution from the interface,
- import/export support,
- example lightweight scripts for testing.

The project is designed to be extended with more real utilities over time.

---

## Roadmap

Possible future improvements:

- add more built-in utilities,
- improve the graphical utility builder,
- add more validation options for inputs,
- support more scripting languages,
- improve sandboxing for safer script execution,
- add a community marketplace for sharing utilities,
- package the app as an executable for Windows/Linux/macOS,
- add automated tests,
- improve documentation with screenshots and tutorials.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'app'`

Make sure you are running the app from inside the `SAKU/` folder:

```bash
cd SAKU
python main.py
```

### `PySide6` is missing

Install dependencies again:

```bash
pip install -r requirements.txt
```

### Java/C/C++ script does not run

Make sure the required compiler is installed and available in your system PATH.

For Java:

```bash
javac -version
java -version
```

For C/C++:

```bash
gcc --version
g++ --version
```

### Script is not detected

Use the expected file names exactly:

```text
main.py
Main.java
Main.c
Main.cpp
```

### The interface freezes or script does not respond

The engine uses asynchronous process execution, but long-running or interactive scripts should print output regularly and flush when necessary.

---

## Security Note

Imported utilities and linked scripts run locally on your machine. Only import or execute scripts from trusted sources.

---

## Authors

Developed as part of a PPP academic project by:

- Adem Ben Yarou
- Amr Slama

---

## License

This project is currently an academic prototype. Add a license file before public release if the repository is intended to be open source.
