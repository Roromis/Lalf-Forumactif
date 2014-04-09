import logging
logger = logging.getLogger("lalf")

import requests
import urllib
import urllib.parse
import sys
import time
from pyquery import PyQuery

from lalf.config import config
from lalf.exceptions import *

session = requests.Session()
sid = None
tid = None

def url(path):
    """
    Returns the full url corresponding to the path given in argument.
    """
    return urllib.parse.urlunparse(("http", config["url"], path, '', '', ''))

def _get(path, **kwargs):
    """
    Download the page with the GET method.
    """

    if "headers" not in kwargs:
        kwargs["headers"] = {}
    
    kwargs["headers"]["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0"
    
    return session.get(url(path), **kwargs)
    
def connect():
    """
    Connect to the forum and initialize session, sid and tid.
    """
    global session
    global sid
    global tid
    
    logger.info('Connection au forum')
        
    session.close()
    sid = None
    tid = None

    session = requests.Session()
    session.keep_alive = False
    
    params = {
        'autologin': 1,
        'login': 'Connexion',
        'password': config["admin_password"],
        'username': config["admin_name"],
        'redirect': ""}
        
    r = _get("/login", params=params)

    logger.debug('Récupération du sid')
    for name, value in session.cookies.items():
        if name[-3:] == "sid":
            sid = value
    
    if sid == None:
        logger.critical('Échec de la connection.')
        raise UnableToConnect()
    
    if tid == None:
        logger.debug('Récupération du tid')
    
        r = _get('/admin/index.forum')
        try:
            tid = urllib.parse.urlparse(r.url).query.split("=")[1]
        except IndexError:
            logger.critical('Impossible de récupérer le tid.')
            raise UnableToConnect()

def connected(html=None):
    """
    Check if the user successfuly connected.

    Parameters :
    html -- source of the last downloaded page
    """
    if sid:
        if html != None:
            d = PyQuery(html)
            for l in d(".mainmenu"):
                if l.get("href", "") == "/login":
                    return False
        return True
    return False

def get(path, **kwargs):
    r = _get(path, **kwargs)

    n = 1
    while r.status_code == 503 or not connected(r.text):
        if n > 4:
            raise UnableToConnect()
        n+=1

        # If the connection failed two times : wait
        if n > 2:
            time.sleep(30)
        
        try:
            connect()
        except UnableToConnect:
            continue
        r = _get(path, **kwargs)
        
    return r

def get_admin(path, **kwargs):
    if not tid:
        connect()

    if not "params" in kwargs:
        kwargs["params"] = {}

    kwargs["params"]["extended_admin"] = 1
    kwargs["params"]["tid"] = tid
        
    return get(path, **kwargs)
