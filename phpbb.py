#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       phpbb.py
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

import re
from binascii import crc32

def email_hash(email):
	return str(crc32(email)&0xffffffff) + str(len(email))

def escape_var(i):
	if isinstance(i,(str,unicode)):
		return i.replace("\\","\\\\").replace("'","\\'")
	return i

def default_forum_acl(forumnumber):
	ret=[]
	for gid, perm in ((1, 17), # guests: readonly
					  (2, 21), # registered: standard w/ polls
					  (3, 21), # registered+COPPA: standard w/ polls
					  (4, 14), # global mods: full access
					  (4, 11), # global mods: standard moderation
					  (5, 14), # admins: full access
					  (5, 10), # admins: full moderation
					  (6, 19), # bots: bot access
					 ):
		ret.append('(%i, %i, 0, %i, 0)'%(gid, forumnumber, perm))
	return ret

def makebitfield(dat):
	bbcodes={'code' : 8,
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
			 'flash' : 11,
			 'font' : 13, # custom BBCodes
			 'align' : 14}
	bf=[0]*10
	for i in bbcodes:
		if re.findall('\\[/'+i+':[^\\[\\]]*<UID>]', dat):
			c,d=divmod(bbcodes[i],8)
			bf[c]|=(1<<(7-d))
	return ''.join([chr(c) for c in bf]).rstrip('\0').encode('base64')

