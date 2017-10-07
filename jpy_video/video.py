
import time
import os

import IPython
import ipywidgets
import traitlets
import shortuuid

from ._version import __version__
from ordered_namespace import Struct
from . import server


__all__ = ['Video', 'TimeCode']


@ipywidgets.register()
class TimeCode(ipywidgets.HTML):
    """Nicely-formatted timecode text display
    """
    _view_name =   traitlets.Unicode('TimeCodeView').tag(sync=True)
    _view_module = traitlets.Unicode('jupyter-video').tag(sync=True)
    _view_module_version = traitlets.Unicode(__version__).tag(sync=True)

    _model_name =   traitlets.Unicode('TimeCodeModel').tag(sync=True)
    _model_module = traitlets.Unicode('jupyter-video').tag(sync=True)
    _model_module_version = traitlets.Unicode(__version__).tag(sync=True)

    # Public information
    timecode = traitlets.Float().tag(sync=True)
    timebase = traitlets.Float().tag(sync=True)

    def __init__(self, timebase=1/30):
        """Create new widget instance
        """
        super().__init__()

        self.timebase = timebase

        self.layout.border = '1px solid grey'
        self.layout.justify_content = 'center'
        self.layout.align_items = 'center'
        self.layout.align_self = 'center'
        self.layout.width = 'fit-content'
        # self.layout.height = '14pt'



