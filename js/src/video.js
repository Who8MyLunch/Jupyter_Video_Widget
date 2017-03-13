var widgets = require('jupyter-js-widgets');
var _ = require('underscore');


// https://remysharp.com/2010/07/21/throttling-function-calls
// See updated version in comments
function throttle(fn, threshhold, scope) {
  // threshhold || (threshhold = 250);
  var last, deferTimer;

  return function () {
    var context = scope || this;

    var now = +new Date,
        args = arguments;
    if (last && now < last + threshhold) {
      // hold on to it
      clearTimeout(deferTimer);
      deferTimer = setTimeout(function () {
        last = now;
        fn.apply(context, args);
      }, threshhold + last - now);
    } else {
      last = now;
      fn.apply(context, args);
    }
  };
}


// Custom Model. Custom widgets models must at least provide default values for model
// attributes when different from the base class.  These include `_model_name`,
// `_view_name`, `_model_module`, and `_view_module` .
//
// When serialiazing entire widget state for embedding, only values different from the
// defaults will be specified.
var VideoModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(_.result(this, 'widgets.DOMWidgetModel.prototype.defaults'), {
        _model_name: 'VideoModel',
        _view_name: 'VideoView',
        _model_module: 'jupyter_video_widget',
        _view_module: 'jupyter_video_widget',
        _model_module_version : '0.0.1',
        _view_module_version : '0.0.1',
        src: '',
        currentTime: 0.0,
        playPause: false,
        _method: [],
        _property: [],
        _event: {},
    })
});


// Custom Widget View to render the model.

// https://www.html5rocks.com/en/tutorials/video/basics/
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
// https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Video_and_audio_content
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_manipulation

// Good stuff implementing custom video player
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/cross_browser_video_player

// Video player styling
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/Video_player_styling_basics

// Media buffering and seeking, nice example displaying time ranges where video is loaded
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/buffering_seeking_time_ranges

//  great example of capturing and displaying event info
// https://www.w3.org/2010/05/video/mediaevents.html

var VideoView = widgets.DOMWidgetView.extend({

    render: function() {
        // This project's view is a single <video/> element.
        this.video = document.createElement('video');
        this.setElement(this.video);

        this.video.controls = true;
        this.video.preload = 'auto';
        this.video.autoplay = false;
        // this.video.tabindex = 1;

        this.src_changed();

        this.model.on('change:_method', this.invoke_method, this);
        this.model.on('change:_property', this.set_property, this);
        this.model.on('change:_playPause', this.playPause_changed, this);
        this.model.on('change:src', this.src_changed, this);
        this.model.on('change:currentTime', this.currentTime_changed, this);

        //-------------------------------------------------
        // Video element event handlers, with throttling in miliseconds
        // frontend --> backend
        var throttled_handle_event = throttle(this.handle_event, 100, this);
        this.video.addEventListener('durationchange', throttled_handle_event);
        this.video.addEventListener('ended',          throttled_handle_event);
        this.video.addEventListener('loadedmetadata', throttled_handle_event);
        this.video.addEventListener('pause',          throttled_handle_event);
        this.video.addEventListener('play',           throttled_handle_event);
        this.video.addEventListener('playing',        throttled_handle_event);
        this.video.addEventListener('ratechange',     throttled_handle_event);
        this.video.addEventListener('seeked',         throttled_handle_event);
        this.video.addEventListener('seeking',        throttled_handle_event);
        this.video.addEventListener('volumechange',   throttled_handle_event);

        var throttled_handle_currentTime = throttle(this.handle_currentTime, 100, this);
        this.video.addEventListener('currentTime', throttled_handle_currentTime);

        // Mouse event handlers
        this.video.onwheel = function(ev) {
            // Prevent page from scrolling with mouse wheel when hovering over video
            ev.preventDefault();
        };

        var throttled_mouse_wheel = throttle(this.handle_mouse_wheel, 100, this);
        this.video.addEventListener('wheel', throttled_mouse_wheel);

        var throttled_mouse_click = throttle(this.handle_mouse_click, 100, this);
        this.video.addEventListener('click', throttled_mouse_click);

        // Keyboard events, enabled by setting tabindex attribute at start of this section
        // var throttled_keypress = throttle(this.handle_keypress, 50, this);
        // this.video.addEventListener('keypress', throttled_keypress);
        // didn't seem to work as expcted.....

        //-------------------------------------------------
        // Minor tweaks
        // Prevent context menu popup from right-click on canvas
        this.video.oncontextmenu = function(ev) {
            ev.preventDefault();
        };
    },

    invoke_method: function() {
        // backend --> frontend

        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
        var parts = this.model.get('_method');

        var name = parts[0];
        var stamp = parts[1];
        var args = parts[2];

        this.video[name](...args);
    },

    set_property: function() {
        // backend --> frontend

        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
        var parts = this.model.get('_property');

        var name = parts[0];
        var stamp = parts[1];
        var value = parts[2];

        this.video[name] = value;
    },

    src_changed: function() {
        // backend --> frontend
        var field = 'src';
        this.video[field] = this.model.get(field);
    },

    currentTime_changed: function() {
        // backend --> frontend
        var field = 'currentTime';
        this.video[field] = this.model.get(field);
    },

    playPause_changed: function() {
        // backend --> frontend
        if (this.video.paused) {
            this.video.play()
        } else {
            this.video.pause()
        }
    },

    handle_event: function(ev) {
        // General video-element event handler
        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
        var fields = ['autoplay', 'clientHeight', 'clientWidth', 'controls', 'currentTime',
                      'currentSrc', 'duration', 'ended', 'loop', 'muted', 'paused', 'playbackRate',
                      'seeking', 'videoHeight', 'videoWidth', 'volume']

        var pev = {'type': ev.type};
        for (let f of fields) {
            pev[f] = ev.target[f];
        }

        this.model.set('_event', pev)
        this.touch();  // Must call this after any frontend modifications to Model data.
    },

    handle_currentTime: function(ev) {
        this.model.set('currentTime', ev.target.currentTime);
        this.touch();  // Must call this after any frontend modifications to Model data.
    },

    // handle_keypress: function(ev) {
    //     console.log(ev);
    // },

    handle_mouse_wheel: function(ev) {
        // scrubbing takes over standard playback.
        this.video.pause()

        // Increment size
        // if ev.altKey
        // if ev.shiftKey
        var increment;  // seconds
        if (ev.ctrlKey) {
            // one second
            increment = 1;
        } else {
            // one frame (1/30)
            increment = 1/30;
        }

        if (ev.deltaY > 0) {
            // Scrub forwards
            this.video.currentTime += increment
        } else {
            // Scrub backwards
            this.video.currentTime -= increment
        }
    },

    handle_mouse_click: function(ev) {
        // a copy of playPause_changed event handler
        if (this.video.paused) {
            this.video.play()
        } else {
            this.video.pause()
        }
    },

});

module.exports = {
    VideoModel: VideoModel,
    VideoView: VideoView
};
