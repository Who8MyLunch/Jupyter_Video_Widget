import time
import os

import IPython
import ipywidgets

from ._version import __version__

from .monotext_widget import MonoText
from .video import Video, TimeCode

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
"""


class VideoPlayer(ipywidgets.VBox):
    """Compound video player widget

    Click the video display to start/stop playback.
    """
    def __init__(self, source, timebase=1/30):
        """Define a new player instance for supplied source
        """
        super().__init__()

        # Build the parts
        self.wid_video = Video(source, timebase=timebase)

        # self.wid_video.layout.width = '100%'  # scale to fit inside parent element
        self.wid_video.layout.align_self = 'center'
        self.wid_video.layout.border = '1px solid grey'

        self.wid_timecode = TimeCode(timebase=timebase)

        # wid_button = ipywidgets.Button(icon='play')  # http://fontawesome.io/icon/pause/

        # self.wid_slider = ipywidgets.FloatSlider(min=0, max=60, step=timebase,
        #                                          continuous_update=True, orientation='horizontal',
        #                                          readout=False,
        #                                          slider_color='blue')
        # self.wid_slider.layout.width = '50%'

        self.wid_label = MonoText(text='source: {}'.format(source))

        # Setup event handlers
        self.wid_video.on_displayed(self._handle_displayed)
        self.wid_video.on_event(self._handle_loaded_metadata, 'loadedmetadata')
        self.wid_video.on_event(self._handle_duration_change, 'durationchange')

        # Assemble
        # self.wid_controls = ipywidgets.HBox(children=[self.wid_timecode, self.wid_slider])
        self.wid_controls = ipywidgets.HBox(children=[self.wid_timecode, self.wid_label])
        self.children = [self.wid_video, self.wid_controls]

        # Link widgets at front end
        # ipywidgets.jslink((self.wid_video, 'current_time'), (self.wid_slider, 'value'))
        ipywidgets.jsdlink((self.wid_video, 'current_time'), (self.wid_timecode, 'timecode'))

    #--------------------------------------------
    # wid_video.on_event(handle_any)
    def _handle_displayed(self, *args, **kwargs):
        """Do stuff that can only be done after widget is displayed
        """
        pass
        # self.wid_video.set_property('controls', False)

    def _handle_duration_change(self, wid, properties):
        """Update anything that depends on video duration
        """
        pass
        # self.wid_slider.max = properties.duration

    def _handle_loaded_metadata(self, wid, properties):
        """Function to be called when sufficient video metadata has been loaded at the frontend
        """
        width = properties.videoWidth
        self.layout.width = '{}px'.format(width+ 5)
        self.wid_video.layout.width = '{}px'.format(width)
        self.layout.align_self = 'center'

    def display(self):
        IPython.display.display(self)

    @property
    def properties(self):
        return self.wid_video.properties


#------------------------------------------------
if __name__ == '__main__':
    pass