@ipywidgets.register()
class Video(ipywidgets.DOMWidget):
    """HTML5 video player as a Jupyter widget
    """
    _view_name =   traitlets.Unicode('VideoView').tag(sync=True)
    _view_module = traitlets.Unicode('jupyter-video').tag(sync=True)
    _view_module_version = traitlets.Unicode(__version__).tag(sync=True)

    _model_name =   traitlets.Unicode('VideoModel').tag(sync=True)
    _model_module = traitlets.Unicode('jupyter-video').tag(sync=True)
    _model_module_version = traitlets.Unicode(__version__).tag(sync=True)

    # Private information
    _method = traitlets.List().tag(sync=True)
    _property = traitlets.List().tag(sync=True)
    _play_pause = traitlets.Bool(False).tag(sync=True)
    _event = traitlets.Dict().tag(sync=True)
    _enable_keyboard = traitlets.Bool(True).tag(sync=True)

    # Public information
    src = traitlets.Unicode('').tag(sync=True)
    current_time = traitlets.Float().tag(sync=True)
    timebase = traitlets.Float().tag(sync=True)

    def __init__(self, source=None, timebase=1/30):
        """Create new widget instance
        """
        super().__init__()

        self.timebase = timebase
        self.properties = Struct()
        self.server = None
        self.filename = None

        # Manage user-defined Python callback functions for frontend events
        self._event_dispatchers = {}  # ipywidgets.widget.CallbackDispatcher()

        if source:
            if os.path.isfile(source):
                # Setting filename starts an internal http server with support for byte-range requests
                # This makes for smooth-as-butter seeking, fast-forward, etc.
                self.filename = source
            elif src:
                # set src traitlet directly
                self.src = source

        # Style
        self.layout.width = '100%'  # scale to fit inside parent element
        self.layout.align_self = 'center'

    def __del__(self):
        if self.server:
            self.server.stop()

    def display(self):
        IPython.display.display(self)

    @property
    def filename(self):
        """Full path to local video file
        """
        return self._filename

    @filename.setter
    def filename(self, fname):
        self.set_filename(fname)

    def set_filename(self, fname, host=None, port=None):
        """Set filename for local video
        """
        if not fname:
            # Supplied filename is None, '', or similar.
            # Set filename to None and shutdown server if running
            self._filename = ''
            if self.server:
                self.server.stop()
            return

        elif not os.path.isfile(fname):
            raise IOError('File does not exist: {}'.format(fname))

        # Configure internal http server for local file
        self._filename = os.path.realpath(fname)

        if not port:
            port = 0
        if not host:
            host = 'localhost'

        # Start server if not already running, update path
        path_served = os.path.dirname(self._filename)
        if not self.server:
            self.server = server.Server(path=path_served, host=host, port=port)
            self.server.start()
        else:
            self.server.path = path_served

        # Random version string to avoid browser caching issues
        version = '?v={}'.format(shortuuid.uuid())

        # Set local file URL for use by internal http server
        self.src = self.server.filename_to_url(self._filename+version)

    def invoke_method(self, name, *args):
        """Invoke method on front-end HTML5 video element
        https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
        """
        stamp = time.time()  # timestamp required to ensure unqique event
        self._method = [name, stamp, args]

    def set_property(self, name, value):
        """Assign value to front-end HTML5 video element property
        https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
        """
        stamp = time.time()  # timestamp required to ensure unqique event
        self._property = [name, stamp, value]

    #--------------------------------------------
    # Video activity control methods
    def play_pause(self, *args, **kwargs):
        """Toggle video playback
        """
        self._play_pause = not self._play_pause

    def play(self, *args, **kwargs):
        """Begin video playback
        """
        self.invoke_method('play')

    def pause(self, *args, **kwargs):
        """Pause video playback
        """
        self.invoke_method('pause')

    def rewind(self, *args, **kwargs):
        """Pause video, then seek to beginning
        """
        self.pause()
        self.current_time = 0

    def seek(self, time):
        """Seek to a specific time
        """
        self.pause()
        self.current_time = time

    #--------------------------------------------
    # Register Python event handlers
    # _known_event_types = []
    def on_event(self, callback, event_type='', remove=False):
        """(un)Register a Python event=-handler functions.
        Default is to register for all event types.  May be called repeatedly to set multiple
        callback functions. Supplied callback function(s) must accept two arguments: widget
        instance and event dict.  Note that no checking is done to verify that supplied event type
        is valid.

        Non-exhaustive list of event types:
            - durationchange
            - ended
            - loadedmetadata
            - pause
            - play
            - playing
            - ratechange
            - seeked
            - seeking
            - volumechange
            - timeupdate

        Set keyword remove=True to unregister an existing callback function.
        """
        # if event_type not in self._known_event_types:
        #     self._known_event_types.append(event_type)

        if event_type not in self._event_dispatchers:
            self._event_dispatchers[event_type] = ipywidgets.widget.CallbackDispatcher()

        # Register with specified dispatcher
        self._event_dispatchers[event_type].register_callback(callback, remove=remove)

        # else:
        #     # Register with all known dispatchers
        #     for v in self._event_dispatchers.values():
        #         v.register_callback(callback, remove=remove)

    def on_pause(self, callback):
        """Register Python event handler for 'pause' event.
        Convenience wrapper around on_event().
        """
        self.on_event('pause', callback)

    def on_play(self, callback):
        """Register Python event handler for 'play' event.
        Convenience wrapper around on_event().
        """
        self.on_event('play', callback)

    def on_ready(self, callback):
        """Register Python event handler for 'ready' event.
        Convenience wrapper around on_event().
        """
        # https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/readyState
        self.on_event('loadedmetadata', callback)

    # def on_display(self, callback):
    #     this method is already builtin to parent DOM Widget class
    #     pass

    def unregister(self):
        """Unregister all event handler functions.
        """
        callbacks = []
        for dispatcher in self.event_dispatchers.values():
            callbacks += dispatcher.callbacks

        for cb in callbacks:
            self.on_event(cb, remove=True)

    #--------------------------------------------
    # Respond to front-end events by calling user's registered handler functions
    @traitlets.observe('current_time', '_event')
    def _handle_event(self, change):
        """Respond to front-end backbone events
        https://traitlets.readthedocs.io/en/stable/api.html#callbacks-when-trait-attributes-change
        """
        assert(change['type'] == 'change')

        if change['name'] == '_event':
            # new stuff is a dict of information from front end
            event = change['new']
            self.properties.update(event)
        elif change['name'] == 'current_time':
            # new stuff is a single number for current_time
            event = {'type': 'timeupdate',
                     'currentTime': change['new']}
            self.properties.update(event)
        else:
            # raise error or not?
            return

        # Call any registered event-specific handler functions
        if event['type'] in self._event_dispatchers:
            self._event_dispatchers[event['type']](self, self.properties)

        # Call any general event handler function
        if '' in self._event_dispatchers:
            self._event_dispatchers[''](self, self.properties)


#------------------------------------------------
if __name__ == '__main__':
    pass
