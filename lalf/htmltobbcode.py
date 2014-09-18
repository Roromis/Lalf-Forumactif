# -*- coding: utf-8 -*-
#
# This file is part of Lalf.
#
# Lalf is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lalf.  If not, see <http://www.gnu.org/licenses/>.

import re
from html import escape
from html.parser import HTMLParser


class HtmltobbcodeParser(HTMLParser):
    def __init__(self, smileys):
        HTMLParser.__init__(self)
        self.smileys = smileys
        self.bbcode = ""
        self.quote = False
        self.author = ""
        self.span = []
        self.div = []
        self.font = []
        self.table = []
        self.li = []
        self.tr = []
        self.td = []
        self.dd = []
        self.a = []
        self.marquee = []

    def handle_data(self, data):
        if self.quote:
            if data[-9:] == " a écrit:":
                self.author = data[:-9]
            self.quote = False
        else:
            self.bbcode += data

    def handle_startendtag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'br':
            self.bbcode += "\n"
        elif tag == 'img':
            if "longdesc" in attrs:
                if attrs["longdesc"] in self.smileys:
                    self.bbcode += " " + self.smileys[attrs["longdesc"]] + " "
            elif "src" in attrs:
                self.bbcode += "[img]" + escape(attrs["src"]) + "[/img]"
        elif tag == 'hr':
            self.bbcode += "[hr][/hr]"


    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'strong':
            self.bbcode += "[b]"
        elif tag == 'i':
            self.bbcode += "[i]"
        elif tag == 'u':
            self.bbcode += "[u]"
        elif tag == "b":
            self.quote = True
            self.author = ""
        elif tag == 'a':
            if "class" in attrs:
                if attrs["class"] == "postlink":
                    if "href" in attrs:
                        self.bbcode += "[url=" + escape(attrs["href"]) + "]"
                        self.a.append("[/url]")
                    else:
                        self.a.append("")
                else:
                    self.a.append("")
            elif "href" in attrs:
                if attrs["href"][:7] == "mailto:":
                    self.bbcode += "[email=" + escape(attrs["href"][7:]) + "]"
                    self.a.append("[/email]")
                else:
                    self.a.append("")
            else:
                self.a.append("")
        elif tag == 'strike':
            self.bbcode += "[strike]"
        elif tag == 'font':
            if "color" in attrs:
                self.bbcode += "[color=" + attrs["color"] + "]"
                self.font.append("[/color]")
            elif "face" in attrs:
                self.bbcode += "[font=" + attrs["face"] + "]"
                self.font.append("[/font]")
            else:
                self.font.append("")
        elif tag == 'span':
            if "style" in attrs:
                size = re.search('font-size: (\d*)px', attrs["style"])
                if size:
                    self.bbcode += "[size=" + str(int(int(size.group(1)) * 100 / 12)) + "]"
                    self.span.append("[/size]")
                else:
                    self.span.append("")
            else:
                self.span.append("")
        elif tag == 'div':
            if "align" in attrs:
                self.bbcode += "[" + attrs["align"] + "]"
                self.div.append("[/" + attrs["align"] + "]\n")
            elif "style" in attrs:
                if "text-align:center" in attrs["style"]:
                    self.bbcode += "[center]"
                    self.div.append("[/center]\n")
                else:
                    self.div.append("")
            elif "class" in attrs:
                if attrs["class"] == "spoiler_content hidden":
                    self.bbcode += "[spoiler]"
                    self.div.append("[/spoiler]\n")
                else:
                    self.div.append("")
            else:
                self.div.append("")
        elif tag == 'ul':
            self.bbcode += "[list]"
        elif tag == 'ol' and "type" in attrs:
            self.bbcode += "[list=" + attrs["type"] + "]"
        elif tag == 'li':
            self.bbcode += "[*]"
            self.li.append("[/*:m]")
        elif tag == 'table':
            if not ("cellspacing" in attrs and "cellpadding" in attrs and "border" in attrs and "align" in attrs and "width" in attrs):
                args = ""
                if "border" in attrs:
                    args += " border=" + attrs["border"]
                if "cellspacing" in attrs:
                    args += " cellspacing=" + attrs["cellspacing"]
                if "cellpadding" in attrs:
                    args += " cellpadding=" + attrs["cellpadding"]
                self.bbcode += "[table" + args + "]"
                self.table.append("[/table]\n")
            else:
                self.table.append("")
        elif tag == 'tr':
            if self.table[len(self.table) - 1] == "[/table]":
                self.bbcode += "[tr]"
                self.tr.append("[/tr]")
            else:
                self.tr.append("")
        elif tag == 'dd':
            if "class" in attrs:
                if attrs["class"] == "quote":
                    if self.author != "":
                        self.bbcode += "[quote=&quot;" + escape(self.author) + "&quot;]"
                    else:
                        self.bbcode += "[quote]"
                    self.dd.append("[/quote]\n")
                elif attrs["class"] == "code":
                    self.bbcode += "[code]"
                    self.dd.append("[/code]\n")
                else:
                    self.dd.append("")
            else:
                self.dd.append("")
        elif tag == 'td':
            if self.table[len(self.table) - 1] == "[/table]":
                self.bbcode += "[td]"
                self.td.append("[/td]")
            else:
                self.td.append("")
        elif tag == 'embed':
            if "width" in attrs and "height" in attrs and "src" in attrs:
                self.bbcode += "[flash=" + attrs["width"] + "," + attrs["height"] + "]" + escape(attrs["src"]) + "[/flash]"
        elif tag == 'marquee':
            if "direction" in attrs:
                if attrs["direction"] == "up":
                    self.bbcode += "[updown]"
                    self.marquee.append("[/updown]")
                else:
                    self.bbcode += "[scroll]"
                    self.marquee.append("[/scroll]")
            else:
                self.bbcode += "[scroll]"
                self.marquee.append("[/scroll]")
        elif tag == "sub":
            self.bbcode += "[sub]"
        elif tag == "sup":
            self.bbcode += "[sup]"

    def handle_endtag(self, tag):
        if tag == 'strong':
            self.bbcode += "[/b]"
        elif tag == 'i':
            self.bbcode += "[/i]"
        elif tag == 'u':
            self.bbcode += "[/u]"
        elif tag == "b":
            self.quote = False
        elif tag == 'a':
            self.bbcode += self.a.pop()
        elif tag == 'strike':
            self.bbcode += "[/strike]"
        elif tag == 'font':
            self.bbcode += self.font.pop()
        elif tag == 'span':
            self.bbcode += self.span.pop()
        elif tag == 'div':
            self.bbcode += self.div.pop()
        elif tag == 'ul':
            self.bbcode = self.bbcode.rstrip("\n")
            self.bbcode += "[/list:u]"
        elif tag == 'ol':
            self.bbcode = self.bbcode.rstrip("\n")
            self.bbcode += "[/list:o]"
        elif tag == 'li':
            if self.bbcode.endswith("\n"):
                self.bbcode = self.bbcode.rstrip("\n")
                self.bbcode += self.li.pop() + "\n"
            else:
                self.bbcode += self.li.pop()
        elif tag == 'table':
            self.bbcode += self.table.pop()
        elif tag == 'td':
            self.bbcode += self.td.pop()
        elif tag == 'dd':
            self.bbcode += self.dd.pop()
        elif tag == 'tr':
            self.bbcode += self.tr.pop()
        elif tag == 'marquee':
            self.bbcode += self.marquee.pop()
        elif tag == "sub":
            self.bbcode += "[/sub]"
        elif tag == "sup":
            self.bbcode += "[/sup]"


def htmltobbcode(string, smileys):
    p = HtmltobbcodeParser(smileys)
    p.feed(string)

    return p.bbcode
