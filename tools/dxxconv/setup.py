from setuptools import setup

setup(
    #install_requires=["numpy", "soundfile"],
    entry_points={
        "console_scripts": [
            "dxxconv = dxxconv:main"
        ]
    }
)