bbcodes = [	u'(13, \'strike\', \'Texte barr\xc3\xa9\', 0, \'[strike]{TEXT}[/strike]\', \'<span style="text-decoration:line-through;">{TEXT}</span>\', \'!\\\\[strike\\\\](.*?)\\\\[/strike\\\\]!ies\', \'\'\'[strike:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/strike:$uid]\'\'\', \'!\\\\[strike:$uid\\\\](.*?)\\\\[/strike:$uid\\\\]!s\', \'<span style="text-decoration:line-through;">${1}</span>\');\n',
			u'(14, \'left\', \'Texte align\xc3\xa9 \xc3\xa0 gauche\', 0, \'[left]{TEXT1}[/left]\', \'<div style="text-align: left;">{TEXT1}</div>\', \'!\\\\[left\\\\](.*?)\\\\[/left\\\\]!ies\', \'\'\'[left:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/left:$uid]\'\'\', \'!\\\\[left:$uid\\\\](.*?)\\\\[/left:$uid\\\\]!s\', \'<div style="text-align: left;">${1}</div>\');\n',
			u'(15, \'center\', \'Texte centr\xc3\xa9\', 0, \'[center]{TEXT1}[/center]\', \'<div style="text-align: center;">{TEXT1}</div>\', \'!\\\\[center\\\\](.*?)\\\\[/center\\\\]!ies\', \'\'\'[center:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/center:$uid]\'\'\', \'!\\\\[center:$uid\\\\](.*?)\\\\[/center:$uid\\\\]!s\', \'<div style="text-align: center;">${1}</div>\');\n',
			u'(16, \'right\', \'Texte align\xc3\xa9 \xc3\xa0 droite\', 0, \'[right]{TEXT1}[/right]\', \'<div style="text-align: right;">{TEXT1}</div>\', \'!\\\\[right\\\\](.*?)\\\\[/right\\\\]!ies\', \'\'\'[right:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/right:$uid]\'\'\', \'!\\\\[right:$uid\\\\](.*?)\\\\[/right:$uid\\\\]!s\', \'<div style="text-align: right;">${1}</div>\');\n',
			u'(17, \'justify\', \'Texte justifi\xc3\xa9\', 0, \'[justify]{TEXT1}[/justify]\', \'<div style="text-align: justify;">{TEXT1}</div>\', \'!\\\\[justify\\\\](.*?)\\\\[/justify\\\\]!ies\', \'\'\'[justify:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/justify:$uid]\'\'\', \'!\\\\[justify:$uid\\\\](.*?)\\\\[/justify:$uid\\\\]!s\', \'<div style="text-align: justify;">${1}</div>\');\n',
			u'(18, \'font=\', \'Modifier la police\', 0, \'[font={SIMPLETEXT1}]{SIMPLETEXT2}[/font]\', \'<span style="font-family: {SIMPLETEXT1};">{SIMPLETEXT2}</span>\', \'!\\\\[font\\\\=([a-zA-Z0-9-+.,_ ]+)\\\\]([a-zA-Z0-9-+.,_ ]+)\\\\[/font\\\\]!i\', \'[font=${1}:$uid]${2}[/font:$uid]\', \'!\\\\[font\\\\=([a-zA-Z0-9-+.,_ ]+):$uid\\\\]([a-zA-Z0-9-+.,_ ]+)\\\\[/font:$uid\\\\]!s\', \'<span style="font-family: ${1};">${2}</span>\');\n',
			u'(19, \'td\', \'Cellule de tableau\', 0, \'[td]{TEXT1}[/td]\', \'<td>{TEXT1}</td>\', \'!\\\\[td\\\\](.*?)\\\\[/td\\\\]!ies\', \'\'\'[td:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/td:$uid]\'\'\', \'!\\\\[td:$uid\\\\](.*?)\\\\[/td:$uid\\\\]!s\', \'<td>${1}</td>\');\n',
			u'(20, \'tr\', \'Ligne de tableau\', 0, \'[tr]{TEXT1}[/tr]\', \'<tr>{TEXT1}</tr>\', \'!\\\\[tr\\\\](.*?)\\\\[/tr\\\\]!ies\', \'\'\'[tr:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/tr:$uid]\'\'\', \'!\\\\[tr:$uid\\\\](.*?)\\\\[/tr:$uid\\\\]!s\', \'<tr>${1}</tr>\');\n',
			u'(21, \'table\', \'Tableau\', 0, \'[table{TEXT1}]{TEXT2}[/table]\', \'<table {TEXT1}>{TEXT2}</table>\', \'!\\\\[table(.*?)\\\\](.*?)\\\\[/table\\\\]!ies\', \'\'\'[table\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\':$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${2}\'\')).\'\'[/table:$uid]\'\'\', \'!\\\\[table(.*?):$uid\\\\](.*?)\\\\[/table:$uid\\\\]!s\', \'<table ${1}>${2}</table>\');\n',
			u'(22, \'updown\', \'Texte d\xc3\xa9filant verticalement\', 0, \'[updown]{TEXT}[/updown]\', \'<marquee height="60" scrollamount="1" direction="up" behavior="scroll">{TEXT}</marquee>\', \'!\\\\[updown\\\\](.*?)\\\\[/updown\\\\]!ies\', \'\'\'[updown:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/updown:$uid]\'\'\', \'!\\\\[updown:$uid\\\\](.*?)\\\\[/updown:$uid\\\\]!s\', \'<marquee height="60" scrollamount="1" direction="up" behavior="scroll">${1}</marquee>\');\n',
			u'(23, \'hr\', \'Ligne horizontale\', 0, \'[hr][/hr]\', \'<hr />\', \'!\\\\[hr\\\\]\\\\[/hr\\\\]!i\', \'[hr:$uid][/hr:$uid]\', \'[hr:$uid][/hr:$uid]\', \'\');\n',
			u'(24, \'scroll\', \'Texte d\xc3\xa9filant horizontalement\', 0, \'[scroll]{TEXT}[/scroll]\', \'<marquee>{TEXT}</marquee>\', \'!\\\\[scroll\\\\](.*?)\\\\[/scroll\\\\]!ies\', \'\'\'[scroll:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/scroll:$uid]\'\'\', \'!\\\\[scroll:$uid\\\\](.*?)\\\\[/scroll:$uid\\\\]!s\', \'<marquee>${1}</marquee>\');\n',
			u'(25, \'sup\', \'Texte en exposant\', 0, \'[sup]{TEXT}[/sup]\', \'<sup>{TEXT}</sup>\', \'!\\\\[sup\\\\](.*?)\\\\[/sup\\\\]!ies\', \'\'\'[sup:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/sup:$uid]\'\'\', \'!\\\\[sup:$uid\\\\](.*?)\\\\[/sup:$uid\\\\]!s\', \'<sup>${1}</sup>\');\n',
			u'(26, \'sub\', \'Texte en indice\', 0, \'[sub]{TEXT}[/sub]\', \'<sub>{TEXT}</sub>\', \'!\\\\[sub\\\\](.*?)\\\\[/sub\\\\]!ies\', \'\'\'[sub:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/sub:$uid]\'\'\', \'!\\\\[sub:$uid\\\\](.*?)\\\\[/sub:$uid\\\\]!s\', \'<sub>${1}</sub>\');\n',
			u'(27, \'spoiler\', \'Spoiler\', 0, \'[spoiler]{TEXT}[/spoiler]\', \'<div style="padding: 3px; background-color: #FFFFFF; border: 1px solid #d8d8d8; font-size: 1em;"><div style="text-transform: uppercase; border-bottom: 1px solid #CCCCCC; margin-bottom: 3px; font-size: 0.8em; font-weight: bold; display: block;"><span onClick="if (this.parentNode.parentNode.getElementsByTagName(\'\'div\'\')[1].getElementsByTagName(\'\'div\'\')[0].style.display != \'\'\'\') {  this.parentNode.parentNode.getElementsByTagName(\'\'div\'\')[1].getElementsByTagName(\'\'div\'\')[0].style.display = \'\'\'\'; this.innerHTML = \'\'<b>Spoiler: </b><a href=\\\\\'\'#\\\\\'\' onClick=\\\\\'\'return false;\\\\\'\'>Cacher</a>\'\'; } else { this.parentNode.parentNode.getElementsByTagName(\'\'div\'\')[1].getElementsByTagName(\'\'div\'\')[0].style.display = \'\'none\'\'; this.innerHTML = \'\'<b>Spoiler: </b><a href=\\\\\'\'#\\\\\'\' onClick=\\\\\'\'return false;\\\\\'\'>Afficher</a>\'\'; }" /><b>Spoiler: </b><a href="#" onClick="return false;">Afficher</a></span></div><div class="quotecontent"><div style="display: none;">{TEXT}</div></div></div>\', \'!\\\\[spoiler\\\\](.*?)\\\\[/spoiler\\\\]!ies\', \'\'\'[spoiler:$uid]\'\'.str_replace(array("\\\\r\\\\n", \'\'\\\\"\'\', \'\'\\\\\'\'\'\', \'\'(\'\', \'\')\'\'), array("\\\\n", \'\'"\'\', \'\'&#39;\'\', \'\'&#40;\'\', \'\'&#41;\'\'), trim(\'\'${1}\'\')).\'\'[/spoiler:$uid]\'\'\', \'!\\\\[spoiler:$uid\\\\](.*?)\\\\[/spoiler:$uid\\\\]!s\', \'<div style="padding: 3px; background-color: #FFFFFF; border: 1px solid #d8d8d8; font-size: 1em;"><div style="text-transform: uppercase; border-bottom: 1px solid #CCCCCC; margin-bottom: 3px; font-size: 0.8em; font-weight: bold; display: block;"><span onClick="if (this.parentNode.parentNode.getElementsByTagName(\'\'div\'\')[1].getElementsByTagName(\'\'div\'\')[0].style.display != \'\'\'\') {  this.parentNode.parentNode.getElementsByTagName(\'\'div\'\')[1].getElementsByTagName(\'\'div\'\')[0].style.display = \'\'\'\'; this.innerHTML = \'\'<b>Spoiler: </b><a href=\\\\\'\'#\\\\\'\' onClick=\\\\\'\'return false;\\\\\'\'>Cacher</a>\'\'; } else { this.parentNode.parentNode.getElementsByTagName(\'\'div\'\')[1].getElementsByTagName(\'\'div\'\')[0].style.display = \'\'none\'\'; this.innerHTML = \'\'<b>Spoiler: </b><a href=\\\\\'\'#\\\\\'\' onClick=\\\\\'\'return false;\\\\\'\'>Afficher</a>\'\'; }" /><b>Spoiler: </b><a href="#" onClick="return false;">Afficher</a></span></div><div class="quotecontent"><div style="display: none;">${1}</div></div></div>\');\n']

