# This file is named "types_" because of a naming conflict in the Python stdlib

import typing as T
import os

Path = T.Union[str, os.PathLike]
Number = T.Union[int, float]
