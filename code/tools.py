
class Tools:
    @staticmethod
    def GetValidMapsIDsFromSteamWebAPIList(listOfMaps: list) -> list:
        validMaps = []
        for map in listOfMaps:
            if (map["filetype"] != 0):
                # not a map
                continue
            validMaps.append(map["publishedfileid"])
        return validMaps

    @staticmethod
    def SteamFileHasTag(fileTags: list, tagToSearch: str) -> bool:
        for tag in fileTags:
            if tag["tag"] == tagToSearch: return True

        return False
    
    @staticmethod
    def IsMapIdAlreadyInList(mapList: dict, mapId: int) -> bool:

        for _map in mapList:
            if mapList[_map]["id"] == mapId:
                return True
        return False