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
from binascii import crc32
import base64
import hashlib
import random

def email_hash(email):
    return str(crc32(email)&0xffffffff) + str(len(email))

def escape_var(i):
    if isinstance(i,(str,unicode)):
        return i.replace("\\","\\\\").replace("'","\\'")
    return i

def default_forum_acl(forumid):
    for gid, perm in ((1, 17), # guests: readonly
                      (2, 21), # registered: standard w/ polls
                      (3, 21), # registered+COPPA: standard w/ polls
                      (4, 14), # global mods: full access
                      (4, 11), # global mods: standard moderation
                      (5, 14), # admins: full access
                      (5, 10), # admins: full moderation
                      (6, 19), # bots: bot access
                     ):
        yield {
            "group_id" : gid,
            "forum_id" : forumid,
            "auth_option_id" : 0,
            "auth_role_id" : perm,
            "auth_setting" : 0
        }

bbcodes = [
    {"bbcode_id" : 13,
     "bbcode_tag" : "strike",
     "bbcode_helpline" : "Texte barré",
     "display_on_posting" : "0",
     "bbcode_match" : "[strike]{TEXT}[/strike]",
     "bbcode_tpl" : "<span style=\"text-decoration: line-through;\">{TEXT}</span>",
     "first_pass_match" : "!\\[strike\\](.*?)\\[/strike\\]!ies",
     "first_pass_replace" : "'[strike:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/strike:$uid]'",
     "second_pass_match" : "!\\[strike:$uid\\](.*?)\\[/strike:$uid\\]!s",
     "second_pass_replace" : "<span style=\"text-decoration: line-through;\">${1}</span>"},
     
    {"bbcode_id" : 14,
     "bbcode_tag" : "left",
     "bbcode_helpline" : "Texte aligné à gauche",
     "display_on_posting" : "0",
     "bbcode_match" : "[left]{TEXT}[/left]",
     "bbcode_tpl" : "<div style=\"text-align: left;\">{TEXT}</div>",
     "first_pass_match" : "!\\[left\\](.*?)\\[/left\\]!ies",
     "first_pass_replace" : "'[left:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/left:$uid]'",
     "second_pass_match" : "!\\[left:$uid\\](.*?)\\[/left:$uid\\]!s",
     "second_pass_replace" : "<div style=\"text-align: left;\">${1}</div>"},
     
    {"bbcode_id" : 15,
     "bbcode_tag" : "center",
     "bbcode_helpline" : "Texte aligné au centre",
     "display_on_posting" : "0",
     "bbcode_match" : "[center]{TEXT}[/center]",
     "bbcode_tpl" : "<div style=\"text-align: center;\">{TEXT}</div>",
     "first_pass_match" : "!\\[center\\](.*?)\\[/center\\]!ies",
     "first_pass_replace" : "'[center:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/center:$uid]'",
     "second_pass_match" : "!\\[center:$uid\\](.*?)\\[/center:$uid\\]!s",
     "second_pass_replace" : "<div style=\"text-align: center;\">${1}</div>"},
     
    {"bbcode_id" : 16,
     "bbcode_tag" : "right",
     "bbcode_helpline" : "Texte aligné à droite",
     "display_on_posting" : "0",
     "bbcode_match" : "[right]{TEXT}[/right]",
     "bbcode_tpl" : "<div style=\"text-align: right;\">{TEXT}</div>",
     "first_pass_match" : "!\\[right\\](.*?)\\[/right\\]!ies",
     "first_pass_replace" : "'[right:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/right:$uid]'",
     "second_pass_match" : "!\\[right:$uid\\](.*?)\\[/right:$uid\\]!s",
     "second_pass_replace" : "<div style=\"text-align: right;\">${1}</div>"},
     
    {"bbcode_id" : 17,
     "bbcode_tag" : "justify",
     "bbcode_helpline" : "Texte justifié",
     "display_on_posting" : "0",
     "bbcode_match" : "[justify]{TEXT}[/justify]",
     "bbcode_tpl" : "<div style=\"text-align: justify;\">{TEXT}</div>",
     "first_pass_match" : "!\\[justify\\](.*?)\\[/justify\\]!ies",
     "first_pass_replace" : "'[justify:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/justify:$uid]'",
     "second_pass_match" : "!\\[justify:$uid\\](.*?)\\[/justify:$uid\\]!s",
     "second_pass_replace" : "<div style=\"text-align: justify;\">${1}</div>"},
     
    {"bbcode_id" : 18,
     "bbcode_tag" : "font",
     "bbcode_helpline" : "Modifier la police",
     "display_on_posting" : "0",
     "bbcode_match" : "[font={SIMPLETEXT}]{TEXT}[/font]",
     "bbcode_tpl" : "<span style=\"font-family: {SIMPLETEXT};\">{TEXT}</span>",
     "first_pass_match" : "!\\[font\\=([a-zA-Z0-9-+.,_ ]+)\\](.*?)\\[/font\\]!ies",
     "first_pass_replace" : "'[font=${1}:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${2}')).'[/font:$uid]'",
     "second_pass_match" : "!\\[font\\=([a-zA-Z0-9-+.,_ ]+):$uid\\](.*?)\\[/font:$uid\\]!s",
     "second_pass_replace" : "<span style=\"font-family: ${1};\">${2}</span>"},
     
    {"bbcode_id" : 19,
     "bbcode_tag" : "td",
     "bbcode_helpline" : "Cellule de tableau",
     "display_on_posting" : "0",
     "bbcode_match" : "[td]{TEXT}[/td]",
     "bbcode_tpl" : "<td>{TEXT}</td>",
     "first_pass_match" : "!\\[td\\](.*?)\\[/td\\]!ies",
     "first_pass_replace" : "'[td:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/td:$uid]'",
     "second_pass_match" : "!\\[td:$uid\\](.*?)\\[/td:$uid\\]!s",
     "second_pass_replace" : "<td>${1}</td>"},

    {"bbcode_id" : 20,
     "bbcode_tag" : "tr",
     "bbcode_helpline" : "Ligne de tableau",
     "display_on_posting" : "0",
     "bbcode_match" : "[tr]{TEXT}[/tr]",
     "bbcode_tpl" : "<tr>{TEXT}</tr>",
     "first_pass_match" : "!\\[tr\\](.*?)\\[/tr\\]!ies",
     "first_pass_replace" : "'[tr:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/tr:$uid]'",
     "second_pass_match" : "!\\[tr:$uid\\](.*?)\\[/tr:$uid\\]!s",
     "second_pass_replace" : "<tr>${1}</tr>"},

    {"bbcode_id" : 21,
     "bbcode_tag" : "table",
     "bbcode_helpline" : "Tableau",
     "display_on_posting" : "0",
     "bbcode_match" : "[table]{TEXT}[/table]",
     "bbcode_tpl" : "<table>{TEXT}</table>",
     "first_pass_match" : "!\\[table([a-zA-Z0-9-+.,_= ]*)\\](.*?)\\[/table\\]!ies",
     "first_pass_replace" : "'[table${1}:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${2}')).'[/table:$uid]'",
     "second_pass_match" : "!\\[table([a-zA-Z0-9-+.,_= ]*):$uid\\](.*?)\\[/table:$uid\\]!s",
     "second_pass_replace" : "<table ${1}>${2}</table>"},
     
    {"bbcode_id" : 22,
     "bbcode_tag" : "updown",
     "bbcode_helpline" : "Texte défilant verticalement",
     "display_on_posting" : "0",
     "bbcode_match" : "[updown]{TEXT}[/updown]",
     "bbcode_tpl" : "<marquee height=\"60\" scrollamount=\"1\" direction=\"up\" behavior=\"scroll\">{TEXT}</marquee>",
     "first_pass_match" : "!\\[updown\\](.*?)\\[/updown\\]!ies",
     "first_pass_replace" : "'[updown:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/updown:$uid]'",
     "second_pass_match" : "!\\[updown:$uid\\](.*?)\\[/updown:$uid\\]!s",
     "second_pass_replace" : "<marquee height=\"60\" scrollamount=\"1\" direction=\"up\" behavior=\"scroll\">${1}</marquee>"},
     
    {"bbcode_id" : 23,
     "bbcode_tag" : "hr",
     "bbcode_helpline" : "Ligne horizontale",
     "display_on_posting" : "0",
     "bbcode_match" : "[hr][/hr]",
     "bbcode_tpl" : "<hr />",
     "first_pass_match" : "!\\[hr\\]\\[/hr\\]!ies",
     "first_pass_replace" : "'[hr:$uid][/hr:$uid]'",
     "second_pass_match" : "!\\[hr:$uid\\]\\[/hr:$uid\\]!s",
     "second_pass_replace" : "<hr />"},
     
    {"bbcode_id" : 24,
     "bbcode_tag" : "scroll",
     "bbcode_helpline" : "Texte défilant horizontalement",
     "display_on_posting" : "0",
     "bbcode_match" : "[scroll]{TEXT}[/scroll]",
     "bbcode_tpl" : "<marquee>{TEXT}</marquee>",
     "first_pass_match" : "!\\[scroll\\](.*?)\\[/scroll\\]!ies",
     "first_pass_replace" : "'[scroll:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/scroll:$uid]'",
     "second_pass_match" : "!\\[scroll:$uid\\](.*?)\\[/scroll:$uid\\]!s",
     "second_pass_replace" : "<marquee>${1}</marquee>"},
     
    {"bbcode_id" : 25,
     "bbcode_tag" : "sup",
     "bbcode_helpline" : "Texte en exposant",
     "display_on_posting" : "0",
     "bbcode_match" : "[sup]{TEXT}[/sup]",
     "bbcode_tpl" : "<sup>{TEXT}</sup>",
     "first_pass_match" : "!\\[sup\\](.*?)\\[/sup\\]!ies",
     "first_pass_replace" : "'[sup:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/sup:$uid]'",
     "second_pass_match" : "!\\[sup:$uid\\](.*?)\\[/sup:$uid\\]!s",
     "second_pass_replace" : "<sup>${1}</sup>"},
     
    {"bbcode_id" : 26,
     "bbcode_tag" : "sub",
     "bbcode_helpline" : "Texte en indice",
     "display_on_posting" : "0",
     "bbcode_match" : "[sub]{TEXT}[/sub]",
     "bbcode_tpl" : "<sub>{TEXT}</sub>",
     "first_pass_match" : "!\\[sub\\](.*?)\\[/sub\\]!ies",
     "first_pass_replace" : "'[sub:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/sub:$uid]'",
     "second_pass_match" : "!\\[sub:$uid\\](.*?)\\[/sub:$uid\\]!s",
     "second_pass_replace" : "<sub>${1}</sub>"},
     
    {"bbcode_id" : 27,
     "bbcode_tag" : "spoiler",
     "bbcode_helpline" : "Spoiler",
     "display_on_posting" : "0",
     "bbcode_match" : "[spoiler]{TEXT}[/spoiler]",
     "bbcode_tpl" : "<div style=\"margin:20px; margin-top:5px\"><div class=\"quotetitle\"><b>Spoiler:</b> <input type=\"button\" value=\"Show\" style=\"width:45px;font-size:10px;margin:0px;padding:0px;\" onclick=\"if (this.parentNode.parentNode.getElementsByTagName('div')[1].getElementsByTagName('div')[0].style.display != '') { this.parentNode.parentNode.getElementsByTagName('div')[1].getElementsByTagName('div')[0].style.display = '';        this.innerText = ''; this.value = 'Hide'; } else { this.parentNode.parentNode.getElementsByTagName('div')[1].getElementsByTagName('div')[0].style.display = 'none'; this.innerText = ''; this.value = 'Show'; }\" /></div><div class=\"quotecontent\"><div style=\"display: none;\">{TEXT}</div></div></div>",
     "first_pass_match" : "!\\[spoiler\\](.*?)\\[/spoiler\\]!ies",
     "first_pass_replace" : "'[spoiler:$uid]'.str_replace(array(\"\\r\\n\", '\\\"', '\\'', '(', ')'), array(\"\\n\", '\"', '&#39;', '&#40;', '&#41;'), trim('${1}')).'[/spoiler:$uid]'",
     "second_pass_match" : "!\\[spoiler:$uid\\](.*?)\\[/spoiler:$uid\\]!s",
     "second_pass_replace" : "<div style=\"margin:20px; margin-top:5px\"><div class=\"quotetitle\"><b>Spoiler:</b> <input type=\"button\" value=\"Show\" style=\"width:45px;font-size:10px;margin:0px;padding:0px;\" onclick=\"if (this.parentNode.parentNode.getElementsByTagName('div')[1].getElementsByTagName('div')[0].style.display != '') { this.parentNode.parentNode.getElementsByTagName('div')[1].getElementsByTagName('div')[0].style.display = '';        this.innerText = ''; this.value = 'Hide'; } else { this.parentNode.parentNode.getElementsByTagName('div')[1].getElementsByTagName('div')[0].style.display = 'none'; this.innerText = ''; this.value = 'Show'; }\" /></div><div class=\"quotecontent\"><div style=\"display: none;\">${1}</div></div></div>"}]

