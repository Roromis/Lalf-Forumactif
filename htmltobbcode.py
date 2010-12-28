#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       htmltobbcode.py
#       
#       Copyright 2010 Roromis <admin@roromis.fr.nf>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import re, HTMLParser

class HtmltobbcodeParser(HTMLParser.HTMLParser):
	def __init__(self, smileys):
		HTMLParser.HTMLParser.__init__(self)
		self.smileys = smileys
		self.bbcode = ""
		self.quote = False
		self.author = ""
		self.span = []
		self.div = []
		self.font = []
		self.table = []
		self.tr = []
		self.td = []
		self.a = []
		self.marquee = []
	
	def handle_data(self, data):
		if self.quote:
			if data[-9:] == u" a écrit:":
				self.author = data[:-9]
			self.quote = False
		else:
			self.bbcode += data
	
	def handle_startendtag(self, tag, attrs):
		attrs = dict(attrs)
		if tag=='br':
			self.bbcode += "\n"
		elif tag=='img':
			if attrs.has_key("longdesc"):
				if self.smileys.has_key(attrs["longdesc"]):
					self.bbcode += " " + self.smileys[attrs["longdesc"]] + " "
			elif attrs.has_key("src"):
				self.bbcode += "[img:<UID>]" + attrs["src"] + "[/img:<UID>]"
		elif tag=='hr':
			self.bbcode += "[hr:<UID>][/hr:<UID>]"
				
	
	def handle_starttag(self, tag, attrs):
		attrs = dict(attrs)
		if tag=='strong':
			self.bbcode += "[b:<UID>]"
		elif tag=='i':
			self.bbcode += "[i:<UID>]"
		elif tag=='u':
			self.bbcode += "[u:<UID>]"
		elif tag=="b":
			self.quote=True
			self.author=""
		elif tag=='a':
			if attrs.has_key("class"):
				if attrs["class"] == "postlink":
					if attrs.has_key("href"):
						self.bbcode += "[url=" + attrs["href"] + ":<UID>]"
						self.a.append("[/url:<UID>]")
					else:
						self.a.append("")
				else:
					self.a.append("")
			elif attrs.has_key("href"):
				if attrs["href"][:7] == "mailto:":
					self.bbcode += "[email=" + attrs["href"][7:] + ":<UID>]"
					self.a.append("[/email:<UID>]")
				else:
					self.a.append("")
			else:
				self.a.append("")
		elif tag=='strike':
			self.bbcode += "[strike:<UID>]"
		elif tag=='font':
			if attrs.has_key("color"):
				self.bbcode += "[color=" + attrs["color"] + ":<UID>]"
				self.font.append("[/color:<UID>]")
			elif attrs.has_key("face"):
				self.bbcode += "[font=" + attrs["face"] + ":<UID>]"
				self.font.append("[/font:<UID>]")
			else:
				self.font.append("")
		elif tag=='span':
			if attrs.has_key("style"):
				size = re.search('font-size: (\d*)px',attrs["style"])
				if size != None:
					self.bbcode += "[size=" + str(int(int(size.group(1))*100/12)) + ":<UID>]"
					self.span.append("[/size:<UID>]")
				else:
					self.span.append("")
			else:
				self.span.append("")
		elif tag=='div':
			if attrs.has_key("align"):
				self.bbcode += "[" + attrs["align"] + ":<UID>]"
				self.div.append("[/" + attrs["align"] + ":<UID>]")
			elif attrs.has_key("style"):
				if "text-align:center" in attrs["style"]:
					self.bbcode += "[center:<UID>]"
					self.div.append("[/center:<UID>]")
				else:
					self.div.append("")
			else:
				self.div.append("")
		elif tag=='ul':
			self.bbcode += "[list:<UID>]"
		elif tag=='ol' and attrs.has_key("type"):
			self.bbcode += "[list=" + attrs["type"] + ":<UID>]"
		elif tag=='li':
			self.bbcode += "[*:<UID>]"
		elif tag=='table':
			if not (attrs.has_key("cellspacing") and attrs.has_key("cellpadding") and attrs.has_key("border") and attrs.has_key("align") and attrs.has_key("width")):
				args = ""
				if attrs.has_key("border"):
					args += " border=" + attrs["border"]
				if attrs.has_key("cellspacing"):
					args += " cellspacing=" + attrs["cellspacing"]
				if attrs.has_key("cellpadding"):
					args += " cellpadding=" + attrs["cellpadding"]
				self.bbcode += "[table" + args + ":<UID>]"
				self.table.append("[/table:<UID>]")
			else:
				self.table.append("")
		elif tag=='tr':
			if self.table[len(self.table)-1] == "[/table:<UID>]":
				self.bbcode += "[tr:<UID>]"
				self.tr.append("[/tr:<UID>]")
			else:
				self.tr.append("")
		elif tag=='td':
			if attrs.has_key("class"):
				if attrs["class"] == "quote":
					if self.author != "":
						self.bbcode += "[quote=\"" + self.author + "\":<UID>]"
					else:
						self.bbcode += "[quote:<UID>]"
					self.td.append("[/quote:<UID>]")
				elif attrs["class"] == "code":
					self.bbcode += "[code:<UID>]"
					self.td.append("[/code:<UID>]")
				elif attrs["class"] == "spoiler_content hidden":
					self.bbcode += "[spoiler:<UID>]"
					self.td.append("[/spoiler:<UID>]")
				else:
					self.td.append("")
			elif self.table[len(self.table)-1] == "[/table:<UID>]":
				self.bbcode += "[td:<UID>]"
				self.td.append("[/td:<UID>]")
			else:
				self.td.append("")
		elif tag=='embed':
			if attrs.has_key("width") and attrs.has_key("height") and attrs.has_key("src"):
				self.bbcode += "[flash=" + attrs["width"] + "," + attrs["height"] + ":<UID>]" + attrs["src"] + "[/flash:<UID>]"
		elif tag=='marquee':
			if attrs.has_key("direction"):
				if attrs["direction"] == "up":
					self.bbcode += "[updown:<UID>]"
					self.marquee.append("[/updown:<UID>]")
				else:
					self.bbcode += "[scroll:<UID>]"
					self.marquee.append("[/scroll:<UID>]")
			else:
				self.bbcode += "[scroll:<UID>]"
				self.marquee.append("[/scroll:<UID>]")
		elif tag=="sub":
			self.bbcode += "[sub:<UID>]"
		elif tag=="sup":
			self.bbcode += "[sup:<UID>]"

	def handle_endtag(self, tag):
		if tag=='strong':
			self.bbcode += "[/b:<UID>]"
		elif tag=='i':
			self.bbcode += "[/i:<UID>]"
		elif tag=='u':
			self.bbcode += "[/u:<UID>]"
		elif tag=="b":
			self.quote=False
		elif tag=='a':
			self.bbcode += self.a.pop()
		elif tag=='strike':
			self.bbcode += "[/strike:<UID>]"
		elif tag=='font':
			self.bbcode += self.font.pop()
		elif tag=='span':
			self.bbcode += self.span.pop()
		elif tag=='div':
			self.bbcode += self.div.pop()
		elif tag=='ul':
			self.bbcode += "[/list:<UID>]"
		elif tag=='ol':
			self.bbcode += "[/list:<UID>]"
		elif tag=='table':
			self.bbcode += self.table.pop()
		elif tag=='td':
			self.bbcode += self.td.pop()
		elif tag=='tr':
			self.bbcode += self.tr.pop()
		elif tag=='marquee':
			self.bbcode += self.marquee.pop()
		elif tag=="sub":
			self.bbcode += "[/sub:<UID>]"
		elif tag=="sup":
			self.bbcode += "[/sup:<UID>]"


def htmltobbcode(string, smileys):
	p = HtmltobbcodeParser(smileys)
	p.feed(string)
	
	return p.bbcode
