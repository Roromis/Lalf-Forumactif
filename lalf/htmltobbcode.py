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

"""
Module handling the conversion of html to bbcode (as stored in the phpbb database)
"""

import logging
import re
from html.parser import HTMLParser
import base64
from urllib.parse import urlparse, urlunparse
from collections import namedtuple
from io import StringIO

from lalf.phpbb import BBCODES
from lalf.util import random_string

TAGS = {
    '*' : -1,
    'quote' : 0,
    'quote=' : 0,
    'b' : 1,
    'i' : 2,
    'url' : 3,
    'url=' : 3,
    'img' : 4,
    'size=' : 5,
    'color=' : 6,
    'u' : 7,
    'code' : 8,
    'list' : 9,
    'list=' : 9,
    'email' : 10,
    'email=' : 10,
    'flash=' : 11,
    'attachment' : 12}
for bbcode in BBCODES:
    TAGS[bbcode["bbcode_tag"]] = bbcode["bbcode_id"]

def escape(string):
    """
    Transform some characters in valid bbcodes

    Phpbb uses the same function (bbcode_specialchars in includes/message_parser.php)
    """
    replace = {
        '<': '&lt;',
        '>': '&gt;',
        '[': '&#91;',
        ']': '&#93;',
        '.': '&#46;',
        ':': '&#58;'
    }
    for key, value in replace.items():
        string = string.replace(key, value)
    return string

def process_link(bb, url):
    """
    Rewrite an internal link to make it point to the same page in the new forum
    """
    logger = logging.getLogger('lalf.htmltobbcode')

    scheme, netloc, path, params, query, fragment = urlparse(url)

    # Add domain name to relative links
    if scheme == "" and netloc == "":
        scheme = "http"
        netloc = bb.config["url"]
    url = urlunparse((scheme, netloc, path, params, query, fragment))

    # Rewrite internal links
    if bb.config["rewrite_links"] and netloc == bb.config["url"]:
        newurl = bb.linkrewriter.rewrite(url)
        if newurl:
            url = newurl
        else:
            logger.warning("Le lien suivant n'a pas pu être réécrit : %s", url)

    return url

class Node(object):
    """
    Node in the tree representation of a bbcode post

    Attrs:
        tag (str): The bbcode tag of this node (or None)
        parent (Node): The parent Node
        children (List(Node)): The children of this node
    """
    def __init__(self, tag=None):
        self.tag = tag
        self.parent = None
        self.children = []

    def add_text(self, text):
        """
        Add text inside the node
        """
        # Get the last child of the node
        try:
            last_child = self.children[-1]
        except IndexError:
            last_child = None

        # Check if it is a TextNode
        if isinstance(last_child, TextNode):
            last_child.text += text
        else:
            self.add_child(TextNode(text))

    def add_child(self, child):
        """
        Add a child
        """
        child.parent = self
        self.children.append(child)

    def get_bbcode(self, fileobj, bb, uid=""):
        """
        Write the bbcode corresponding to this node in a file object
        """
        for child in self.children:
            child.get_bbcode(fileobj, bb, uid)

    def get_bitfield(self, bitfield):
        """
        Get the bitifield of this node
        """
        if self.tag in TAGS and TAGS[self.tag] >= 0:
            c, d = divmod(TAGS[self.tag], 8)
            bitfield[c] |= (1 << (7-d))

        for child in self.children:
            child.get_bitfield(bitfield)

class TextNode(Node):
    """
    Node containing only text (no bbcode tags)
    """
    def __init__(self, text):
        Node.__init__(self)
        self.text = text

    def get_bbcode(self, fileobj, bb, uid=""):
        fileobj.write(self.text)

BBCodePost = namedtuple("BBCodePost", ("text", "uid", "bitfield"))

