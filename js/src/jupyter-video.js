var widgets = require('@jupyter-widgets/base');
var _ = require('underscore');


// https://remysharp.com/2010/07/21/throttling-function-calls
// See updated version in above article's comments
function throttle(fn, threshhold, scope) {
  // threshhold || (threshhold = 250);
  var last, deferTimer;

  return function () {
    var context = scope || this;

    var now = +new Date, args = arguments;
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

function zero_pad_two_digits(number) {
    var size = 2;
    var pretty = "00" + number;
    return pretty.substr(pretty.length-size);
}

//-----------------------------------------------

// Widget models must provide default values for the model attributes that are
// different from the base class.  These include at least `_model_name`, `_view_name`,
// `_model_module`, and `_view_module`.  When serialiazing entire widget state for embedding,
// only values different from default will be specified.

var TimeCodeModel = widgets.HTMLModel.extend({
    defaults: _.extend(_.result(this, 'widgets.HTMLModel.prototype.defaults'), {
        _model_name:   'TimeCodeModel',
        _model_module: 'jupyter-video',

        _view_name:    'TimeCodeView',
        _view_module:  'jupyter-video',
    })
});


var VideoModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(_.result(this, 'widgets.DOMWidgetModel.prototype.defaults'), {
        _model_name:   'VideoModel',
        _model_module: 'jupyter-video',

        _view_name:    'VideoView',
        _view_module:  'jupyter-video',
    })
});


//-----------------------------------------------

// Widget View renders the model to the DOM
var TimeCodeView = widgets.HTMLView.extend({
    // https://codereview.stackexchange.com/questions/49524/updating-single-view-on-change-of-a-model-in-backbone
    render: function() {
        this.listenTo(this.model, 'change:timecode', this.timecode_changed);

        TimeCodeView.__super__.render.apply(this);

        this.timecode_changed();
        this.update();

        return this;
    },

    timecode_changed: function() {
        var time_base = this.model.get('timebase');

        var t = this.model.get('timecode');  //  current video time in seconds

        var h = Math.floor((t/3600));
        var m = Math.floor((t % 3600)/60);
        var s = Math.floor((t % 60));
        var f = Math.floor((t % 1)/time_base);
        // var f = Math.round((t % 1)/time_base);

        // Pretty timecode string
        var time_string = zero_pad_two_digits(h) + ':' +
                          zero_pad_two_digits(m) + ':' +
                          zero_pad_two_digits(s) + ';' +
                          zero_pad_two_digits(f);

        var html = `<p style="font-family:   DejaVu Sans Mono, Consolas, Lucida Console, Monospace;'
                              font-variant:  normal;
                              font-weight:   bold;
                              font-style:    normal;
                              font-size:     11pt;
                              margin-left:   3pt;
                              margin-right:  3pt;
                              margin-top:    4pt;
                              margin-bottom: 2pt;
                              ">
                    ${time_string}</p>`;
                              // line-height:   13pt;">

        this.model.set('value', html);
        this.touch();
    },
});

//-----------------------------------------------

