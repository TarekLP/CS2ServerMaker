class Tools:
    @staticmethod
    def GetValidMapsIDsFromSteamWebAPIList(listOfMaps: list) -> list:
        validMaps = []
        for map_item in listOfMaps: # Renamed 'map' to 'map_item' to avoid shadowing the built-in map() function
            if ("filetype" in map_item and map_item["filetype"] != 0): # Added check for "filetype" key existence
                # not a map
                continue
            # Some workshop items might not have 'filetype' explicitly or it might be 0 for generic items.
            # We need to rely on tags for accurate classification in CS2 context.
            # Assuming if it's in the children list of a collection, and not filtered by "filetype" (if present), it's a map ID.
            # The actual map validation (tags, app_id) happens in GetPublishedFileDetails
            if "publishedfileid" in map_item: # Ensure publishedfileid exists
                validMaps.append(map_item["publishedfileid"])
        return validMaps

    @staticmethod
    def SteamFileHasTag(fileTags: list, tagToSearch: str) -> bool:
        for tag in fileTags:
            if tag.get("tag") == tagToSearch: return True # Used .get() for safer dictionary access

        return False
    
    @staticmethod
    def IsMapIdAlreadyInList(mapList: dict, mapId: int) -> bool:

        for _map_name in mapList: # Iterating over keys (map names)
            if mapList[_map_name]["id"] == mapId:
                return True
        return False