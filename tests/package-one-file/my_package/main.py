import sys
from pathlib import Path

# pyinstaller internal variable
root = sys._MEIPASS

for file in [
    "icon.ico",
    "icon_a.ico",
    "element_images/image.png",
    "element_images/image_a.png",
]:
    if Path(root, file).exists():
        print(f"{file} exists")
