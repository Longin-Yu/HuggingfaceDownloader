from setuptools import setup, find_packages

setup(
    name="hfdown",
    version="0.0.1",
    author="Hao Yu",
    author_email="longinyh@gmail.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hfdown = hfdown.downloader:main',
        ],
    },
)