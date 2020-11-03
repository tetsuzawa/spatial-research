from setuptools import setup

setup(
    install_requires=["numpy", "dxx"],
    entry_points={
        "console_scripts": [
            "cosine_windowing = cosine_windowing:main"
        ]
    }
)
