import logging
logger = logging.getLogger("lalf")

import re
from pyquery import PyQuery
import session
from node import Node
from userspage import UsersPage
import sql
import phpbb
from exceptions import *

class Users(Node):
    def _export_(self):
        logger.info('Récupération des membres')
    
        params = {
            "part" : "users_groups",
            "sub" : "users"
        }

        r = session.get_admin("/admin/index.forum", params=params)
        result = re.search('function do_pagination_start\(\)[^\}]*start = \(start > \d+\) \? (\d+) : start;[^\}]*start = \(start - 1\) \* (\d+);[^\}]*\}', r.text)
    
        try:
            pages = int(result.group(1))
            usersperpage = int(result.group(2))
        except:
            pages = 1
            usersperpage = 0
        
        for page in range(0,pages):
            self.children.append(UsersPage(self.parent, page*usersperpage))
        
    def get_users(self):
        for p in self.children:
            for c in p.children:
                yield c

    def get_newid(self, name):
        for u in self.get_users():
            if u.name == name:
                # The user exists
                return u.newid
        # The user does not exist (he is either anonymous or has been deleted)
        return 1
    
    def add_bot(self, file, bot, id):
        sql.insert(file, "users", {
            "user_id" : id,
            "user_type" : "2",
            "group_id" : "6",
            "username" : bot["name"],
            "username_clean" : bot["name"].lower(),
            "user_regdate" : "0",
            "user_password" : "",
            "user_colour" : "9E8DA7",
            "user_email" : "",
            "user_email_hash" : "00",
            "user_lang" : "fr",
            "user_style" : "1",
            "user_timezone" : "0",
            "user_dateformat" : "D M d, Y g:i a",
            "user_allow_massemail" : "0"})
        sql.insert(file, "user_group", {
            "group_id" : "6",
            "user_id" : id,
            "user_pending" : "0",
            "group_leader" : "0"})
        sql.insert(file, "bots", {
            "bot_active" : "1",
            "bot_name" : bot["name"],
            "user_id" : id,
            "bot_agent" : bot["agent"],
            "bot_ip" : bot["ip"]})
    
    def _dump_(self, file):
        # Clean users tables
        sql.truncate(file, "users")
        sql.truncate(file, "user_group")
        sql.truncate(file, "bots")

        # Add anonymous user
        sql.insert(file, "users", {
            "user_id" : "1",
            "user_type" : "2",
            "group_id" : "1",
            "username" : "Anonymous",
            "username_clean" : "anonymous",
            "user_regdate" : "0",
            "user_password" : "",
            "user_email" : "",
            "user_lang" : "fr",
            "user_style" : "1",
            "user_rank" : "0",
            "user_colour" : "",
            "user_posts" : "0",
            "user_permissions" : "",
            "user_ip" : "",
            "user_birthday" : "",
            "user_lastpage" : "",
            "user_last_confirm_key" : "",
            "user_post_sortby_type" : "t",
            "user_post_sortby_dir" : "a",
            "user_topic_sortby_type" : "t",
            "user_topic_sortby_dir" : "d",
            "user_avatar" : "",
            "user_sig" : "",
            "user_sig_bbcode_uid" : "",
            "user_from" : "",
            "user_icq" : "",
            "user_aim" : "",
            "user_yim" : "",
            "user_msnm" : "",
            "user_jabber" : "",
            "user_website" : "",
            "user_occ" : "",
            "user_interests" : "",
            "user_actkey" : "",
            "user_newpasswd" : "",
            "user_allow_massemail" : "0"})
        sql.insert(file, "user_group", {
            "group_id" : "1",
            "user_id" : "1",
            "user_pending" : "0"})

        id = 2
        # Add bots
        for bot in phpbb.bots:
            self.add_bot(file, bot, id)
            id += 1
