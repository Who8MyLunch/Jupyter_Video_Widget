
import time

import ipywidgets as widgets
import traitlets

from . import struct

@widgets.register()
class Video(widgets.DOMWidget):
    """
    HTML5 video player as a Jupyter widget
    """
    _view_name =   traitlets.Unicode('VideoView').tag(sync=True)
    _view_module = traitlets.Unicode('jupyter_video_widget').tag(sync=True)
    _view_module_version = traitlets.Unicode('0.1.0').tag(sync=True)

    _model_name =   traitlets.Unicode('VideoModel').tag(sync=True)
    _model_module = traitlets.Unicode('jupyter_video_widget').tag(sync=True)
    _model_module_version = traitlets.Unicode('0.1.0').tag(sync=True)

    # Private information
    _method = traitlets.List().tag(sync=True)
    _property = traitlets.List().tag(sync=True)
    _event = traitlets.Dict().tag(sync=True)
    _play_pause = traitlets.Bool(False).tag(sync=True)

    # Public information
    src = traitlets.Unicode('').tag(sync=True)
    currentTime = traitlets.Float().tag(sync=True)

    def __init__(self, src=''):
        """
        Create new widget instance
        """
        super().__init__()

        self.src = src
        self._properties = struct.Struct()

        # Manage user-defined Python callback functions for frontend events
        self._event_dispatchers = {}  # widgets.widget.CallbackDispatcher()

    @property
    def properties(self):
        """
        Video widget current property values (read only).
        """
        return self._properties

    @property
    def ready_state(self):
        """
        Integer indicating the readiness state of the media.

        HAVE_NOTHING        0   No information is available about the media resource.
        HAVE_METADATA       1   Enough of the media resource has been retrieved that the metadata
                                attributes are initialized. Seeking will no longer raise an
                                exception.
        HAVE_CURRENT_DATA   2   Data is available for the current playback position, but not
                                enough to actually play more than one frame.
        HAVE_FUTURE_DATA    3   Data for the current playback position as well as for at least a
                                little bit of time into the future is available (in other words, at
                                least two frames of video, for example).
        HAVE_ENOUGH_DATA    4   Enough data is available—and the download rate is high enough—that
                                the media can be played through to the end without interruption.

        https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/readyState
        """
        return self.properties.readyState

    def invoke_method(self, name, *args):
        """
        Invoke arbitrary front-end method
        """
        stamp = time.time()  # timestamp required to ensure unqique event
        self._method = [name, stamp, args]

    def set_property(self, name, value):
        """
        Assign value to arbitrary front-end property
        """
        stamp = time.time()  # timestamp required to ensure unqique event
        self._property = [name, stamp, value]

    #--------------------------------------------
    # Video methods
    def play_pause(self):
        self._play_pause = not self._play_pause

    def play(self):
        self.invoke_method('play')

    def pause(self):
        self.invoke_method('pause')

    def rewind(self):
        self.pause()
        self.set_property('currentTime', 0)

    def seek(self, time):
        self.set_property('currentTime', time)

    #--------------------------------------------
    # Event handler stuff
    @traitlets.observe('_event')
    def _handle_event(self, change):
        """
        Respond to front-end events
        https://traitlets.readthedocs.io/en/stable/api.html#callbacks-when-trait-attributes-change
        """
        assert(change['type'] == 'change')
        assert(change['name'] == '_event')
        event = change['new']

        self._properties.update(event)

        # Call any registered event handlers
        if event['type'] in self._event_dispatchers:
            self._event_dispatchers[event['type']](self, event)


    #--------------------------------------------
    # Register Python event handlers
    def on_event(self, event_type, callback, remove=False):
        """
        Register frontend-event callback function.

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

    # def on_pause(callback):
    #     self.on_event('pause', callback)

    # def on_play(callback):
    #     self.on_event('play', callback)

    def on_ready(callback):
        """
        Convenience method to set a callback function to be called when sufficient metadata
        is loaded by frontend video element.

        May be called repeatedly to set multiple callback functions.
        """
        self.on_event('loadedmetadata', callback)

    def unregister(self):
        """
        Unregister all event handler functions.
        """
        callbacks = []
        for dispatcher in self.event_dispatchers.values():
            callbacks += dispatcher.callbacks

        for cb in callbacks:
            self.on_event(cb, remove=True)



# class FancyVideo(Video)::
#     def __init__(self, src=''):
#         """
#         Create new widget instance
#         """
#         super().__init__(src)




#------------------------------------------------
if __name__ == '__main__':
    pass