var VideoView = widgets.DOMWidgetView.extend({
    render: function() {
        // This project's view is a single <video/> element.
        this.video = document.createElement('video');
        this.setElement(this.video);

        this.video.preload = 'metadata';
        this.video.autoplay = false;
        this.video.controls = true;

        this.src_changed();

        // .listenTo() is better than .on()
        // http://backbonejs.org/#Events-listenTo
        // https://coderwall.com/p/fpxt4w/using-backbone-s-new-listento
        this.listenTo(this.model, 'change:_method',      this.invoke_method);
        this.listenTo(this.model, 'change:_property',    this.set_property);
        this.listenTo(this.model, 'change:_play_pause',  this.play_pause_changed);
        this.listenTo(this.model, 'change:src',          this.src_changed);
        this.listenTo(this.model, 'change:current_time', this.current_time_changed);

        //-------------------------------------------------
        // Video element event handlers
        // frontend --> backend
        // https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
        this.video.addEventListener('durationchange', this.handle_event.bind(this), false);
        this.video.addEventListener('ended',          this.handle_event.bind(this), false);
        this.video.addEventListener('loadedmetadata', this.handle_event.bind(this), false);
        this.video.addEventListener('pause',          this.handle_event.bind(this), false);
        this.video.addEventListener('play',           this.handle_event.bind(this), false);
        this.video.addEventListener('playing',        this.handle_event.bind(this), false);
        this.video.addEventListener('ratechange',     this.handle_event.bind(this), false);
        this.video.addEventListener('seeked',         this.handle_event.bind(this), false);
        this.video.addEventListener('seeking',        this.handle_event.bind(this), false);
        this.video.addEventListener('timeupdate',     this.handle_event.bind(this), false);
        this.video.addEventListener('volumechange',   this.handle_event.bind(this), false);

        // Special handling for play and pause events
        this.enable_fast_time_update = false
        this.video.addEventListener('play',  this.handle_play.bind(this),  false);
        this.video.addEventListener('pause', this.handle_pause.bind(this), false);

        // Define throttled event handlers for mouse wheel and mouse click
        var dt = 10;  // miliseconds
        var throttled_mouse_wheel = throttle(this.handle_mouse_wheel, dt, this);
        this.video.addEventListener('wheel', throttled_mouse_wheel);

        var throttled_mouse_click = throttle(this.handle_mouse_click, dt, this);
        this.video.addEventListener('click', throttled_mouse_click);

        // Keyboard events, enabled by setting tabindex attribute at start of this section
        // var throttled_keypress = throttle(this.handle_keypress, 50, this);
        // this.video.addEventListener('keypress', throttled_keypress);
        // didn't seem to work as expcted.....

        //-------------------------------------------------
        // Minor tweaks
        // Prevent page from scrolling with mouse wheel when hovering over video element
        this.video.onwheel = function(ev) {
            ev.preventDefault();
        };

        // Prevent context menu popup from right-click on video element
        this.video.oncontextmenu = function(ev) {
            ev.preventDefault();
        };

        return this;
    },

    //------------------------------------------------------------------------------------------
    // Functions defined below generally are called in response to changes in the backbone model.
    // Typical outcome is to make changes to some front-end components, or to make changes to other
    // model components.
    invoke_method: function() {
        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
        // stamp is a timestamp generated at back end.  Its used here to guarantee a unique data
        // Backbone event.
        var parts = this.model.get('_method');
        var name = parts[0];
        var stamp = parts[1];
        var args = parts[2];

        this.video[name](...args);
    },

    set_property: function() {
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

    current_time_changed: function() {
        // HTML5 video element responds to backbone model changes.
        // if (this.video.paused) {  // should no longer need this if test...
            // Only respond if not currently playing.
        this.video['currentTime'] = this.model.get('current_time');
        // }
    },

    play_pause_changed: function() {
        if (this.video.paused) {
            this.play();
        } else {
            this.pause();
        }
    },

    play: function() {
        // Start video playback, handled through backbone system.
        this.model.set('_method', ['play', Date.now(), '']);
        this.touch();
    },

    pause: function() {
        // Stop video playback, handled through backbone system.
        this.model.set('_method', ['pause', Date.now(), '']);
        this.touch();
    },

    //-------------------------------------------------------------------------------------------
    // The various handle_<something> functions are written to respond to front-end
    // JavaScript-generated events.  The usual outcome is either changing a parameter in the
    // backbone model or changing some other front-end component.
    handle_event: function(ev) {
        // General video-element event handler
        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
        var fields = ['clientHeight', 'clientWidth', 'controls', 'currentTime', 'currentSrc',
                      'duration', 'ended', 'muted', 'paused', 'playbackRate',
                      'readyState', 'seeking', 'videoHeight', 'videoWidth', 'volume'];

        var pev = {'type': ev.type};
        for (let f of fields) {
            pev[f] = ev.target[f];
        }
        this.model.set('_event', pev);

        // https://developer.mozilla.org/en-US/docs/Web/Events/timeupdate
        this.model.set('current_time', ev.target['currentTime']);
        this.touch();
    },

    fast_time_update: function() {
        this.model.set('current_time', this.video['currentTime']);
        this.touch();

        var delta_time_fast = 100;   // milliseconds
        if (this.enable_fast_time_update) {
            setTimeout(this.fast_time_update.bind(this), delta_time_fast);
        }
    },

    handle_play: function(ev) {
        // console.log(ev);
        // Don't respond to current_time events while playing. The video itself the source of those
        // events, and responding to them will only cause hard-to-debug timming trouble.
        this.stopListening(this.model, 'change:current_time');

        // Emit time updates in background at faster rate
        this.enable_fast_time_update = true;
        this.fast_time_update();
    },

    handle_pause: function(ev) {
        // Once no longer playing it is safe again to listen for current_time events.
        this.listenTo(this.model, 'change:current_time', this.current_time_changed);

        // Stop emitting time updates at faster rate
        this.enable_fast_time_update = false;
    },

    // handle_currentTime: function(ev) {
    //     var field = 'currentTime';
    //     this.model.set(field, ev.target[field]);
    //     this.touch();  // Must call this after any frontend modifications to Model data.
    // },

    // handle_keypress: function(ev) {
    //     console.log(ev);
    // },

    handle_mouse_wheel: function(ev) {
        // Scrubbing takes over from standard playback.
        this.video.pause();

        // Increment size
        // if ev.altKey
        // if ev.shiftKey
        var increment;  // seconds
        if (ev.ctrlKey) {
            // one second
            increment = 1;
        } else {
            // one frame, e.g. 1/30 or 1/60
            increment = this.model.get('timebase');
        }

        if (ev.deltaY > 0) {
            // Scrub forwards
            this.video.currentTime += increment;
        } else {
            // Scrub backwards
            this.video.currentTime -= increment;
        }
    },

    handle_mouse_click: function(ev) {
        this.play_pause_changed();
    },
});


//-----------------------------------------------

module.exports = {
    TimeCodeModel: TimeCodeModel,
    TimeCodeView: TimeCodeView,
    VideoModel: VideoModel,
    VideoView: VideoView
};