bots = [{'name': 'AdsBot [Google]'			, 'agent': 'AdsBot-Google'								, 'ip': ''},
		{'name': 'Alexa [Bot]'				, 'agent': 'ia_archiver'								, 'ip': ''},
		{'name': 'Alta Vista [Bot]'			, 'agent': 'Scooter/'									, 'ip': ''},
		{'name': 'Ask Jeeves [Bot]'			, 'agent': 'Ask Jeeves'									, 'ip': ''},
		{'name': 'Baidu [Spider]'			, 'agent': 'Baiduspider+('								, 'ip': ''},
		{'name': 'Bing [Bot]'				, 'agent': 'bingbot/'									, 'ip': ''},
		{'name': 'Exabot [Bot]'				, 'agent': 'Exabot/'									, 'ip': ''},
		{'name': 'FAST Enterprise [Crawler]', 'agent': 'FAST Enterprise Crawler'					, 'ip': ''},
		{'name': 'FAST WebCrawler [Crawler]', 'agent': 'FAST-WebCrawler/'							, 'ip': ''},
		{'name': 'Francis [Bot]'			, 'agent': 'http://www.neomo.de/'						, 'ip': ''},
		{'name': 'Gigabot [Bot]'			, 'agent': 'Gigabot/'									, 'ip': ''},
		{'name': 'Google Adsense [Bot]'		, 'agent': 'Mediapartners-Google'						, 'ip': ''},
		{'name': 'Google Desktop'			, 'agent': 'Google Desktop'								, 'ip': ''},
		{'name': 'Google Feedfetcher'		, 'agent': 'Feedfetcher-Google'							, 'ip': ''},
		{'name': 'Google [Bot]'				, 'agent': 'Googlebot'									, 'ip': ''},
		{'name': 'Heise IT-Markt [Crawler]'	, 'agent': 'heise-IT-Markt-Crawler'						, 'ip': ''},
		{'name': 'Heritrix [Crawler]'		, 'agent': 'heritrix/1.'								, 'ip': ''},
		{'name': 'IBM Research [Bot]'		, 'agent': 'ibm.com/cs/crawler'							, 'ip': ''},
		{'name': 'ICCrawler - ICjobs'		, 'agent': 'ICCrawler - ICjobs'							, 'ip': ''},
		{'name': 'ichiro [Crawler]'			, 'agent': 'ichiro/'									, 'ip': ''},
		{'name': 'Majestic-12 [Bot]'		, 'agent': 'MJ12bot/'									, 'ip': ''},
		{'name': 'Metager [Bot]'			, 'agent': 'MetagerBot/'								, 'ip': ''},
		{'name': 'MSN NewsBlogs'			, 'agent': 'msnbot-NewsBlogs/'							, 'ip': ''},
		{'name': 'MSN [Bot]'				, 'agent': 'msnbot/'									, 'ip': ''},
		{'name': 'MSNbot Media'				, 'agent': 'msnbot-media/'								, 'ip': ''},
		{'name': 'NG-Search [Bot]'			, 'agent': 'NG-Search/'									, 'ip': ''},
		{'name': 'Nutch [Bot]'				, 'agent': 'http://lucene.apache.org/nutch/'			, 'ip': ''},
		{'name': 'Nutch/CVS [Bot]'			, 'agent': 'NutchCVS/'									, 'ip': ''},
		{'name': 'OmniExplorer [Bot]'		, 'agent': 'OmniExplorer_Bot/'							, 'ip': ''},
		{'name': 'Online link [Validator]'	, 'agent': 'online link validator'						, 'ip': ''},
		{'name': 'psbot [Picsearch]'		, 'agent': 'psbot/0'									, 'ip': ''},
		{'name': 'Seekport [Bot]'			, 'agent': 'Seekbot/'									, 'ip': ''},
		{'name': 'Sensis [Crawler]'			, 'agent': 'Sensis Web Crawler'							, 'ip': ''},
		{'name': 'SEO Crawler'				, 'agent': 'SEO search Crawler/'						, 'ip': ''},
		{'name': 'Seoma [Crawler]'			, 'agent': 'Seoma [SEO Crawler]'						, 'ip': ''},
		{'name': 'SEOSearch [Crawler]'		, 'agent': 'SEOsearch/'									, 'ip': ''},
		{'name': 'Snappy [Bot]'				, 'agent': 'Snappy/1.1 ( http://www.urltrends.com/ )'	, 'ip': ''},
		{'name': 'Steeler [Crawler]'		, 'agent': 'http://www.tkl.iis.u-tokyo.ac.jp/~crawler/'	, 'ip': ''},
		{'name': 'Synoo [Bot]'				, 'agent': 'SynooBot/'									, 'ip': ''},
		{'name': 'Telekom [Bot]'			, 'agent': 'crawleradmin.t-info@telekom.de'				, 'ip': ''},
		{'name': 'TurnitinBot [Bot]'		, 'agent': 'TurnitinBot/'								, 'ip': ''},
		{'name': 'Voyager [Bot]'			, 'agent': 'voyager/1.0'								, 'ip': ''},
		{'name': 'W3 [Sitesearch]'			, 'agent': 'W3 SiteSearch Crawler'						, 'ip': ''},
		{'name': 'W3C [Linkcheck]'			, 'agent': 'W3C-checklink/'								, 'ip': ''},
		{'name': 'W3C [Validator]'			, 'agent': 'W3C_*Validator'								, 'ip': ''},
		{'name': 'WiseNut [Bot]'			, 'agent': 'http://www.WISEnutbot.com'					, 'ip': ''},
		{'name': 'YaCy [Bot]'				, 'agent': 'yacybot'									, 'ip': ''},
		{'name': 'Yahoo MMCrawler [Bot]'	, 'agent': 'Yahoo-MMCrawler/'							, 'ip': ''},
		{'name': 'Yahoo Slurp [Bot]'		, 'agent': 'Yahoo! DE Slurp'							, 'ip': ''},
		{'name': 'Yahoo [Bot]'				, 'agent': 'Yahoo! Slurp'								, 'ip': ''},
		{'name': 'YahooSeeker [Bot]'		, 'agent': 'YahooSeeker/'								, 'ip': ''}]
