import ipywidgets as widgets
import traitlets

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
    # _handlers_active = traitlets.Bool(False).tag(sync=True)

    # Public information
    src = traitlets.Unicode().tag(sync=True)
    currentTime = traitlets.Float().tag(sync=True)

    def __init__(self, src=''):
        """
        Create new widget instance
        """
        super().__init__()

        self.src = src

        # Allow user-defined Python callback functions for any of these event types
        # kinds = ['durationchange', 'ended', 'loadedmetadata', 'pause', 'play', 'playing',
        #          'ratechange', 'seeked', 'volumechange']
        # self._event_dispatchers = {}
        # for k in kinds:
        #     self._event_dispatchers[k] = widgets.widget.CallbackDispatcher()

        # Manage user-defined Python event callback functions
        self._event_dispatcher = widgets.widget.CallbackDispatcher()

        self._state = {}

    @property
    def state(self):
        """
        Video widget state information
        """
        return self._state

    def invoke_method(self, name, *args):
        """
        Invoke front-end method
        """
        self._method = [name, args]

    def set_property(self, name, value):
        """
        Assign value to front-end property
        """
        self._property = [name, value]

    @traitlets.observe('_event')
    def _handle_event(self, change):
        """
        Respond to front-end events
        https://traitlets.readthedocs.io/en/stable/api.html#callbacks-when-trait-attributes-change
        """
        assert(change['type'] == 'change')
        assert(change['name'] == '_event')
        event = change['new']

        # Update self state information
        self._state = event

        # Call any registered event handlers
        self._event_dispatcher(self, event)
        # try:
        #     # Do it
        #     kind = event['type']
        #     self._event_dispatchers[kind](self, event)
        # except KeyError:
        #     raise ValueError('Unexpected kind of event: {}'.format(kind))

    #--------------------------------------------
    # Register Python event handlers
    # def _num_handlers(self):
    #     numbers = [len(d.callbacks) for d in self._event_dispatchers.values()]
    #     return sum(numbers)

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

    #--------------------------------------------
    # Video methods
    def play(self):
        self.invoke_method('play')

    def pause(self):
        self.invoke_method('pause')

    def rewind(self):
        self.set_property('currentTime', 0)

    def seek(self, time):
        self.set_property('currentTime', time)

#------------------------------------------------
if __name__ == '__main__':
    pass
