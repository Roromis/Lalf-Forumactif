# -*- coding: utf-8 -*-
#
# This file is part of Lalf.
#
# Lalf is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lalf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lalf.  If not, see <http://www.gnu.org/licenses/>.

import logging
logger = logging.getLogger("lalf")

import re
from html import escape
from html.parser import HTMLParser
import base64
import hashlib

from lalf.phpbb import bbcodes

class Handler(object):
    def start(self, parser, stack, args):
        return

    def end(self, parser, stack):
        return

    def startend(self, parser, stack, args):
        return

class StackHandler(Handler):
    def __init__(self):
        self.stack = []

    def end(self, parser, stack):
        parser.append_tag(self.stack.pop())

class Parser(HTMLParser):
    handlers = {}

    @classmethod
    def handler(cls, *tags):
        def class_rebuilder(handler_class):
            handler = handler_class()
            for tag in tags:
                cls.handlers[tag] = handler
            return handler_class
        return class_rebuilder

    @classmethod
    def unsupported(cls, **props):
        def method_rebuilder(method):
            def new_method(self, parser, tag, attrs):
                if tag in props:
                    for prop in props[tag]:
                        if prop in attrs:
                            logger.warning('La propriété "%s" du bbcode [%s] n\'est pas supportée.',
                                           prop, tag)

                method(self, parser, tag, attrs)
            return new_method
        return method_rebuilder

    def __init__(self, smilies, uid):
        HTMLParser.__init__(self)

        self.smilies = smilies

        if uid:
            self.uid = ":{}".format(uid)
        else:
            self.uid = ""

        self.output = ""
        self.bitfield = [0] * 10

        self.tags = {'code' : 8,
                'quote' : 0,
                'attachment' : 12,
                'b' : 1,
                'i' : 2,
                'url' : 3,
                'img' : 4,
                'size' : 5,
                'color' : 6,
                'u' : 7,
                'list' : 9,
                'email' : 10,
                'flash' : 11}
        for b in bbcodes:
            self.tags[b["bbcode_tag"]] = b["bbcode_id"]

        self.capture_data = False
        self.data = ""

    def get_bitfield(self):
        tempstr = ''.join([chr(c) for c in self.bitfield]).rstrip('\0').encode("latin-1")
        return base64.b64encode(tempstr).decode("utf-8")

    def get_checksum(self):
        return hashlib.md5(self.output.encode("utf8")).hexdigest()

    def append_text(self, text):
        self.output += text

    def append_tag(self, tag, options=""):
        if tag:
            if tag in self.tags:
                c, d = divmod(self.tags[tag], 8)
                self.bitfield[c] |= (1 << (7-d))
            self.append_text("[{}{}{}]".format(tag, options, self.uid))

    def rstrip(self):
        i = len(self.output)
        while self.output[i-1] == "\n":
            i -= 1
        newlines = self.output[i:]
        self.output = self.output[:i]
        return newlines

    def start_capture(self):
        self.data = ""
        self.capture_data = True

    def end_capture(self):
        self.capture_data = False
        data = self.data
        self.data = ""
        return data

    def handle_data(self, data):
        if self.capture_data:
            self.data += data
        else:
            self.append_text(data)

    def handle_startendtag(self, tag, attrs):
        try:
            handler = self.__class__.handlers[tag]
        except KeyError:
            pass
        else:
            handler.startend(self, tag, dict(attrs))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        attrs["class"] = attrs.get("class", None)
        attrs["style"] = attrs.get("style", "")

        try:
            handler = self.__class__.handlers[tag]
        except KeyError:
            pass
        else:
            handler.start(self, tag, attrs)

    def handle_endtag(self, tag):
        try:
            handler = self.__class__.handlers[tag]
        except KeyError:
            pass
        else:
            handler.end(self, tag)

@Parser.handler("i", "u", "strike", "sub", "sup", "tr", "hr", "tr", "td")
class InlineHandler(Handler):
    @Parser.unsupported(td=["colspan", "rowspan"])
    def start(self, parser, tag, attrs):
        parser.append_tag(tag)

    def end(self, parser, tag):
        parser.append_tag("/{}".format(tag))

    def startend(self, parser, tag, attrs):
        parser.append_tag(tag)
        parser.append_tag("/{}".format(tag))

@Parser.handler("strong")
class StrongHandler(Handler):
    def start(self, parser, tag, attrs):
        parser.append_tag("b")

    def end(self, parser, tag):
        parser.append_tag("/b")

@Parser.handler("table")
class TableHandler(Handler):
    @Parser.unsupported(table=["border", "cellspacing", "cellpadding"])
    def start(self, parser, tag, attrs):
        parser.append_tag("table")

    def end(self, parser, tag):
        parser.append_tag("/table")
        parser.append_text("\n")

@Parser.handler("br")
class NewlineHandler(Handler):
    def startend(self, parser, tag, attrs):
        parser.append_text("\n")

@Parser.handler("ul", "ol", "li")
class ListHandler(Handler):
    def start(self, parser, tag, attrs):
        if tag == "ul":
            parser.append_tag("list")
        elif tag == "ol":
            parser.append_tag("list", "="+attrs["type"])
        elif tag == "li":
            parser.append_tag("*")

    def end(self, parser, tag):
        if tag == "ul":
            newlines = parser.rstrip()
            parser.append_tag("/list:u")
        elif tag == "ol":
            newlines = parser.rstrip()
            parser.append_tag("/list:o")
        elif tag == "li":
            newlines = parser.rstrip()
            parser.append_tag("/*:m")
            parser.append_text(newlines)

