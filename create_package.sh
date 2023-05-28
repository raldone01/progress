#!/bin/sh

pyinstaller --onefile --add-data "icon_dark.svg:." --add-data "icon_light.svg:." --add-data "messages.txt:." progress.py
