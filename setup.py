from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

__author__ = "Denis Mulyalin <d.mulyalin@gmail.com>"

setup(
    name="ttp",
    version="0.5.0",
    author="Denis Mulyalin",
    author_email="d.mulyalin@gmail.com",
    description="Template Text Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dmulyalin/ttp",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': ['ttp=ttp.ttp:cli_tool'],
    }
)