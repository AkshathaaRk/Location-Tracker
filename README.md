# LocTracker

A location tracking application built with Python.

## Features

- Location tracking capabilities
- Built as a standalone executable using PyInstaller

## Project Structure

- `loc.py` - Main application file
- `loc.spec` - PyInstaller specification file
- `build/` - Build artifacts directory

## Installation

Clone the repository and install any required dependencies:

```bash
git clone <repository-url>
cd loctracker
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python loc.py
```

## Building

To build a standalone executable:

```bash
pyinstaller loc.spec
```

The executable will be created in the `dist/` directory.

