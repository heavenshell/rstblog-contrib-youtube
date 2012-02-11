# -*- coding: utf-8 -*-
"""
    rstblog.modules.youtube
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module was inspired and ported from Sphinx's YouTube module.

    This module defines a directive, `youtube`.  It takes a single, required
    argument, a YouTube video ID::

    ..  youtube:: oHg5SJYRHA0

    The referenced video will be embedded into HTML output.  By default, the
    embedded video will be sized for 720p content.  To control this, the
    parameters "aspect", "width", and "height" may optionally be provided::

    ..  youtube:: oHg5SJYRHA0
        :width: 640
        :height: 480

    ..  youtube:: oHg5SJYRHA0
        :aspect: 4:3

    ..  youtube:: oHg5SJYRHA0
        :width: 100%

    ..  youtube:: oHg5SJYRHA0
        :height: 200px

    :copyright: (c) 2011 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import re
from docutils import nodes
from docutils.parsers.rst import Directive, directives

CONTROL_HEIGHT = 30


def get_size(d, key):
    if key not in d:
        return None
    m = re.match('(\d+)(|%|px)$', d[key])
    if not m:
        raise ValueError('invalid size %r' % d[key])
    return int(m.group(1)), m.group(2) or 'px'


def css(d):
    return '; '.join(sorted('%s: %s' % kv for kv in d.iteritems()))


def make_iframetag(id, aspect=None, width=None, height=None):
    body = []

    if aspect is None:
        aspect = 16, 9
    if (height is None) and (width is not None) and (width[1] == '%'):
        style = {
            'padding-top': '%dpx' % CONTROL_HEIGHT,
            'padding-bottom': '%f%%' % (width[0] * aspect[1] / aspect[0]),
            'width': '%d%s' % width,
            'position': 'relative',
        }
        body.append('<div style="%s>"' % css(style))
        style = {
            'position': 'absolute',
            'top': '0',
            'left': '0',
            'width': '100%',
            'height': '100%',
            'border': '0',
        }
        src = 'http://www.youtube.com/embed/%s' % id
        body.append('<iframe src="%s" style="%s">' % (src, css(style)))
        body.append('</iframe></div>')
    else:
        if width is None:
            if height is None:
                width = 560, 'px'
            else:
                width = height[0] * aspect[0] / aspect[1], 'px'
        if height is None:
            height = width[0] * aspect[1] / aspect[0], 'px'
        style = {
            'width': '%d%s' % width,
            'height': '%d%s' % (height[0] + CONTROL_HEIGHT, height[1]),
            'border': '0',
        }
        src = 'http://www.youtube.com/embed/%s' % id
        style = css(style)
        body.append('<iframe src="%s" style="%s">' % (src, style))
        body.append('</iframe>')

    return ''.join(body)


class YouTube(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'width': directives.unchanged,
        'height': directives.unchanged,
        'aspect': directives.unchanged
    }

    def run(self):
        if 'aspect' in self.options:
            aspect = self.options.get('aspect')
            m = re.match('(\d+):(\d+)', aspect)
            if m is None:
                raise ValueError('invalid aspect ratio %r' % aspect)
            aspect = tuple(int(x) for x in m.groups())
        else:
            aspect = None

        width = get_size(self.options, 'width')
        height = get_size(self.options, 'height')

        body = make_iframetag(id=self.arguments[0], aspect=aspect, \
                              width=width, height=height)

        return [nodes.raw('', body, format='html')]


def setup(builder):
    directives.register_directive('youtube', YouTube)