class Parser(HTMLParser):
    """
    Object used to parse html and generate bbcode
    """
    handlers = {}

    @classmethod
    def handler(cls, *tags):
        """
        Decorator adding a handler to the Parser class

        The function handling a certain tag is called when a start tag of this type is met.
        It should take two arguments :
           tag (str): The tag of the element
           attrs (Dict(str, str)): Dictionnary containing the attributes of the element

        And it should return a node or a string that will be added to the current node

        Args:
            *tags (List(str)): The tags handled by the handler
        """
        def decorator(handler):
            for tag in tags:
                cls.handlers[tag] = handler
            return handler
        return decorator

    def __init__(self, bb):
        HTMLParser.__init__(self)

        self.logger = logging.getLogger("{}.{}".format(self.__class__.__module__,
                                                       self.__class__.__name__))

        self.bb = bb

        self.root_node = Node()
        self.current_node = self.root_node
        self.stack = []

    def get_post(self, uid=None):
        """
        Get the post content

        Attrs:
            uid (Optionnal(str)): The bbcode uid (a 8-character string)
               if the uid is "", no uid will be used
               if the uid is None, a random uid will be generated

        Returns:
            BBCodePost: A named tuple with the following attributes:
                text (str): The post's content in bbcode
                uid (str)
                bitfield (str)
        """
        if uid is None:
            uid = random_string()
        actual_uid = uid

        if uid != "":
            uid = ":"+uid

        # Get the post's text
        fileobj = StringIO()
        self.root_node.get_bbcode(fileobj, self.bb, uid)
        text = fileobj.getvalue().rstrip("\n")
        fileobj.close()

        # Get the bitfield
        bitfield = [0] * 10
        self.root_node.get_bitfield(bitfield)
        bitfield = ''.join([chr(c) for c in bitfield]).rstrip('\0').encode("latin-1")
        bitfield = base64.b64encode(bitfield).decode("utf-8")

        return BBCodePost(text, actual_uid, bitfield)

    def handle_data(self, data):
        """
        Handle the text nodes

        In normal mode, add the data to the output.
        In capture mode, save the data.
        """
        self.current_node.add_text(data)

    def handle_starttag(self, tag, attrs):
        """
        Handle the start tag of an element
        """
        attrs = dict(attrs)
        attrs["class"] = attrs.get("class", None)
        attrs["style"] = attrs.get("style", "")

        # Get the handler for this tag, and call it
        # If it creates a node, set it as the current one and add True to the stack
        # (in order to be able to tell that a node was opened when the end tag of
        # this element is encountered)
        try:
            handler = self.__class__.handlers[tag]
        except KeyError:
            self.stack.append(False)
        else:
            node = handler(tag, attrs)
            if isinstance(node, Node):
                self.current_node.add_child(node)
                self.current_node = node
                self.stack.append(True)
            elif isinstance(node, str):
                self.current_node.add_text(node)
                self.stack.append(False)
            else:
                self.stack.append(False)

    def handle_endtag(self, tag):
        """
        Handle the end tag of an element
        """
        # Check if a node was opened at the start tag of this element, and close it
        if self.stack.pop():
            self.current_node = self.current_node.parent

class CaptureNode(Node):
    """
    Node used to capture text. Its content will not be rendered by the get_bbcode method.
    """
    def __init__(self):
        Node.__init__(self)
        self.text = ""

    def add_text(self, text):
        self.text += text

    def get_bbcode(self, fileobj, bb, uid=""):
        return

class SmileyNode(Node):
    """
    Node representing a smiley
    """
    def __init__(self, smiley_id):
        Node.__init__(self)
        self.smiley_id = smiley_id

    def get_bbcode(self, fileobj, bb, uid=""):
        try:
            smiley = bb.smilies[self.smiley_id]
        except KeyError:
            return

        if smiley["smiley_url"]:
            fileobj.write((
                "  <!-- s{code} -->"
                "<img src=\"{{SMILIES_PATH}}/{url}\" alt=\"{code}\" title=\"{title}\" />"
                "<!-- s{code} -->  "
            ).format(
                url=smiley["smiley_url"],
                code=smiley["code"],
                title=smiley["emotion"]))
        else:
            fileobj.write(" {code} ".format(**bb.smilies[self.smiley_id]))

class InlineTagNode(Node):
    """
    A node representing an inline element
    """
    def __init__(self, tag, attrs="", closing_tag=None, content=""):
        Node.__init__(self, tag)
        self.closing_tag = closing_tag
        self.attrs = attrs

        if content:
            self.add_text(content)

    def get_bbcode(self, fileobj, bb, uid=""):
        if self.tag not in TAGS:
            logger = logging.getLogger("lalf.htmltobbcode")
            logger.warning("La balise bbcode [%s] n'est pas supportée.", self.tag)

            Node.get_bbcode(self, fileobj, bb, uid)
        else:
            fileobj.write("[{}{}{}]".format(self.tag, self.attrs, uid))
            Node.get_bbcode(self, fileobj, bb, uid)
            if self.closing_tag:
                fileobj.write("[/{}{}]".format(self.closing_tag, uid))
            else:
                fileobj.write("[/{}{}]".format(self.tag.rstrip("="), uid))

