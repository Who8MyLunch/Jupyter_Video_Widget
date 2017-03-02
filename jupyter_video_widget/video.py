import ipywidgets as widgets
from traitlets import Unicode


@widgets.register()
class Video(widgets.DOMWidget):
    """
    A Jupyter widget for standard HTML5 video player.
    """
    _view_name =   Unicode('VideoView').tag(sync=True)
    _view_module = Unicode('jupyter_video_widget').tag(sync=True)
    _view_module_version = Unicode('0.0.1').tag(sync=True)

    _model_name =   Unicode('VideoModel').tag(sync=True)
    _model_module = Unicode('jupyter_video_widget').tag(sync=True)
    _model_module_version = Unicode('0.0.1').tag(sync=True)

    url = Unicode('Hello World!, sadafsaf').tag(sync=True)

