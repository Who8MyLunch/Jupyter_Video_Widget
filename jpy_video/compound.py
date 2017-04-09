import time
import os

import IPython
import ipywidgets as widgets

from ._version import __version__

from .video import Video

__all__ = ['Player']

"""
Compound video player widget based on my own custom HTML5 video widget combined with various
builtin Jupyter widgets.

Available Jupyter widgets:
    Jupyter.BoundedFloatText
    Jupyter.BoundedIntText
    Jupyter.Box
    Jupyter.Button
    Jupyter.ButtonStyle
    Jupyter.Checkbox
    Jupyter.ColorPicker
    Jupyter.Controller
    Jupyter.ControllerAxis
    Jupyter.ControllerButton
    Jupyter.DatePicker
    Jupyter.Dropdown
    Jupyter.FloatProgress
    Jupyter.FloatRangeSlider
    Jupyter.FloatSlider
    Jupyter.FloatText
    Jupyter.HBox
    Jupyter.HTML
    Jupyter.HTMLMath
    Jupyter.Image
    Jupyter.IntProgress
    Jupyter.IntRangeSlider
    Jupyter.IntSlider
    Jupyter.IntText
    Jupyter.Label
    Jupyter.Play
    Jupyter.ProgressStyle
    Jupyter.RadioButtons
    Jupyter.Select
    Jupyter.SelectMultiple
    Jupyter.SelectionSlider
    Jupyter.SliderStyle
    Jupyter.Tab
    Jupyter.Text
    Jupyter.Textarea
    Jupyter.ToggleButton
    Jupyter.ToggleButtons
    Jupyter.VBox
    Jupyter.Valid
    jupyter.DirectionalLink
    jupyter.Link
    jupyter_video_widget.videoVide
"""

# build various individual widgets:
# - video
# - slider
# - nice time numbers, including N/30 as surrogate for frame number
# - buttons: play, pause, fast play fast rev play, ??
#

class VideoPlayer(ipywidgets.VBox):
    """Compound video player widget
    """
    def __init__(self, source):
        """Define a new player instance for supplied source
        """
        #$ Build the parts
        wid_video = Video(source)

        wid_video.layout.width = '100%'  # scale to fit inside parent element
        wid_video.layout.align_self = 'center'
        wid_video.layout.border = '2px solid grey'

        wid_button = ipywidgets.Button(icon='play')  # http://fontawesome.io/icon/pause/

        wid_slider = ipywidgets.FloatSlider(description=None, min=0, max=60, step=1/30,
                                            continuous_update=True, orientation='horizontal',
                                            readout=True, readout_format='.2f',
                                            slider_color='blue')
        ipywidgets.Label()

        ipywidgets.HBox
        ipywidgets.VBox
        ipywidgets.FloatSlider
        ipywidgets.jslink
        ipywidgets.jsdlink

        # Store things in self
        # self.asdsadsad = asdasd

        # Setup event handlers for video event
        wid_video.on_event('durationchange', self._handle_duration_change)

    def _handle_duration_change(self, event):
        print(event.duration)
        self.wid_slider.max = event.duration


    def display(self):
        IPython.display.display(self.container)


# ipywidgets.jslink((wid, 'current_time'), (wid_slider, 'value'))

# wid_slider = ipywidgets.FloatSlider(description='Test:', min=0, max=10.0, step=1/30,
#                                     continuous_update=True, orientation='horizontal', readout=True,
#                                     readout_format='.2f', slider_color='white')

# ipywidgets.jslink((wid, 'current_time'), (wid_slider, 'value'))



