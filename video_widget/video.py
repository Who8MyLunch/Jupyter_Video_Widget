
import time
import os

import IPython
import ipywidgets as widgets
import traitlets
import shortuuid

from ._version import __version__
from .namespace import Struct
from . import server

__all__ = ['Video', 'TimeCode']

@widgets.register()
class TimeCode(widgets.HTMLWidget):
    _view_name =   traitlets.Unicode('TimeCodeView').tag(sync=True)
    _view_module = traitlets.Unicode('video').tag(sync=True)
    _view_module_version = traitlets.Unicode(__version__).tag(sync=True)

    _model_name =   traitlets.Unicode('TimeCodeModel').tag(sync=True)
    _model_module = traitlets.Unicode('video').tag(sync=True)
    _model_module_version = traitlets.Unicode(__version__).tag(sync=True)

    # Private information
    _method = traitlets.List().tag(sync=True)
    _property = traitlets.List().tag(sync=True)
    _play_pause = traitlets.Bool(False).tag(sync=True)
    _event = traitlets.Dict().tag(sync=True)

    # Public information
    src = traitlets.Unicode('').tag(sync=True)
    current_time = traitlets.Float().tag(sync=True)

    def __init__(self, source=None):
        """Create new widget instance
        """
        super().__init__()

        self.properties = Struct()
        self.server = None


@widgets.register()
class Video(widgets.DOMWidget):
    """HTML5 video player as a Jupyter widget
    """
    _view_name =   traitlets.Unicode('VideoView').tag(sync=True)
    _view_module = traitlets.Unicode('video').tag(sync=True)
    _view_module_version = traitlets.Unicode(__version__).tag(sync=True)

    _model_name =   traitlets.Unicode('VideoModel').tag(sync=True)
    _model_module = traitlets.Unicode('video').tag(sync=True)
    _model_module_version = traitlets.Unicode(__version__).tag(sync=True)

    # Private information
    _method = traitlets.List().tag(sync=True)
    _property = traitlets.List().tag(sync=True)
    _play_pause = traitlets.Bool(False).tag(sync=True)
    _event = traitlets.Dict().tag(sync=True)

    # Public information
    src = traitlets.Unicode('').tag(sync=True)
    current_time = traitlets.Float().tag(sync=True)

    def __init__(self, source=None):
        """Create new widget instance
        """
        super().__init__()

        self.properties = Struct()
        self.server = None
        self.filename = None

        # Manage user-defined Python callback functions for frontend events
        self._event_dispatchers = {}  # widgets.widget.CallbackDispatcher()

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
        if not fname:
            # Supplied filename is None, '', or similar.
            # Set filename to None and shutdown server if running
            self._filename = ''
            if self.server:
                self.server.stop()
            return
        elif not os.path.isfile(fname):
            raise ValueError('File does not exist: {}'.format(fname))

        # Configure internal http server for local file
        self._filename = os.path.realpath(fname)

        # Start server if not already running, update path
        path_served = os.path.dirname(self._filename)
        if not self.server:
            self.server = server.Server(path=path_served)
            self.server.start()
        else:
            self.server.path = path_served

        # Random version string to avoid browser cacheing issues
        version = '?v={}'.format(shortuuid.uuid())

        # Set local file URL via internal http server
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
    def play_pause(self):
        """Toggle video playback
        """
        self._play_pause = not self._play_pause

    def play(self):
        """Begin video playback
        """
        self.invoke_method('play')

    def pause(self):
        """Pause video playback
        """
        self.invoke_method('pause')

    def rewind(self):
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
    # Event handler stuff
    # def handle_current_time(self, change):
    #     pass


    @traitlets.observe('current_time', '_event')
    def _handle_event(self, change):
        """Respond to front-end backbone events
        https://traitlets.readthedocs.io/en/stable/api.html#callbacks-when-trait-attributes-change
        """
        assert(change['type'] == 'change')

        if change['name'] == '_event':
            event = change['new']   # new stuff is a dict of information from front end
            self.properties.update(event)
        elif change['name'] == 'current_time':
            event = {'type': 'timeupdate',     # new stuff is a single number for current_time
                     'currentTime': change['new']}
            self.properties.update(event)
        else:
            # raise error or not?
            return

        # Call any registered event-specific handler functions
        if event['type'] in self._event_dispatchers:
            self._event_dispatchers[event['type']](self, **event)

        # Call any general event handler function
        if '' in self._event_dispatchers:
            self._event_dispatchers[''](self, **event)



    #--------------------------------------------
    # Register Python event handlers
    _known_event_types = []
    def on_event(self, callback, event_type='', remove=False):
        """(un)Register a Python event=-handler functions.
        Default is to register for all event types.
        May be called repeatedly to set multiple callback functions.

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

        Supplied callback function(s) must accept two arguments: widget instance and event dict.
        Note: no checking is done to verify that supplied event type is valid.
        """
        if event_type not in self._known_event_types:
            self._known_event_types.append(event_type)

        if event_type not in self._event_dispatchers:
            self._event_dispatchers[event_type] = widgets.widget.CallbackDispatcher()

        # Register with specified dispatcher
        self._event_dispatchers[event_type].register_callback(callback, remove=remove)

        # else:
        #     # Register with all known dispatchers
        #     for v in self._event_dispatchers.values():
        #         v.register_callback(callback, remove=remove)

    def on_pause(callback):
        """Register Python event handler for 'pause' event.
        Convenience wrapper around on_event().
        """
        self.on_event('pause', callback)

    def on_play(callback):
        """Register Python event handler for 'play' event.
        Convenience wrapper around on_event().
        """
        self.on_event('play', callback)

    def on_ready(callback):
        """Register Python event handler for 'ready' event.
        Convenience wrapper around on_event().
        """
        # https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/readyState
        self.on_event('loadedmetadata', callback)

    def unregister(self):
        """Unregister all event handler functions.
        """
        callbacks = []
        for dispatcher in self.event_dispatchers.values():
            callbacks += dispatcher.callbacks

        for cb in callbacks:
            self.on_event(cb, remove=True)

#------------------------------------------------
if __name__ == '__main__':
    pass