#
# intial credit to Titou74
#       https://github.com/Roromis/Lalf-Forumactif/issues/56
# for Iframe
#
class IframeTagNode(Node):
    """
    A node representing an inline element
    """
    def __init__(self, tag, attrs="", closing_tag=None, content=""):
        Node.__init__(self, tag)
        self.closing_tag = closing_tag
        self.attrs = attrs
		
        if content:
            self.add_text(content)

    def get_bbcode(self, fileobj, bb, uid=""):
        if self.tag not in TAGS:
            logger = logging.getLogger('lalf.htmltobbcode')
            logger.warning("La balise bbcode [%s] n'est pas supportée.", self.tag)

            Node.get_bbcode(self, fileobj, bb, uid)
        else:
            fileobj.write("[{}{}{}]".format(self.tag, self.attrs, uid))
            Node.get_bbcode(self, fileobj, bb, uid)
            if self.closing_tag:
                fileobj.write("[/{}{}]".format(self.closing_tag, uid))
            else:
                fileobj.write("[/{}{}]".format(self.tag.rstrip("="), uid))


class BlockTagNode(InlineTagNode):
    """
    A node representing an block element
    """
    def get_bbcode(self, fileobj, bb, uid=""):
        InlineTagNode.get_bbcode(self, fileobj, bb, uid)
        fileobj.write("\n")

class CodeQuoteNode(BlockTagNode):
    """
    A node representing a code block or a quote block
    """
    def __init__(self):
        BlockTagNode.__init__(self, "quote")

    def get_bbcode(self, fileobj, bb, uid=""):
        try:
            node = self.children[0]
        except IndexError:
            node = None

        self.attrs = ""
        if isinstance(node, CaptureNode):
            if node.text[-9:] == " a écrit:":
                self.tag = "quote="
                self.attrs = "&quot;{}&quot;".format(node.text[:-9])
            elif node.text == "Code:":
                self.tag = "code"
                try:
                    child = self.children[0]
                except IndexError:
                    pass
                try:
                    child.text = escape(child.text)
                except AttributeError:
                    pass

        BlockTagNode.get_bbcode(self, fileobj, bb, uid)

class ItemNode(InlineTagNode):
    """
    Node representing a list item
    """
    def __init__(self):
        InlineTagNode.__init__(self, "*", closing_tag="*:m")

    def get_bbcode(self, fileobj, bb, uid=""):
        try:
            node = self.children[-1]
        except IndexError:
            node = None

        if isinstance(node, TextNode):
            i = len(node.text)
            while i > 0 and node.text[i-1] == "\n":
                i -= 1
            newlines = node.text[i:]
            node.text = node.text[:i]
        else:
            newlines = ""

        InlineTagNode.get_bbcode(self, fileobj, bb, uid)
        fileobj.write(newlines)

class EmailNode(InlineTagNode):
    """
    Node representing a email
    """
    def __init__(self, email):
        InlineTagNode.__init__(self, "email")
        self.email = email

    def get_bbcode(self, fileobj, bb, uid=""):
        try:
            text = self.children[0].text
        except (IndexError, AttributeError):
            text = None

        if len(self.children) > 1:
            text = None

        if text == self.email:
            self.tag = "email"
            self.children[0].text = escape(self.children[0].text)
        else:
            self.tag = "email="
            self.attrs = escape(self.email)
        InlineTagNode.get_bbcode(self, fileobj, bb, uid)

class UrlNode(InlineTagNode):
    """
    Node representing a url
    """
    def __init__(self, url, postlink):
        InlineTagNode.__init__(self, None)
        self.url = url
        self.postlink = postlink

    def get_bbcode(self, fileobj, bb, uid=""):
        try:
            text = self.children[0].text
        except (IndexError, AttributeError):
            text = None

        if len(self.children) > 1:
            text = None

        url = process_link(bb, self.url)

        if self.postlink or not text:
            # [url] tag
            if text == self.url:
                self.tag = "url"
                self.children = [TextNode(escape(url))]
            else:
                self.tag = "url="
                self.attrs = escape(url)
            InlineTagNode.get_bbcode(self, fileobj, bb, uid)
        else:
            # Magic url
            local = url.startswith(bb.config["phpbb_url"])
            if local:
                # Remove domain name and first forward slash
                ellipsized_url = url[len(bb.config["phpbb_url"])+1:]
            else:
                ellipsized_url = url

            if len(ellipsized_url) > 55:
                # Remove middle part of the url
                ellipsized_url = "{} ... {}".format(url[:39], url[-10:])

            if local:
                fileobj.write('<!-- l --><a class="postlink-local" href="{}">{}</a><!-- l -->'
                              .format(url, ellipsized_url))
            else:
                fileobj.write('<!-- m --><a class="postlink" href="{}">{}</a><!-- m -->'
                              .format(url, ellipsized_url))

