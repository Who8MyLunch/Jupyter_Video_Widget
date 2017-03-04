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
        url: 'Hello World, eh?'

    })
});


// Custom Widget View renders the widget model.

// https://www.html5rocks.com/en/tutorials/video/basics/
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
// https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Video_and_audio_content
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_manipulation

// Video player styling
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/Video_player_styling_basics

// Good stuff implementing custom video player
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/cross_browser_video_player

// Media buffering and seeking, nice example displaying time ranges where video is loaded
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/buffering_seeking_time_ranges

// Rate playback explained
// https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/WebAudio_playbackRate_explained
var VideoView = widgets.DOMWidgetView.extend({

    render: function() {
        // This project's view is quite simple: just a single <video/> element.
        console.log('render');

        this.video = document.createElement('video');
        this.video.controls = true;
        this.video.preload = 'auto';
        this.video.autoplay = false;
        console.log(this.video);

        this.url_changed();
        this.model.on('change:url', this.url_changed, this);
    },

    url_changed: function() {
        console.log('url_changed: ' + this.model.get('url'));

        this.video.src = this.model.get('url');
    },

    // Video methods
    play: function() {
        this.video.play();
    },

    pause: function() {
        this.video.pause();
    },

    // Video events
    // https://developer.mozilla.org/en-US/docs/Web/Guide/Events/Media_events
    // primary: progress,playing, play, seeking, seeked,timeupdate
    // secondary:  loadeddata, stalled, waiting, suspend,

    /////////////////////////////////////////
    // JavaScript --> Python
    // Tell Backbone how to respond to JavaScript-generated events
    // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement
    // https://developer.mozilla.org/en-US/docs/Web/Guide/Events/Media_events
    // events: {
    //     play: 'handle_event',
    //     playing: 'handle_event',
    //     pause: 'handle_event',
    // },

    // handle_event: function(ev) {
    //     console.log(ev);
    // }
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