@Parser.handler("dl", "dt", "dd")
class BoxHandler(Handler):
    def __init__(self):
        self.author = ""
        self.stack = []

    def start(self, parser, tag, attrs):
        if tag == "dl":
            if "hidecode" in attrs["class"]:
                logger.warning("La balise [hide] n'est pas supportée.")
                self.stack.append(None)
            elif "spoiler" in attrs["class"]:
                parser.append_tag("spoiler")
                self.stack.append("/spoiler")
            else:
                self.stack.append(None)
        elif tag == "dt":
            parser.start_capture()
        elif tag == "dd":
            if attrs["class"] == "quote":
                if self.author:
                    parser.append_tag("quote", "=&quot;{}&quot;".format(escape(self.author)))
                    self.author = ""
                else:
                    parser.append_tag("quote")
                self.stack.append("/quote")
            elif attrs["class"] == "code":
                parser.append_tag("code")
                self.stack.append("/code")
            elif attrs["class"] == "spoiler_closed":
                parser.start_capture()
                self.stack.append(None)
            else:
                self.stack.append(None)

    def end(self, parser, tag):
        data = parser.end_capture()
        if tag == "dt":
            if data[-9:] == " a écrit:":
                self.author = data[:-9]
        else:
            tag = self.stack.pop()
            if tag:
                parser.append_tag(tag)
                parser.append_text("\n")

@Parser.handler("a")
class LinkHandler(Handler):
    def __init__(self):
        self.stack = []

    def start(self, parser, tag, attrs):
        if attrs["class"] == "postlink" and "href" in attrs:
            parser.append_tag("url", "={}".format(escape(attrs["href"])))
            self.stack.append("/url")
        elif "href" in attrs and attrs["href"][:7] == "mailto:":
            parser.append_tag("email", "={}".format(escape(attrs["href"][7:])))
            self.stack.append("/email")
        elif "href" in attrs:
            url = attrs["href"]
            # TODO : add domain
            if len(url) <= 55:
                ellipsized_url = url
            else:
                ellipsized_url = "{} ... {}".format(url[:39], url[-10:])
            parser.append_text('<!-- m --><a class="postlink" href="{}">{}</a><!-- m -->'
                               .format(url, ellipsized_url))
            parser.start_capture()
            self.stack.append(None)
        else:
            self.stack.append(None)

    def end(self, parser, tag):
        parser.end_capture()
        parser.append_tag(self.stack.pop())

@Parser.handler("font")
class FontHandler(StackHandler):
    def start(self, parser, tag, attrs):
        if "color" in attrs:
            parser.append_tag("color", "={}".format(attrs["color"]))
            self.stack.append("/color")
        elif "face" in attrs:
            parser.append_tag("font", "={}".format(attrs["face"]))
            self.stack.append("/font")
        else:
            self.stack.append(None)


@Parser.handler("span")
class SizeHandler(StackHandler):
    def start(self, parser, tag, attrs):
        match = re.search('font-size: (\\d+)px', attrs["style"])
        if match:
            size = int(int(match.group(1)) * 100 / 12)
            parser.append_tag("size", "={}".format(size))
            self.stack.append("/size")
        else:
            self.stack.append(None)

@Parser.handler("div")
class AlignHandler(StackHandler):
    def start(self, parser, tag, attrs):
        if "align" in attrs:
            parser.append_tag(attrs["align"])
            self.stack.append("/{}".format(attrs["align"]))
        elif "text-align:center" in attrs["style"]:
            parser.append_tag("center")
            self.stack.append("/center")
        else:
            self.stack.append(None)

    def end(self, parser, stack):
        tag = self.stack.pop()
        if tag:
            parser.append_tag(tag)
            parser.append_text("\n")

@Parser.handler("img")
class ImageHandler(Handler):
    def startend(self, parser, tag, attrs):
        if "longdesc" in attrs:
            if attrs["longdesc"] in parser.smilies:
                if parser.smilies[attrs["longdesc"]]["smiley_url"]:
                    parser.append_text("  <!-- s{code} --><img src=\"{{SMILIES_PATH}}/{smiley_url}\" alt=\"{code}\" title=\"{emotion}\" /><!-- s{code} -->  ".format(**parser.smilies[attrs["longdesc"]]))
                else:
                    parser.append_text(" {code} ".format(**parser.smilies[attrs["longdesc"]]))
        elif "src" in attrs:
            parser.append_tag("img")
            parser.append_text(escape(attrs["src"]))
            parser.append_tag("/img")

@Parser.handler("embed")
class FlashHandler(Handler):
    def start(self, parser, tag, attrs):
        if "width" in attrs and "height" in attrs and "src" in attrs:
            parser.append_tag("flash", "={},{}".format(attrs["width"], attrs["height"]))
            parser.append_text(escape(attrs["src"]))
            parser.append_tag("/flash")

    def end(self, parser, tag):
        pass

@Parser.handler("marquee")
class MarqueeHandler(StackHandler):
    def start(self, parser, tag, attrs):
        if "direction" in attrs and attrs["direction"] == "up":
            parser.append_tag("updown")
            self.stack.append("/updown")
        else:
            parser.append_tag("scroll")
            self.stack.append("/scroll")
