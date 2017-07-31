
import ipywidgets


# <pre style="font-family:  DejaVu Sans Mono, Consolas, Lucida Console, Monospace;'
            # background-color: #f5f5f5;

_html_template = """
<pre style="font-family:      Monospace;'
            display:          block;
            white-space:      pre;
            font-variant:     normal;
            font-weight:      normal;
            font-style:       normal;
            font-size:        10pt;
            color:            #333333;
            background-color: #fff;
            margin:           0em 0;
            margin-left:      1pt;
            margin-right:     1pt;
            margin-top:       1pt;
            margin-bottom:    1pt;
            border:           0px solid #ccc;
            border-radius:    2px;
            ">
{content:s}
</pre>
"""

class MonoText(ipywidgets.HTML):
    """Monospace text version of ipywidget.Text widget
    """
    def __init__(self, text=None):
        super().__init__()
        self._text = ''
        self.text = text

    @property
    def text(self):
        """Widget's displayed text
        """
        return self._text

    @text.setter
    def text(self, list_or_string):
        if not list_or_string:
            return

        if isinstance(list_or_string, str):
            list_or_string = [list_or_string]

        if not isinstance(list_or_string, list):
            msg = 'Input item must be a string or list of strings: {}'.format(type(list_or_string))
            raise ValueError(msg)

        if not isinstance(list_or_string[0], str):
            msg = 'Input item(s) must be a string or list of strings: {}'.format(type(list_or_string[0]))
            raise ValueError(msg)

        self._text = '\n'.join(list_or_string)
        self._update()

    def _update(self):
        """Refresh displayed text
        """
        self.value = _html_template.format(content=self.text)

#------------------------------------------------

if __name__ == '__main__':
    pass
