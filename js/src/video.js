var widgets = require('jupyter-js-widgets');
var _ = require('underscore');


// Custom Model. Custom widgets models must at least provide default values
// for model attributes when different from the base class.  These include `_model_name`,
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
        url: 'Hello World'
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

// Rate playback explained
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/WebAudio_playbackRate_explained
var VideoView = widgets.DOMWidgetView.extend({

    render: function() {
        // This project's view is quite simple: just a single <video/> element.
        console.log('render');

        this.video = document.createElement('video');
        this.setElement(this.video);

        this.video.controls = true;
        this.video.preload = 'auto';
        this.video.autoplay = false;

        // this.video.addEventListener('loadedmetadata', function (e) {
        //     var width = this.videoWidth;
        //     var height = this.videoHeight;
        //     console.log(this);
        //     console.log(e);
        //     console.log(width, height);
        // }, false);

        this.url_changed();
        this.model.on('change:url', this.url_changed, this);
        this.model.on('change:_method', this.invoke_method, this);
        this.model.on('change:_property', this.set_property, this);
    },

    url_changed: function() {
        console.log('url_changed: ' + this.model.get('url'));
        this.video.src = this.model.get('url');
    },

    invoke_method: function() {
        // Invoke method on video element.
        var parts = this.model.get('_method');
        console.log('parts: ', parts);
        var name = parts[0];
        var args = parts[1];

        this.video[name](...args);
    },

    set_property: function() {
        // Set property value
        var parts = this.model.get('_property');
        console.log('parts: ', parts);
        var name = parts[0];
        var value = parts[1];

        this.video[name] = value;
    },

    // Video events
    // https://developer.mozilla.org/en-US/docs/Web/Guide/Events/Media_events
    // metadata: progress, loadeddata, ratechange, stalled, canplaythrough

    // Event handlers
    events: {
        ended: 'handle_event',
        pause: 'handle_event',
        play: 'handle_event',
        playing: 'handle_event',
        seeked: 'handle_event',
        timeupdate: 'handle_event',
        volumechange: 'handle_event',

        canplaythrough: 'handle_event',
        loadedmetadata: 'handle_event',
        progress: 'handle_event',
        ratechange: 'handle_event',
        stalled: 'handle_event',
    },

    handle_event: function(ev) {
        console.log(ev.type);
        console.log(ev);

        // Build simple structure to send back to Python backend
        var pev = {type: ev.type}

        // event-specific information
        if (ev.type == 'loadeddata') {
            // Video info
        } else if (ev.type == 'progress') {
            // Timing info

        }


        this.model.set('_property', ev)
        this.touch(); // Must call after any modifications to Backbone Model data.


    }

    // handle_playing: function(ev) {
    //     console.log(ev);
    // }
    // handle_pause: function(ev) {
    //     console.log(ev);
    // }


});

module.exports = {
    VideoModel: VideoModel,
    VideoView: VideoView
};
