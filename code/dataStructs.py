
#
#   DATA STRUCTURES
#
class SteamCollection:
    """
    Steam Collection Meta Implementation
    """

    id: int = 0
    url: str = ""
    name: str = ""

    mapIds: list = []

    def __init__(self, id: int, url: str, name: str, mapIds: list):
        self.id                 = id
        self.url                = url
        self.name               = name

        self.mapIds             = mapIds

    def ToDict(self) -> map:
        return {"id":self.id, "url":self.url, "name":self.name, "mapIds":self.mapIds}

class CSMap:
    """
    Counter Strike 2 map
    """
    publishedfileid: int    = 0
    creator: int            = 0
    title: str              = ""
    tags: list              = []
    def __init__(self, publishedfileid: int = 0, creator: int = 0, title: str = "", tags: list = []):
        self.publishedfileid    = publishedfileid
        self.creator            = creator
        self.title              = title
        self.tags               = tags

    def ToDict(self) -> map:
        return {"publishedfileid":self.publishedfileid, "creator":self.creator, "title":self.title, "tags":self.tags }

class SteamFileElement:
    """
    a common wrapper for steam file elements (including collections, maps, items etc.)
    it's the response of GetPublishedFileDetails
    """
    publishedfileid: int    = 0
    creator: int            = 0
    title: str              = ""
    tags: list              = []
    fileType: str           = ""

    def __init__(self, publishedfileid: int = 0, creator: int = 0, title: str = "", tags: list = [], fileType: str = "Unknown"):
        self.publishedfileid    = publishedfileid
        self.creator            = creator
        self.title              = title
        self.tags               = tags
        self.fileType               = fileType

    def ToDict(self) -> map:
        return {"publishedfileid":self.publishedfileid, "creator":self.creator, "title":self.title, "tags":self.tags , "fileType":self.fileType }

    def ToCSMap(self) -> CSMap:
        _map = CSMap(self.publishedfileid, self.creator, self.title, self.tags)
        return _map
