# jupyter_video_widget

A Jupyter widget to play videos via HTML5 video player.

## Information

- [Jupyter widgets documentation](https://ipywidgets.readthedocs.io/en/latest/)
    - [Building a custom widget](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Custom.html)
    - [Low-level widget tutorial](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Low%20Level.html)
- [Jupyter widgets github](https://github.com/ipython/ipywidgets)
- [Cookiecutter template](https://github.com/jupyter-widgets/widget-cookiecutter)



## Installation

To install use pip:

```bash
pip install jupyter_video_widget
jupyter nbextension enable --py --sys-prefix jupyter_video_widget
```

For a development installation (requires npm),

```bash
git clone https://github.com/who8mylunch/jupyter_video_widget.git
cd jupyter_video_widget
pip install -e .
jupyter nbextension install --py --symlink --sys-prefix jupyter_video_widget
jupyter nbextension enable  --py           --sys-prefix jupyter_video_widget
```

## Developer Workflow

not really sure what to do.  
npm plays a role, somehow...




## Ideas

- file selection compound widget: https://gist.github.com/DrDub/6efba6e522302e43d055
