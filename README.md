# Jupyter Video Widget

The goal of this project is to develop a custom Jupyter [widget](https://github.com/ipython/ipywidgets)
making it easy to play videos (local and remote) via HTML5 video player embededed in a Jupyter Notebook.
This widget was initialized using this very handy Cookiecutter [template](https://github.com/jupyter-widgets/widget-cookiecutter).


## Prerequisites

Need to enable ipywidgets notebook extension if not already done.

```bash
jupyter nbextension enable --py --sys-prefix widgetsnbextension
```

## Example



## Standard Installation

Use pip to install:

```sh
pip install Jupyter-Video-Widget

jupyter nbextension enable --py --sys-prefix jpy_video
```

Modify above `nbextension` command as needed for your own configuration and/or environment.

## Developer Installation

Development installation requires npm.

```bash
git clone git@github.com:Who8MyLunch/Jupyter_Video_Widget.git

cd Jupyter_Video_Widget

pip install -e .
jupyter nbextension install --py --symlink --sys-prefix jpy_video
jupyter nbextension enable  --py           --sys-prefix jpy_video
```


## After Making Changes to JavaScript Code

Change to the `js` folder (the one containing the file `package.json`) and enter the following command:

```bash
npm install --save
```

This prepares and packages all JavaScript components and installs them into the `static` folder up
and over on the Python side.   See the links below for more helpful information:
- https://docs.npmjs.com/cli/install
- http://stackoverflow.com/questions/19578796/what-is-the-save-option-for-npm-install


## File Layout

Note: I found this write-up at npmjs.com very helpful in understanding the required folder layout: https://docs.npmjs.com/files/folders.

- Jupyter_Video_Widget/
    - jpy_video/                *All Python code lives here*
        - static/
        - version.py
        - video.py              *Widget Python code*
        - server.py             *Included http video file server with builtin support for byte range requests*
        - namespace.py
    - js/                       *All JavaScript code lives here*
        - dist/
        - node_modules/
        - src/
            - jupyter-video.js  *Widget javaScript code*
            - embed.js          *Only edit to update exported module name (e.g. video.js)*
            - index.js          *Only edit to update exported module name (e.g. video.js)*
            - extension.js
        - README.md
        - package.json          *Double check author name, email address, github org., etc.*
        - webpack.config.js     *Contains path to static JS folder on the Python side*
    - setup.py
    - setup.cfg
    - MANIFEST.in               *Relative path to static folder under jpy_video*
    - requirements.txt


## Reference Information

- Jupyter widgets documentation
    - [Jupyter widgets github](https://github.com/ipython/ipywidgets)
    - [Building a custom widget](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Custom.html)
    - [Low-level widget tutorial](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Low%20Level.html)

- Helpful HTML5 articles
    - [Good stuff about implementing custom video HTML5 player](https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/cross_browser_video_player)
    - [Video player styling](https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/Video_player_styling_basics)
    - [Media buffering and seeking, nice example displaying time ranges where video is loaded](https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/buffering_seeking_time_ranges)
    - [HTML5 media events](https://www.w3.org/2010/05/video/mediaevents.html)

- More information about HTML5 and video/audio media
    - https://www.html5rocks.com/en/tutorials/video/basics/
    - https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement
    - https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
    - https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Video_and_audio_content
    - https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery
    - https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_manipulation




# Ideas for the Future

- file selection compound widget: https://gist.github.com/DrDub/6efba6e522302e43d055
- http://mindtrove.info/4-ways-to-extend-jupyter-notebook/#nb-server-exts
- http://jupyter-notebook.readthedocs.io/en/latest/extending/handlers.html

