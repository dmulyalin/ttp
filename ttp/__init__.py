name = "ttp"

__all__ = ["ttp"]
__author__ = "Denis Mulyalin <d.mulyalin@gmail.com>"
__version__ = "0.9.5"
from sys import version_info

# get python version:
python_major_version = version_info.major

if python_major_version == 3:
    from ttp.ttp import ttp
    from ttp.utils.quick_parse import quick_parse
elif python_major_version == 2:
    from ttp import ttp
    from utils.quick_parse import quick_parse
