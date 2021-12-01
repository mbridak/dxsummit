# DXSummit
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)  [![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)  [![Made With:PyQt5](https://img.shields.io/badge/Made%20with-PyQt5-red)](https://pypi.org/project/PyQt5/)

## What is it?

Pulls latest dxsummit spots. Displays them in a compact interface. If you have an instance of `rigctld` running, when you click on a spot your radio will automatically tune to the spotted frequency and change modes to match the spot.   Filter output to band and or mode.

![screenshot](pic/screen.png)

## Running from source

First install the needed dependencies.

`python3 -m pip3 install -r requirements.txt`

Or if you're the Ubuntu/Debian type you can:

`sudo apt install python3-pyqt5 python3-requests`

Then, run the program from source.

`./dxsummit.py` or `python3 dxsummit.py`

## Building a binary

If you are so inclined, I've included a .spec file so you can build a binary version for easy launching.

If you don't have pyinstaller already you can:

`python3 -m pip3 install pyinstaller`

Then `pyinstaller -F dxsummit.spec`

You should then find your executable in the `dist` folder that has just been created.
