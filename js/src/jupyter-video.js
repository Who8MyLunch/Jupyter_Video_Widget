var _ = require('lodash');

var widgets_base = require('@jupyter-widgets/base');
var widgets_controls = require('@jupyter-widgets/controls');

var module_name = require('../package.json').name;
var module_version = require('../package.json').version;


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

console.log(widgets_base);
console.log(widgets_controls);


var TimeCodeModel = widgets_controls.HTMLModel.extend({
    defaults: _.extend(_.result(this, 'widgets.HTMLModel.prototype.defaults'), {
        _model_name:          'TimeCodeModel',
        _model_module:         module_name,
        _model_module_version: module_version,

        _view_name:          'TimeCodeView',
        _view_module:         module_name,
        _view_module_version: module_version,
    })
});


var VideoModel = widgets_base.DOMWidgetModel.extend({
    defaults: _.extend(_.result(this, 'widgets.DOMWidgetModel.prototype.defaults'), {
        _model_name:          'VideoModel',
        _model_module:         module_name,
        _model_module_version: module_version,

        _view_name:          'VideoView',
        _view_module:         module_name,
        _view_module_version: module_version,
    })
});


//-----------------------------------------------

// Widget View renders the model to the DOM
var TimeCodeView = widgets_controls.HTMLView.extend({
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

        var html = `<p style="font-family:   DejaVu Sans Mono, Consolas, Monospace;'
                              font-variant:  normal;
                              font-weight:   bold;
                              font-style:    normal;
                              margin-left:   3pt;
                              margin-right:  3pt;
                              margin-top:    3pt;
                              margin-bottom: 3pt;
                              font-size:     11pt;
                              line-height:   13pt;
                              ">${time_string}</p>`;

        this.model.set('value', html);
        this.touch();
    },
});

//-----------------------------------------------
//-----------------------------------------------

var VideoView = widgets_base.DOMWidgetView.extend({
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
        // https://developer.mozilla.org/en-US/docs/Web/Reference/Events
        // https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
        this.video.addEventListener('durationchange', this.handle_event.bind(this));
        this.video.addEventListener('ended',          this.handle_event.bind(this));
        this.video.addEventListener('loadedmetadata', this.handle_event.bind(this));
        this.video.addEventListener('pause',          this.handle_event.bind(this));
        this.video.addEventListener('play',           this.handle_event.bind(this));
        this.video.addEventListener('playing',        this.handle_event.bind(this));
        this.video.addEventListener('ratechange',     this.handle_event.bind(this));
        this.video.addEventListener('seeked',         this.handle_event.bind(this));
        this.video.addEventListener('seeking',        this.handle_event.bind(this));
        this.video.addEventListener('timeupdate',     this.handle_event.bind(this));
        this.video.addEventListener('volumechange',   this.handle_event.bind(this));

        // Special handling for play and pause events
        this.enable_fast_time_update = false
        this.video.addEventListener('play',  this.handle_play.bind(this));
        this.video.addEventListener('pause', this.handle_pause.bind(this));

        // Define throttled event handlers for mouse wheel and mouse click
        var dt = 10;  // miliseconds
        var throttled_mouse_wheel = throttle(this.handle_mouse_wheel, dt, this);
        this.video.addEventListener('wheel', throttled_mouse_wheel);

        var throttled_mouse_click = throttle(this.handle_mouse_click, dt, this);
        this.video.addEventListener('click', throttled_mouse_click);

        //-------------------------------------------------
        // Handle keyboard event via containing div element.
        this.video.onloadedmetadata = function(ev) {
            // Parent element only knowable after DOM is rendered
            var container = ev.target.closest('div');
            container.tabIndex = 0

            function div_focus() {
                if (this.model.get('_enable_keyboard')) {
                    container.focus();
                };
            }

            container.addEventListener('mouseover', div_focus.bind(this));
            container.addEventListener('keydown', this.handle_keypress.bind(this));
        }.bind(this);

        //-------------------------------------------------
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

    jump_frames: function(num_frames) {
        // Jump fractional number of frames, positive or negative
        var dt_frame = this.model.get('timebase');

        this.jump_seconds(num_frames*dt_frame);
    },

    jump_seconds: function(dt_seconds) {
        // Jump fractional number of seconds, positive or negative
        if (!this.video.paused) {
            this.video.pause();
        }
        this.video.currentTime += dt_seconds;

        // if (paused) {
        //     this.video.play();
        // }
    },

    //-------------------------------------------------------------------------------------------
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
        // Don't respond to current_time events while playing. The video itself is the source of
        // those events, and responding to them will only cause hard-to-debug timming trouble.
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

    handle_keypress: function(ev) {
        if (this.model.get('_enable_keyboard')) {
            // console.log(ev.key)

            // 'altKey'
            // 'metaKey'
            // 'ctrlKey'
            ev.stopImmediatePropagation();
            ev.stopPropagation();
            ev.preventDefault();

            if (ev.key == ' ') {
                // space bar toggle play/pause
                this.play_pause_changed();
            } else if (ev.key == 'ArrowLeft') {
                if (ev.ctrlKey) {
                    this.jump_seconds(-1);
                } else {
                    this.jump_frames(-1);
                }
            } else if (ev.key == 'ArrowRight') {
                if (ev.ctrlKey) {
                    this.jump_seconds(1);
                } else {
                    this.jump_frames(1);
                }
            } else if (ev.key == 'ArrowUp') {
                // Increase play rate
                this.video.playbackRate *= 2.0;
            } else if (ev.key == 'ArrowDown') {
                // Increase play rate
                this.video.playbackRate /= 2.0;
            }
        }
    },

    handle_mouse_wheel: function(ev) {
        var increment;
        if (ev.deltaY < 0) {
            // Forwards
            increment = 1
        } else {
            // Backwards
            increment = -1
        }

        if (ev.ctrlKey) {
            // ctrl --> skip one second
            this.jump_seconds(increment);
        } else {
            // skip a single frame
            // e.g. 1/30 or 1/60 sec
            this.jump_frames(increment);
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
