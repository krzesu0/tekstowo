import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from . import urls
from . import exceptions

month = {"stycznia": 1,
         "lutego": 2,
         "marca": 3,
         "kwietnia": 4,
         "maja": 5,
         "czerwca": 6,
         "lipca": 7,
         "sierpnia": 8,
         "września": 9,
         "października": 10,
         "listopada": 11,
         "grudnia": 12}


def parseSite(requestObj):
    page = BeautifulSoup(requestObj, "html5lib")
    return page


def urlEncode(url):
    return quote_plus(url)


class Defaults():
    _login_headers = {
        "Referer": urls.login,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
    }
    _use_headers = {
        "Accept-Encoding": "gzip",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
    }
    proxies = {}
    headers = {}


class TekstowoSession():
    """Utilities class, for user auth."""

    __jar = requests.Session()
    is_logged = False
    username = None

    def __init__(self, login=None, password=None):
        if(login is None or password is None):
            return
        self.login(login, password)

    def login(self, login, password):
        # won't relogin, PHPSESS is still valid
        # if logged in, it wouldnt even let you login again (i think)
        if(not self.is_logged):
            payload = {"login": login, "haslo": password}
            self.__jar = requests.sessions.Session()
            ret = self.__jar.post(urls.login,
                                  data=payload,
                                  headers=Defaults._login_headers)
            # when login is succesful it redirects to /, if bad it stays at /logowanie.html
            # ~~i could also check if session cookie is set, but i think this
            # also should work~~. it doesent work, session cookie is set immediately
            # on first page lookup, later its just assigned as logged in.
            if(ret.ok):
                if(ret.url == urls.login):
                    raise exceptions.TekstowoUnableToLogin("Bad login or password")
                self.is_logged = True
            else:
                raise exceptions.TekstowoBadSite("ret.ok is not ok")

    def logout(self):
        # can't logout when not logged in. stupid
        # technically unnecessary but better to
        if(self.is_logged):
            self.__jar.get(urls.logout)
            self.__jar = requests.Session()

    def __del__(self):
        self.logout()

    def get(self, url, *args, **kwargs):
        return parseSite(self.raw_get(url, *args, **kwargs))

    def raw_get(self, url, *args, **kwargs):
        requestObj = self.__jar.get(url, *args, **kwargs)
        try:
            if requestObj.status_code != 200:
                raise exceptions.TekstowoBadSite("Status code != 200")
        except Exception:
            raise("No network connection, bad proxy, or bad URL")
        return str(bytes(requestObj.text, "ISO-8859-1"), "utf-8").strip("\n")
