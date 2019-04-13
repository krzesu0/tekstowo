from . import artist
from . import comment
from . import utils


class Lyrics:
    """Class for storing song lyrics and some info about them.
    Local variables:
     - artist (str)
     - songName (str)
     - url (str)
     - hasText (bool)
     - hasTranslation (bool)
     - text (str) # Very long string, TODO: fix it later
     - translation (str)
     - artistUrl (str)
     - comment count (int)
     - id (int)
     - upVotes (int)

    Local methods: # rather self explanatory
     - getComments
     - getArtistObject
    """

    utils = utils.Utils()

    def __init__(self, page):
        """Initialized with site to parse (lyrics page)"""
        if str(type(page)) != "<class 'bs4.BeautifulSoup'>":
            raise("Passed page is not a BeautifulSoup class")
        self.__parse__(page)

    def __str__(self):
        return "{artist}:{song}".format(artist=self.artist, song=self.songName)

    def __repr__(self):
        return "{artist}LyricsObject".format(artist=self.artist)

    def __getArtist(self, page):
        """Returns artist name"""
        artist_ = page.find_all("div", "left-corner")[0].find_all("a", "green")[2].get("title")
        return artist_

    def __getSongName(self, page):
        """Returns song name"""
        songname = page.find_all("div", "left-corner")[0].find_all("a", "green")[3].get("title")
        return songname

    def __getUrl(self, page):
        """Returns url of a page"""
        url = page.find_all("meta")
        for meta in url:
            if meta.get("property") == "og:url":
                return meta.get("content")

    def __hasText(self, page):
        """Returns True if song has text"""
        if page.find_all("div", "tekst")[0].find_all("div", "song-text"):
            return True
        else:
            return False

    def __getText(self, page):
        """Returns string with song lyrics"""
        text = page.find_all("div", "song-text")[0].get_text()
        return text[65:-130].lstrip().rstrip()

    def __hasTranslation(self, page):
        """Returns True if there is is translation for a given song"""
        if page.find_all("div", "tlumaczenie")[0].find_all("a", "pokaz-tlumaczenie")[0].get("title") == "Pokaż tłumaczenie":
            return True
        else:
            return False

    def __getTranslation(self, page):
        """Returns text translation for given page"""
        return page.find(id="translation").get_text()[:-130].lstrip().rstrip()

    def __getArtistUrl(self, page):
        try:
            return "http://www.tekstowo.pl" + page.find_all("a", "link-wykonawca")[0].get("href")
        except IndexError:
            return None

    def __getID(self, page):
        return int(page.find_all("a", "pokaz-rev")[0].get("song_id"))

    def __getCommentCount(self, page):
        return int(page.find_all("h2", "margint10")[0].getText().strip("Komentarze ():"))

    def __getUpVotes(self, page):
        return int(page.find_all("div", "glosowanie")[0].find_all("span", "rank")[0].getText().strip("(+)"))

    def __parse__(self, page):
        """Uses other functions to parse website for information"""
        self.artist       = self.__getArtist(page)
        self.songName     = self.__getSongName(page)
        self.url          = self.__getUrl(page)
        self.artistUrl    = self.__getArtistUrl(page)
        self.id           = self.__getID(page)
        self.commentCount = self.__getCommentCount(page)
        self.upVotes      = self.__getUpVotes(page)

        if self.__hasText(page):
            self.hasText = True
            self.text = self.__getText(page)
            # No need to check for translation if there is not even a normal text
            if self.__hasTranslation(page):
                self.hasTranslation = True
                self.translation = self.__getTranslation(page)
        else:
            self.hasText = False
            self.text = None
            self.hasTranslation = False
            self.translation = None

    def getComments(self, amount=30, startFrom=0):
        """Spaghetti code incoming...
        code used to download *amount* of comments starting from *startFrom*
        comment in order with its response

        returns [Comment]"""
        commentList = []
        amount = amount - 1
        start = 0
        while True:  # I shouldn't do that
            site = self.utils.getWebsite("http://www.tekstowo.pl/js,moreComments,S,{},{}".format(self.id, startFrom+start+len(commentList)))
            for comment_ in site.find_all("div", "komentarz"):
                childs = []
                username = comment_.a.get("title")
                content = comment_.find_all("div", "p")[0].get_text().strip()
                upVotes = comment_.find_all("div", "icons")[0].span.get_text()
                url = comment_.find_all("a")[0].get("href")
                id = comment_.find_all("div", "p")[0].div.get("id")[8:]
                time = comment_.find_all("div", "bar")[0].contents[2].split()[0]
                if "↓" in comment_.p.getText().strip():
                    replies = self.utils.getWebsite("http://www.tekstowo.pl/js,showParent,{}".format(id))
                    for reply in replies.find_all("div", "komentarz "):
                        reply_username = comment_.a.get("title")
                        reply_content = comment_.find_all("div", "p")[0].get_text().strip()
                        reply_url = comment_.find_all("a")[0].get("href")
                        reply_time = comment_.find_all("div", "bar")[0].contents[2].split()
                        childs.append(comment.Comment(reply_username, reply_content, None, reply_time, reply_url, None))
                commentList.append(comment.Comment(username, content, id, time, upVotes, url, childs))
                if not(len(commentList) <= amount):
                    return commentList
        # Failsafe
        return []

    def getArtistObject(self):
        """returns artist class"""
        return artist.Artist(self.utils.getWebsite(self.artistUrl))