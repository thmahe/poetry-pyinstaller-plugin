# package-directory

Test package functionality with all known variations for a `onedir` install

## Expected result

```tree
.
└── dist
    └── pyinstaller
        └── {Platform}
            └── package-directory
                ├── docs
                │   └── index.html
                ├── LICENSE
                ├── package-directory ............. Executable
                ├── _package-directory_internal
                │   ├── element_images
                │   │   ├── image_a.png
                │   │   └── image.png
                │   ├── icon_a.ico
                │   └── icon.ico
                └── USER_README.md
```

## Notes

* What is being tested: Are files being placed in the correct location?
* This README should *not* be included
* `main.py` functionality is essential for testing
* `sys._MEIPASS = "dist/pyinstaller/{platform}/_package-directory_internal"`
