# package-one-file

Test package functionality with all known variations for a `onefile` install

## Expected result

```tree
.
└── dist
    └── pyinstaller
        └── {platform}
            ├── docs
            │   └── index.html
            ├── LICENSE
            ├── package-one-file ............. Executable
            └── USER_README.md
```

## Notes

* What is being tested: Are files files assessable in the `exe` and are other
  files in the correct location?
* This README should *not* be included
* `main.py` functionality is **essential** for testing
* `sys._MEIPASS = "%TEMP%"`
