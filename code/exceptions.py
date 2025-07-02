class CollectionNotFoundException(Exception):
    "Raised when the remote collection does not exist"
    pass

class CollectionIsNotPublicException(Exception):
    "Raised when the remote collection is not set to public. Can't retreive maps"
    pass

class SteamFileElementIsNotPublicException(Exception):
    "Raised when the remote file is not set to public"
    pass

class SteamFileElementNotFoundException(Exception):
    "Raised when the remote file does not exist"
    pass
    
class SteamFileElementIsAnIncompatibleMap(Exception):
    "Raised when the remote file is an old version of the map"
    pass

class SteamFileElementIsNotACS2Item(Exception):
    "Raised when the remote file is not made for cs2/csgo (appid != 730)"
    pass
