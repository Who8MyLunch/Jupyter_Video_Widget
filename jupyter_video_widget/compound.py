import time
import os

import IPython
import ipywidgets as widgets

from ._version import __version__

from .video import Video

__all__ = ['Player']

"""
Compound video player widget
"""

# build various individual widgets:
# - video
# - slider
# - nice time numbers, including N/30 as surrogate for frame number
# - play, pause
#
