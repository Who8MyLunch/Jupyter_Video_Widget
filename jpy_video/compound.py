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
        self._source = source
        self._timebase = timebase
        self.wid_video = Video(source, timebase=timebase)

        # Video event handlers
        self.wid_video.on_displayed(self._handle_displayed)
        self.wid_video.on_event(self._handle_loaded_metadata, 'loadedmetadata')
        self.wid_video.on_event(self._handle_duration_change, 'durationchange')
        self.wid_video.on_event(self._handle_rate_change, 'ratechange')

        # Define additional widget components
        # self.wid_video.layout.width = '100%'  # scale to fit inside parent element
        self.wid_video.layout.align_self = 'center'
        self.wid_video.layout.border = '1px solid grey'

        self.wid_timecode = TimeCode(timebase=timebase)

        # wid_button = ipywidgets.Button(icon='play')  # http://fontawesome.io/icon/pause/

        # Progress bar/slider
        self.wid_slider = ipywidgets.FloatSlider(min=0, max=1, step=timebase,
                                                 continuous_update=True, orientation='horizontal',
                                                 readout=False,
                                                 slider_color='blue')
        self.wid_slider.layout.width = '50%'

        # Text info
        self.wid_info = MonoText()

        # Assemble the parts
        self.wid_box = ipywidgets.HBox(children=[self.wid_timecode, self.wid_slider])
        # self.wid_controls_B = ipywidgets.HBox(children=[self.wid_timecode,
        #                                               self.wid_slider,
        #                                               self.wid_info])

        self.children = [self.wid_video, self.wid_box, self.wid_info]

        # Link widgets at front end
        # ipywidgets.jsdlink((self.wid_video, 'current_time'), (self.wid_progress, 'value'))
        ipywidgets.jslink((self.wid_video, 'current_time'), (self.wid_slider, 'value'))
        ipywidgets.jsdlink((self.wid_video, 'current_time'), (self.wid_timecode, 'timecode'))

    def _update_info(self):
        tpl = "Source: {} | Timebase: {:.1f} fps | Playback: {}x"

        try:
            rate = self.properties.playbackRate
        except KeyError:
            rate = 1

        text = tpl.format(os.path.basename(self._source),
                          1/self._timebase,
                          rate)

        self.wid_info.text = text

    #--------------------------------------------
    def _handle_displayed(self, *args, **kwargs):
        """Do stuff that can only be done after widget is displayed
        """
        self.wid_video.set_property('controls', False)

    def _handle_duration_change(self, wid, properties):
        """Update anything that depends on video duration
        """
        self.wid_slider.max = properties.duration

    def _handle_rate_change(self, wid, properties):
        """Update anything that depends on playback rate
        """
        self._update_info()

    def _handle_loaded_metadata(self, wid, properties):
        """Function to be called when sufficient video metadata has been loaded at the frontend
        """
        width = properties.videoWidth
        self.wid_video.layout.width = '{}px'.format(width)
        self.layout.width = '{}px'.format(width + 5)
        self.layout.align_self = 'center'
        self._update_info()

    def display(self):
        IPython.display.display(self)

    @property
    def properties(self):
        return self.wid_video.properties


#------------------------------------------------
if __name__ == '__main__':
    pass
