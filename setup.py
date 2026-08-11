from setuptools import setup

APP = ["assistant_ui.py"]
DATA_FILES = ["character.png", ".env"]
OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "CFBundleName": "Zebraz",
        "CFBundleDisplayName": "Zebraz",
        "CFBundleGetInfoString": "Zebraz desktop AI assistant",
        "CFBundleIdentifier": "com.nihal.zebraz",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
    },
    "packages": ["PyQt6", "pynput", "dotenv"],
    "includes": ["google.genai", "google.auth", "AppKit"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
