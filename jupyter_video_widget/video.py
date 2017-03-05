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

    url = traitlets.Unicode().tag(sync=True)
    _method = traitlets.List().tag(sync=True)
    _property = traitlets.List().tag(sync=True)
    _event = traitlets.List().tag(sync=True)

    def __init__(self, url=None):
        """
        Create new widget instance
        """
        super().__init__()

        if url:
            self.url = url

    def _invoke_method(self, name, *args):
        """
        Invoke front-end method
        """
        self._method = [name, args]

    def _set_property(self, name, value):
        """
        Assign value to front-end property
        """
        self._property = [name, value]

    @traitlets.observe('_event')
    def _handle_event(self, change):
        """
        Respond to front-end event
        https://traitlets.readthedocs.io/en/stable/api.html#callbacks-when-trait-attributes-change
        """
        print(change['type'], change['name'])

    #--------------------------------------------

    def play(self):
        self._invoke_method('play')

    def pause(self):
        self._invoke_method('pause')



