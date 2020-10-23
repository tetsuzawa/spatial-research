from setuptools import setup

setup(
    name="dxx",
    version="1.2.1",
    description="dxx is a library for converting binary files",
    packages=["dxx"],
    install_requires=["numpy", "SoundFile"],
    entry_points={
        "console_scripts": [
            "dxxconv = dxx.dxxconv:main"
        ]
    },
    author="Tetsu Takizawa",
    author_email="tetsu.varmos@gmail.com",
    url="https://github.com/tetsuzawa/spatial-research/tree/master/modules/dxx"
)
