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



wid_slider = ipywidgets.FloatSlider(description='Test:', min=0, max=10.0, step=1/30,
                                    continuous_update=True, orientation='horizontal', readout=True,
                                    readout_format='.2f', slider_color='white')

ipywidgets.jslink((wid, 'current_time'), (wid_slider, 'value'))

class VideoPlayer():
    """
    Compound video player widget.
    """
    def __init__(self, source):
        """
        Define a new player instance for supplied source
        """


    def display(self):
        IPython.display.display(self.container)

