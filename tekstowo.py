from bs4 import BeautifulSoup
import requests

def main():
    import argparse

    parser = argparse.ArgumentParser(description="CLI tekstowo wrapper.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g", help="get song lyrics [URL]", action = "store_true")
    group.add_argument("-a", help="returns all songs of an artist [name]", action = "store_true")
    group.add_argument("-s", help="search for an n amount of things", type = str, action = "store", metavar="type", choices = ["artist","song"])
    group.add_argument("-i", help="get info from the website [URL]", action = "store_true")
    group.add_argument("-x", help="returns all songs lyrics in one go [name]", action = "store_true")
    parser.add_argument("name_url", help="of an artist or song")
    parser.add_argument("amount", help="of displayed results", default=10, nargs="?")

    args = parser.parse_args()
    def _webStr(stri):
        r = ""
        tc = {" ":"_"}
        for i in stri:
            if i in tc:
                r += tc[i]
            else:
                r += i
        return r

    tekstowo = Tekstowo(headers=None)

    if args.g:
        if args.name_url[0] != "/":
            print("ERROR: url invalid")
            return -1
        print(tekstowo.getText(args.name_url))
        return 0

    elif args.a:
        x = tekstowo.getLyricURLs(_webStr(args.name_url))
        for i in x:
            print(i + ": " + x[i])
        return 0

    elif args.s:
        if args.s == "artist":
            x = tekstowo.searchArtist(_webStr(args.name_url),int(args.amount))
        if args.s == "song":
            x = tekstowo.searchSong(_webStr(args.name_url),int(args.amount))

        for i in x:
            print(i + ": " + x[i])
        return 0

    elif args.i:
        x = tekstowo.getSongInfo(args.name_url)
        for i in x:
            print(str(i) + ": " + str(x[i]))
        return 0

    elif args.x:
        urls = tekstowo.getLyricURLs(_webStr(args.name_url))
        for url in urls:
            print(tekstowo.getText(urls[url]))
        return 0

class Tekstowo:

    headers = {}

    website = {"artistSearch"   :  """http://www.tekstowo.pl/szukaj,wykonawca,{},strona,{}.html""",
               "songSearch"     :  """http://www.tekstowo.pl/szukaj,wykonawca,,tytul,{},strona,{}.html""",
               "website"        :  """http://www.tekstowo.pl{}""",
               "artistSongs"    :  """http://www.tekstowo.pl/piosenki_artysty,{},alfabetycznie,strona,{}.html"""}

    def __init__(self,headers=None):
        self.headers = headers

    def _getMultiPageContent(self, thing, query, page):
        things = {}
        page = self._getWebsite(self.website[thing].format(query,page))
        if thing in ["artistSearch","songSearch"]:
            URLRaw = page.find(id="center").find_all("div","content")[0].find_all("div","box-przeboje")
        else:
            URLRaw = page.find_all("div","ranking-lista")[0].find_all("div","box-przeboje")
        for entry in URLRaw:
            position = entry.find_all("a","title")[0]
            things[position.get("title")] = position.get("href")
        return things

    def _getWebsite(self,url):
        site = requests.get(url,headers=self.headers).text
        site = str(bytes(site,"ISO-8859-1"),"utf-8").strip("\n")
        return BeautifulSoup(site,"html5lib")


    def getText(self,url):
        try:
            text = self._getWebsite(self.website["website"].format(url)).find_all("div","song-text")[0].get_text()
        except IndexError as e:
            return ""
        return text[65:-130].lstrip().rstrip()

    def searchArtist(self,artistName,amount=10):
        artists = {}
        page = self._getWebsite(self.website["artistSearch"].format(artistName,1))
        noPages = page.find_all("div","padding")
        if noPages == [] or amount < 30:
            artists = self._getMultiPageContent("artistSearch", artistName, 1)
        else:
            pages = int(noPages[0].find_all("a","page")[1::-1][0].get_text())
            for site in range(1,pages+1):
                artists.update(self._getMultiPageContent("artistSearch",artistName,site))
                if len(artists) < amount:
                    break
        slicedArtists = {}
        for i in artists:
            slicedArtists.update({i:artists[i]})
            if len(slicedArtists) == amount:
                break
        return slicedArtists

    def searchSong(self,name,amount=10):
        songs = {}
        page = self._getWebsite(self.website["songSearch"].format(name,1))
        noPages = page.find_all("div","padding")
        if noPages == [] or amount < 30:
            songs = self._getMultiPageContent("songSearch",name, 1)
        else:
            pages = int(noPages[0].find_all("a","page")[1::-1][0].get_text())
            for site in range(1,pages+1):
                songs.update(self._getMultiPageContent("songSearch",name,site))
                if len(songs) < amount:
                    break
        slicedSongs = {}
        for i in songs:
            slicedSongs.update({i:songs[i]})
            if len(slicedSongs) == amount:
                break
        return slicedSongs

    def getSongInfo(self,url):
        info = {}
        page = self._getWebsite(self.website["website"].format(url))
        odslon = page.find_all("div","odslon")[0].getText().replace("Odsłon: ","")
        info.update({"Odslony":int(odslon)})
        table = page.find_all("div","metric")[0].tbody.find_all("tr")
        for entry in table:
            info.update({entry.th.getText()[:-1:]:entry.td.p.getText()})
        return info

    def getLyricURLs(self, artistName):
        songs = {}
        page = self._getWebsite(self.website["artistSongs"].format(artistName,1))
        noPages = page.find_all("div","padding")
        if noPages == []:
            return self._getMultiPageContent("artistSongs",artistName, 1)
        else:
            pages = int(noPages[0].find_all("a","page")[1::-1][0].get_text())
            for site in range(1,pages+1):
                songs.update(self._getMultiPageContent("artistSongs",artistName,site))
        return songs

if __name__ == "__main__":
    main()