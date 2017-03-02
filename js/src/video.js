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


// Custom View. Renders the widget model.

// https://www.html5rocks.com/en/tutorials/video/basics/
// https://html.spec.whatwg.org/#the-video-element
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/playbackRate
// https://www.w3schools.com/tags/ref_av_dom.asp

var VideoView = widgets.DOMWidgetView.extend({
    video: HTMLVideoElement,

    render: function() {
        console.log('render');
        // This project's view is quite simple: just a single <video/> element.
        // this.setElement('<video />');
        // console.log(this.el);
        // this.video = this.el;
        console.log(this.video);
        console.log('sdfsdfZZZ');

        this.url_changed();
        // this.model.on('change:url', this.url_changed, this);
    },

    url_changed: function() {
        console.log('url_changed');
        console.log(this.model.get('url'));
        this.video.src = this.model.get('url');
    },

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
