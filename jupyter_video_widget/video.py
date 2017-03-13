
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
    _view_module_version = traitlets.Unicode('0.0.1').tag(sync=True)

    _model_name =   traitlets.Unicode('VideoModel').tag(sync=True)
    _model_module = traitlets.Unicode('jupyter_video_widget').tag(sync=True)
    _model_module_version = traitlets.Unicode('0.0.1').tag(sync=True)

    # Behind-the-scenes information
    _method = traitlets.List().tag(sync=True)
    _property = traitlets.List().tag(sync=True)
    _event = traitlets.Dict().tag(sync=True)
    _playPause = traitlets.Bool(False).tag(sync=True)

    # Public information
    src = traitlets.Unicode('').tag(sync=True)
    currentTime = traitlets.Float().tag(sync=True)

    def __init__(self, src=''):
        """
        Create new widget instance
        """
        super().__init__()

        self.src = src

        # Manage user-defined Python callback functions for frontend events
        self._event_dispatcher = widgets.widget.CallbackDispatcher()

    @property
    def state(self):
        """
        Video widget current property values (read only).
        """
        return self._event.copy()

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
    def playPause(self):
        self._playPause = not self._playPause

    def play(self):
        self.invoke_method('play')

    def pause(self):
        self.invoke_method('pause')

    def rewind(self):
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

        # Call any registered event handlers
        self._event_dispatcher(self, event)

    #--------------------------------------------
    # Register Python event handlers
    def on_event(self, callback, remove=False):
        """
        Register frontend-event callback function.

        Set keyword remove=True to unregister an existing callback function.

        Supplied callback function(s) must accept two arguments: widget instance and event dict.
        """
        # Register/un-register
        self._event_dispatcher.register_callback(callback, remove=remove)

        # # Default to all defined event types
        # if not kinds:
        #     kinds = self._event_dispatchers.keys()
        # if isinstance(kinds, str):
        #     kinds = [kinds]
        # for k in kinds:
        #     if k not in self._event_dispatchers:
        #         raise ValueError('Unexpected kind of callback: {}'.format(k))
        #     # Register/un-register
        #     self._event_dispatchers[k].register_callback(callback, remove=remove)

        # Enable/disable event handling at front end.
        # self._handlers_active = self._num_handlers() > 0

    # def _num_handlers(self):
    #     numbers = [len(d.callbacks) for d in self._event_dispatchers.values()]
    #     return sum(numbers)

#------------------------------------------------
if __name__ == '__main__':
    pass
