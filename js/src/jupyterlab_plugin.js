var jupyter_video = require('./index');

var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'jupyter.extensions.jupyter-video',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'jupyter-video',
          version: jupyter_video.version,
          exports: jupyter_video
      });
  },
  autoStart: true
};
