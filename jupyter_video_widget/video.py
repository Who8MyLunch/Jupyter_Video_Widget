
import time
import os

import ipywidgets as widgets
import traitlets
import shortuuid

from ._version import __version__
from .namespace import Struct
from . import server

__all__ = ['Video']

@widgets.register()
class Video(widgets.DOMWidget):
    """HTML5 video player as a Jupyter widget
    """
    _view_name =   traitlets.Unicode('VideoView').tag(sync=True)
    _view_module = traitlets.Unicode('jupyter_video_widget').tag(sync=True)
    _view_module_version = traitlets.Unicode(__version__).tag(sync=True)

    _model_name =   traitlets.Unicode('VideoModel').tag(sync=True)
    _model_module = traitlets.Unicode('jupyter_video_widget').tag(sync=True)
    _model_module_version = traitlets.Unicode(__version__).tag(sync=True)

    # Private information
    _method = traitlets.List().tag(sync=True)
    _property = traitlets.List().tag(sync=True)
    _event = traitlets.Dict().tag(sync=True)
    _play_pause = traitlets.Bool(False).tag(sync=True)

    # Public information
    src = traitlets.Unicode('').tag(sync=True)
    currentTime = traitlets.Float().tag(sync=True)

    def __init__(self, src='', filename=''):
        """Create new widget instance
        """
        super().__init__()

        self.properties = Struct()
        self.server = None
        self.filename = None

        # Manage user-defined Python callback functions for frontend events
        self._event_dispatchers = {}  # widgets.widget.CallbackDispatcher()

        if filename:
            # Setting filename starts an internal http server with support for byte-range requests
            # This makes for smooth-as-butter seeking, fast-forward, etc.
            self.filename = filename
        elif src:
            # set src traitlet directly
            self.src = src

    def __del__(self):
        if self.server:
            self.server.stop()

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
        self._play_pause = not self._play_pause

    def play(self):
        self.invoke_method('play')

    def pause(self):
        self.invoke_method('pause')

    def rewind(self):
        self.pause()
        self.currentTime = 0

    def seek(self, time):
        self.pause()
        self.currentTime = time

    #--------------------------------------------
    # Event handler stuff
    @traitlets.observe('_event')
    def _handle_event(self, change):
        """Respond to front-end events
        https://traitlets.readthedocs.io/en/stable/api.html#callbacks-when-trait-attributes-change
        """
        assert(change['type'] == 'change')
        assert(change['name'] == '_event')
        event = change['new']

        # Update internal copy of Video element properties
        self.properties.update(event)

        # Call any registered event handlers
        if event['type'] in self._event_dispatchers:
            self._event_dispatchers[event['type']](self, event)

    #--------------------------------------------
    # Register Python event handlers
    def on_event(self, event_type, callback, remove=False):
        """Register Python callback functions.

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

        Set keyword remove=True to unregister an existing callback function.
        Supplied callback function(s) must accept two arguments: widget instance and event dict.
        Note: no checking is done to verify that supplied event type is valid.
        """
        if event_type not in self._event_dispatchers:
            self._event_dispatchers[event_type] = widgets.widget.CallbackDispatcher()

        # Register/un-register
        self._event_dispatchers[event_type].register_callback(callback, remove=remove)

    def on_pause(callback):
        self.on_event('pause', callback)

    def on_play(callback):
        self.on_event('play', callback)

    def on_ready(callback):
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
