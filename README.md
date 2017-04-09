# Jupyter Video Widget

A Jupyter widget that nmakes it easy to play videos (local and remote) via HTML5 video player.

## Information

- [Jupyter widgets documentation](https://ipywidgets.readthedocs.io/en/latest/)
    - [Building a custom widget](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Custom.html)
    - [Low-level widget tutorial](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Low%20Level.html)
- [Jupyter widgets github](https://github.com/ipython/ipywidgets)
- [Cookiecutter template](https://github.com/jupyter-widgets/widget-cookiecutter)

-[npm folders](https://docs.npmjs.com/files/folders)


## Notes and Ideas

### Miscelaneous links

- https://www.html5rocks.com/en/tutorials/video/basics/
- https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement
- https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
- https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Video_and_audio_content
- https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery
- https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_manipulation

### Good stuff implementing custom video player
- https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/cross_browser_video_player

### Video player styling
- https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/Video_player_styling_basics

### Media buffering and seeking, nice example displaying time ranges where video is loaded
- https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/buffering_seeking_time_ranges

### Media events
- https://www.w3.org/2010/05/video/mediaevents.html



## Prerequisites

```bash
jupyter nbextension enable --py --sys-prefix widgetsnbextension
```

## Standard Installation

Use pip to install:

```bash
pip install Jupyter_Video_Widget

jupyter nbextension enable --py --sys-prefix video_widget
```

## Developer Installation

Development installation requires npm.

```bash
git clone git@github.com:Who8MyLunch/Jupyter_Video_Widget.git

cd Jupyter_Video_Widget

pip install -e .
jupyter nbextension install --py --symlink --sys-prefix video_widget
jupyter nbextension enable  --py           --sys-prefix video_widget
```

# Developer Workflow

## Which Files to Edit?

- Jupyter_Video_Widget/
    - video_widget/             *All Python code lives here*
        - static/
        - __init__.py
        - _version.py
        - video.py              *Widget Python code*
        - server.py             *Included http video file server with builtin support for byte range requests*
        - namespace.py
    - js/                       *All JavaScript code lives here*
        - dist/
        - node_modules/
        - src/
            - video.js          *Widget javaScript code*
            - embed.js          *Only edit to update exported module name (e.g. video.js)*
            - index.js          *Only edit to update exported module name (e.g. video.js)*
            - extension.js
        - README.md
        - package.json          *Double check author name, email address, github org., etc.*
        - webpack.config.js 

## After Making an Edit

Change to the `js` folder and enter the following command:

```bash
npm install --save
```

This prepares and packages all JavaScript components and installs them into the `static` folder up
and over on the Python side. 

# Ideas for the Future

- file selection compound widget: https://gist.github.com/DrDub/6efba6e522302e43d055
- http://mindtrove.info/4-ways-to-extend-jupyter-notebook/#nb-server-exts
- http://jupyter-notebook.readthedocs.io/en/latest/extending/handlers.html