def makebitfield(dat):
    tags = {'code' : 8,
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
        tags[b["bbcode_tag"]] = b["bbcode_id"]

    bf = [0] * 10
    for i in tags:
        bbtag = '\[/'+i+'\]'
        if re.findall(bbtag, dat):
            c, d = divmod(tags[i], 8)
            bf[c] |= (1 << (7-d))

    tempstr = ''.join([chr(c) for c in bf]).rstrip('\0').encode("latin-1")
    return base64.b64encode(tempstr).decode("UTF-8")  # decode("UTF-8") is required to convert from byte list to string

def format_post(post):
    tags = ['*', 'code', 'quote', 'attachment', 'b', 'i', 'url', 'img', 'size', 'color', 'u', 'list', 'email', 'flash']
    for n in bbcodes:
        tags.append(n["bbcode_tag"])
        
    uid = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(8)])
    bitfield = makebitfield(post)

    # Cleanup one ugly case
    post = post.replace("Spoiler: [spoiler]", "[spoiler]")
    post = post.replace("[spoiler]", "[spoiler]")

    for t in tags:
        post = post.replace("[{}]".format(t), "[{}:{}]".format(t, uid))
        post = post.replace("[/{}]".format(t), "[/{}:{}]".format(t, uid))
    checksum = hashlib.md5(post.encode("utf8")).hexdigest()

    # find tags such as [list=1] or [quote="me"] that are ignored by the code above
    regex = re.compile("\[(list|quote|url|flash|size|color|font)=(.+?)\]", re.IGNORECASE)
    foundtags = regex.findall(post)
    for tag in foundtags:
        post = post.replace("[{}={}]".format(tag[0], tag[1]), "[{}={}:{}]".format(tag[0], tag[1], uid))

    # handle [/*:m], [/list:u] and [/list:o] cases
    post = post.replace("[/*:m]", "[/*:m:{}]".format(uid))
    post = post.replace("[/list:u]", "[/list:u:{}]".format(uid))
    post = post.replace("[/list:o]", "[/list:o:{}]".format(uid))

    return post, uid, bitfield, checksum
    

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
