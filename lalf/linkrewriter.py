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
Module handling the rewriting of internal links
"""

import re
from urllib.parse import urlparse, parse_qs

class LinkRewriter(object):
    """
    Object used to rewrite internal links
    """
    handlers = []

    @classmethod
    def handler(cls, regex, required_params=None):
        """
        Decorator adding a handler to the LinkRewriter class

        Args:
            regex (str): A regular expression matching the paths that should be
                rewritten by this handler
            required_params (List(str)): A list of GET parameters that are
                required for this handler to be used

        When the rewrite method is called, the first handler whose regular
        expression matches the path (returned by `urlparse`_) and whose
        required parameters are defined in the query is called with the
        following arguments:
            bb (BB): The BB object containing the exported forum (which should
                be used to convert the ids when necessary)
            match: `Match object`_ returned by re.fullmatch(regex, path)
            params: The query of the url (see `urlparse`_) parsed with `parse_qs`_
            fragment (str): The fragment of the url (see `urlparse`_)


        .. _urlparse:
            https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse

        .. _parse_qs:
            https://docs.python.org/3/library/urllib.parse.html#urllib.parse.parse_qs

        .. _Match object:
            https://docs.python.org/3/library/re.html#match-objects
        """
        def decorator(handler): # pylint: disable=missing-docstring
            cls.handlers.append((re.compile(regex), handler, required_params or []))
            return handler
        return decorator

    def __init__(self, bb):
        self.bb = bb

    def rewrite(self, url):
        """
        Rewrite an internal link

        Attrs:
            url (str): Link to a page in the original forum

        Returns:
            (str): A link to the corresponding page in the new forum or
                None if there is no rewriting handler for this url
        """
        _, netloc, path, params, query, fragment = urlparse(url)

        if netloc != self.bb.config["url"]:
            return None

        for (regex, handler, required_params) in self.__class__.handlers:
            params = parse_qs(query)
            match = regex.fullmatch(path)
            if match and all(param in params for param in required_params):
                newpath = handler(self.bb, match, params, fragment)
                if newpath:
                    return self.bb.config["phpbb_url"] + newpath

@LinkRewriter.handler(r"")
@LinkRewriter.handler(r"/")
@LinkRewriter.handler(r"/forum")
def root_handler(bb, match, params, fragment):
    """
    Rewrite urls pointing to the root of the forum
    """
    return "/"

@LinkRewriter.handler(r"/([fc]\d+)-.*")
@LinkRewriter.handler(r"/.*-([fc]\d+)/")
@LinkRewriter.handler(r"/.*-([fc]\d+).htm")
def forum_handler(bb, match, params, fragment):
    """
    Rewrite urls of the following forms:

    /f<id>-...
    /c<id>-...
    /...-f<id>/
    /...-f<id>.htm
    """
    forum_id = match.group(1)
    try:
        forum_id = bb.forums[forum_id].newid
    except KeyError:
        return None

    return "/viewforum.php?f={}".format(forum_id)

@LinkRewriter.handler(r"/t(\d+)[-p].*")
@LinkRewriter.handler(r"/.*-t(\d+)\.htm")
@LinkRewriter.handler(r"/.*-t(\d+)-\d+\.htm")
def topic_handler(bb, match, params, fragment):
    """
    Rewrite urls of the following forms:

    /t<id>-...
    /...-t<id>.htm
    /...-t<id>-<page>.htm
    """
    try:
        post_id = int(fragment)
    except ValueError:
        pass
    else:
        return "/viewtopic.php?p={post}#p{post}".format(post=post_id)

    return "/viewtopic.php?f={}".format(match.group(1))

@LinkRewriter.handler(r"/viewtopic.forum", ["t"])
def viewtopic_handler(bb, match, params, fragment):
    """
    Rewrite urls of the following forms:

    /viewtopic.forum?t=<id>
    """
    return "/viewtopic.php?t={post}".format(post=params["t"][0])

@LinkRewriter.handler(r"/.*-p(\d+).htm")
def post_handler(bb, match, params, fragment):
    """
    Rewrite urls of the following forms:

    /...-p<id>.htm
    """
    return "/viewtopic.php?p={post}#p{post}".format(post=match.group(1))

@LinkRewriter.handler(r"/viewtopic.forum", ["p"])
def viewpost_handler(bb, match, params, fragment):
    """
    Rewrite urls of the following forms:

    /viewtopic.forum?p=<id>
    """
    return "/viewtopic.php?p={post}#p{post}".format(post=params["p"][0])

@LinkRewriter.handler(r"/u(\d+)")
def user_handler(bb, match, params, fragment):
    """
    Rewrite urls of the following forms:

    /u<id>
    """
    user_id = int(match.group(1))
    try:
        user_id = bb.user_ids[user_id].newid
    except KeyError:
        return None

    return "/memberlist.php?mode=viewprofile&u={}".format(user_id)
