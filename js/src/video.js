var widgets = require('jupyter-js-widgets');
var _ = require('underscore');


// Custom Model. Custom widgets models must at least provide default values
// for model attributes when different from the base class.  These include `_model_name`,
// `_view_name`, `_model_module`, and `_view_module` .
//
// When serialiazing entire widget state for embedding, only values different from the
// defaults will be specified.
var HelloModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend({}, widgets.DOMWidgetModel.prototype.defaults, {
        _model_name : 'VideoModel',
        _view_name : 'VideoView',
        _model_module : 'jupyter_video_widget',
        _view_module : 'jupyter_video_widget',
        url : 'Hello World'
    })
});


// Custom View. Renders the widget model.
var VideoView = widgets.DOMWidgetView.extend({
    render: function() {
        this.value_changed();
        this.model.on('change:url', this.url_changed, this);
    },

    url_changed: function() {
        this.el.textContent = this.model.get('url');
    }
});


module.exports = {
    VideoModel : VideoModel,
    VideoView : VideoView
};
