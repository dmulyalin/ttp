name = "ttp"

__all__ = ["ttp"]
__author__ = "Denis Mulyalin <d.mulyalin@gmail.com>"
__version__ = "0.0.2"
from sys import version_info

# get python version:
python_major_version = version_info.major

if python_major_version == 3:
    from ttp.ttp import ttp
elif python_major_version == 2:
    from ttp import ttp