#
# initial credit to Titou74
# https://github.com/Roromis/Lalf-Forumactif/issues/56
@Parser.handler("i", "u", "strike", "sub", "sup", "hr", "tr", "h2", "h3", "h4")
def _inline_handler(tag, attrs):
    return InlineTagNode(tag)

@Parser.handler("td")
def _td_handler(tag, attrs):
    logger = logging.getLogger('lalf.htmltobbcode')
    colspan = attrs.get("colspan", 1)
    rowspan = attrs.get("rowspan", 1)
    if colspan == 1 and rowspan == 1:
        return InlineTagNode("td")
    else:
        return InlineTagNode("td=", "{},{}".format(colspan, rowspan))


#
# intial credit to Titou74
#       https://github.com/Roromis/Lalf-Forumactif/issues/56
# for Iframe
@Parser.handler("iframe")
def _iframe_handler(tag, attrs):
    logger = logging.getLogger('lalf.htmltobbcode')
    if attrs["src"][:30] == "https://www.youtube.com/embed/":
        logger.warning(attrs["src"][30:len(attrs["src"])])
        return IframeTagNode("youtube", content=attrs["src"][30:len(attrs["src"])])
    if attrs["src"][:39] == "http://www.dailymotion.com/embed/video/":
        logger.warning(attrs["src"][39:len(attrs["src"])])
        return IframeTagNode("dailymotion", content=attrs["src"][39:len(attrs["src"])])
    return InlineTagNode(tag)

@Parser.handler("strong")
def _strong_handler(tag, attrs):
    return InlineTagNode("b")

@Parser.handler("table")
def _table_handler(tag, attrs):
    logger = logging.getLogger('lalf.htmltobbcode')
    if "border" in attrs:
        logger.warning('La propriété "border" du bbcode [table] n\'est pas supportée.')
    if "cellspacing" in attrs:
        logger.warning('La propriété "cellspacing" du bbcode [table] n\'est pas supportée.')
    if "cellpadding" in attrs:
        logger.warning('La propriété "cellpadding" du bbcode [table] n\'est pas supportée.')
    return BlockTagNode("table")

@Parser.handler("br")
def _br_handler(tag, attrs):
    return "\n"

@Parser.handler("ul")
def _ul_handler(tag, attrs):
    return InlineTagNode("list", closing_tag="list:u")

@Parser.handler("ol")
def _ol_handler(tag, attrs):
    return InlineTagNode("list=", attrs["type"], closing_tag="list:o")

@Parser.handler("li")
def _li_handler(tag, attrs):
    return ItemNode()

@Parser.handler("dt")
def _dt_handler(tag, attrs):
    # Get the quote author's name
    return CaptureNode()

@Parser.handler("dl")
def _dl_handler(tag, attrs):
    if "hidecode" in attrs["class"]:
        return BlockTagNode("hide")
    elif "spoiler" in attrs["class"]:
        return BlockTagNode("spoiler")
    else:
        return CodeQuoteNode()

@Parser.handler("dd")
def _dd_handler(tag, attrs):
    if attrs["class"] == "spoiler_closed":
        return CaptureNode()

@Parser.handler("a")
def _a_handler(tag, attrs):
    if "href" in attrs:
        if attrs["href"][:7] == "mailto:":
            return EmailNode(attrs["href"][7:])
        else:
            return UrlNode(attrs["href"], attrs["class"] == "postlink")

@Parser.handler("font")
def _font_handler(tag, attrs):
    if "color" in attrs:
        return InlineTagNode("color=", attrs["color"])
    elif "face" in attrs:
        return InlineTagNode("font=", attrs["face"])

@Parser.handler("span")
def _span_handler(tag, attrs):
    match = re.search('font-size: (\\d+)px', attrs["style"])
    if match:
        size = int(int(match.group(1)) * 100 / 12)
        return InlineTagNode("size=", size)

@Parser.handler("div")
def _div_handler(tag, attrs):
    if "align" in attrs:
        return BlockTagNode(attrs["align"])

@Parser.handler("img")
def _img_handler(tag, attrs):
    if "longdesc" in attrs:
        return SmileyNode(attrs["longdesc"])
    elif "src" in attrs:
        return InlineTagNode("img", content=escape(attrs["src"]))

@Parser.handler("embed")
def _embed_handler(tag, attrs):
    if "width" in attrs and "height" in attrs and "src" in attrs:
        return InlineTagNode("flash=", "{width},{height}".format(**attrs),
                             content=escape(attrs["src"]))

@Parser.handler("marquee")
def _marquee_handler(tag, attrs):
    if "direction" in attrs and attrs["direction"] == "up":
        return InlineTagNode("updown")
    else:
        return InlineTagNode("scroll")
       
