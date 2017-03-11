var widgets = require('jupyter-js-widgets');
var _ = require('underscore');


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
        _method: [],
        _property: [],
        _event: {},
    })
});


// Custom Widget View renders the widget model.

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
var VideoView = widgets.DOMWidgetView.extend({

    render: function() {
        // This project's view is quite simple: just a single <video/> element.
        this.video = document.createElement('video');
        this.setElement(this.video);

        this.video.controls = true;
        this.video.preload = 'auto';
        this.video.autoplay = false;

        this.src_changed();
        this.model.on('change:src', this.src_changed, this);
        this.model.on('change:currentTime', this.currentTime_changed, this);
        this.model.on('change:_method', this.invoke_method, this);
        this.model.on('change:_property', this.set_property, this);
    },

    invoke_method: function() {
        // Invoke method on video element
        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
        var parts = this.model.get('_method');

        var name = parts[0];
        var args = parts[1];

        this.video[name](...args);
    },

    set_property: function() {
        // Set property value on video element
        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
        var parts = this.model.get('_property');

        var name = parts[0];
        var value = parts[1];

        this.video[name] = value;
    },

    src_changed: function() {
        var field = 'src';
        this.video[field] = this.model.get(field);
    },

    currentTime_changed: function() {
        var field = 'currentTime';
        this.video[field] = this.model.get(field);
    },

    // Event handlers
    // https://developer.mozilla.org/en-US/docs/Web/Guide/Events/Media_events
    events: {
        // State information
        durationchange: 'handle_event',
        ended: 'handle_event',
        loadedmetadata: 'handle_event',
        pause: 'handle_event',
        play: 'handle_event',
        playing: 'handle_event',
        ratechange: 'handle_event',
        seeked: 'handle_event',
        seeking: 'handle_event',
        volumechange: 'handle_event',

        // Timeline information
        timeupdate: 'handle_currentTime',
    },

    handle_event: function(ev) {
        // Generic event handler
        if (this.model.get('_handlers_active')) {
            // Gather information
            // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
            var fields = ['autoplay', 'clientHeight', 'clientWidth', 'controls',
                          'duration', 'ended', 'loop', 'muted', 'paused', 'playbackRate',
                          'seeking', 'videoHeight', 'videoWidth', 'volume']

            var pev = {'type': ev.type,
                       'timeStamp': ev.timeStamp};

            for (let f of fields) {
                pev[f] = ev.target[f];
            }

            this.model.set('_event', pev)
            this.touch();  // Must call after any modifications to Model data.
        }
    },

    handle_currentTime: function(ev) {
        this.model.set('currentTime', ev.target.currentTime);
        this.touch();
    },

});

module.exports = {
    VideoModel: VideoModel,
    VideoView: VideoView
};
