from tools import Tools
from dataStructs import CSMap, SteamCollection, SteamFileElement
from steamWebAPI import SteamWebAPI
from exceptions import CollectionIsNotPublicException, CollectionNotFoundException, SteamFileElementIsAnIncompatibleMap, SteamFileElementIsNotACS2Item, SteamFileElementIsNotPublicException, SteamFileElementNotFoundException


class MapDataWrapper:
    """
    class to handle map data (collections, maps etc.)
    """
    isFeatureActivated = True       # Saved in preset.json

    collections: list = []          # Saved in preset.json
    mapsFromCollectionCache = []

    manuallyAddedMaps: list = []    # Saved in preset.json

    @staticmethod
    def Clear()->None:
        MapDataWrapper.isFeatureActivated = True
        MapDataWrapper.collections = []
        MapDataWrapper.mapsFromCollectionCache = []
        MapDataWrapper.manuallyAddedMaps = []

    @staticmethod
    def SerializeCollections()->list:
        _col = []

        for collection in MapDataWrapper.collections:
            if(not isinstance(collection, SteamCollection)): # Changed type() to isinstance()
                continue

            _col.append(collection.ToDict())

        return _col

    @staticmethod
    def DeserializeCollections(serializedList: list)->list:
        _col = []
        if(not isinstance(serializedList, list)): # Changed type() to isinstance()
            return _col
        
        for collection in serializedList:
            if(not isinstance(collection, dict)): # Changed type() to isinstance()
                continue

            if("id" not in collection.keys()):
                continue

            _c = SteamCollection(collection["id"], collection["url"], collection["name"], collection["mapIds"])
            _col.append(_c)

        return _col

    @staticmethod
    def SerializeManuallyAddedMaps()->list:
        _maps = []

        for map_item in MapDataWrapper.manuallyAddedMaps:
            if(not isinstance(map_item, CSMap)): # Changed type() to isinstance()
                continue

            _maps.append(map_item.ToDict())

        return _maps

    @staticmethod
    def DeserializeManuallyAddedMaps(serializedList: list)->list:
        _maps = []
        if(not isinstance(serializedList, list)): # Changed type() to isinstance()
            return _maps
        
        for map_item in serializedList:
            if(not isinstance(map_item, dict)): # Changed type() to isinstance()
                continue

            if("publishedfileid" not in map_item.keys()):
                continue

            _m = CSMap(map_item["publishedfileid"], map_item["creator"], map_item["title"], map_item["tags"])
            _maps.append(_m)

        return _maps
    
    @staticmethod
    def SaveConfig(ptr_config: dict) -> None:
        ptr_config["isFeatureActivated"]    = MapDataWrapper.isFeatureActivated
        ptr_config["collections"]           = MapDataWrapper.SerializeCollections()
        ptr_config["manuallyAddedMaps"]     = MapDataWrapper.SerializeManuallyAddedMaps()

    @staticmethod
    def SaveConfigPtr(ptr_config: dict) -> None:
        ptr_config["isFeatureActivated"]    = MapDataWrapper.isFeatureActivated
        ptr_config["collections"]           = MapDataWrapper.SerializeCollections()
        ptr_config["manuallyAddedMaps"]     = MapDataWrapper.SerializeManuallyAddedMaps()

    @staticmethod
    def LoadConfig(config: dict) -> None:
        MapDataWrapper.isFeatureActivated   = config.get("isFeatureActivated", True)
        MapDataWrapper.collections          = MapDataWrapper.DeserializeCollections(config.get("collections", []))
        MapDataWrapper.manuallyAddedMaps    = MapDataWrapper.DeserializeManuallyAddedMaps(config.get("manuallyAddedMaps", []))

    @staticmethod
    def AddCollection(collectionId: int, ptr_error: list = []) -> bool:
        """
        Add a collection to the list and caches its maps if the feature is activated
        ptr_error: returns list of errors found (from exceptions)
        """
        try:
            _collection = SteamWebAPI.GetCollectionDetails(collectionId)
            
            if(not isinstance(_collection, SteamCollection)): # Changed type() to isinstance()
                ptr_error.append({"UnknownError":"unknown error when retrieving collection"})
                return False

            MapDataWrapper.collections.append(_collection)
            return True
        except CollectionNotFoundException:
            ptr_error.append({"CollectionNotFoundException":f"Collection {collectionId} not found"})
        except CollectionIsNotPublicException:
            ptr_error.append({"CollectionIsNotPublicException":f"Collection {collectionId} is not public"})
        except Exception as e:
            ptr_error.append({"Error":f"An unexpected error occurred: {e}"})
        return False
        
    @staticmethod
    def AddManuallyAddedMap(mapId: int, ptr_error: list = []) -> bool:
        """
        Add a map to the list of manually added maps
        ptr_error: returns list of errors found (from exceptions)
        """
        try:
            _file = SteamWebAPI.GetPublishedFileDetails(1, [mapId])[0] # GetPublishedFileDetails returns a list

            if(not isinstance(_file, SteamFileElement)): # Changed type() to isinstance()
                ptr_error.append({"UnknownError":"unknown error when retrieving map"})
                return False

            MapDataWrapper.manuallyAddedMaps.append(_file.ToCSMap())
            return True
        except SteamFileElementIsNotACS2Item:
            ptr_error.append({"SteamFileElementIsNotACS2Item":f"Map {mapId} is not a CS2 item"})
        except SteamFileElementIsNotPublicException:
            ptr_error.append({"SteamFileElementIsNotPublicException":f"Map {mapId} is not public"})
        except SteamFileElementIsAnIncompatibleMap:
            ptr_error.append({"SteamFileElementIsAnIncompatibleMap":f"Map {mapId} is an incompatible map"})
        except SteamFileElementNotFoundException:
            ptr_error.append({"SteamFileElementNotFoundException":f"Map {mapId} not found"})
        except Exception as e:
            ptr_error.append({"Error":f"An unexpected error occurred: {e}"})
        return False

    @staticmethod
    def CacheMapsFromCollections(ptr_error: list = []) -> bool:
        """
        Will cache all maps from all collections
        ptr_error: returns list of errors found (from exceptions)
        """
        if(not MapDataWrapper.isFeatureActivated):
            return False

        MapDataWrapper.mapsFromCollectionCache = []

        _maps = SteamWebAPI.GetMapsFromCollectionsList(MapDataWrapper.collections)

        for file in _maps:
            if(not isinstance(file, CSMap)): # Changed type() to isinstance()
                continue
            
            MapDataWrapper.mapsFromCollectionCache.append(file)

        if(MapDataWrapper.manuallyAddedMaps == [] and MapDataWrapper.mapsFromCollectionCache == []): # Added check for mapsFromCollectionCache as well
            ptr_error.append({"SteamFileElementNotFoundException":"no compatible or public files were found."})
            return False

        return True

    @staticmethod
    def GetFinalMapIDs(CacheCollections = True)->dict:
        """
        returns all the ids with map names for ui list (no dupplicates)

        will cache maps by default (CacheCollections = True param)
        """

        if(CacheCollections):
            MapDataWrapper.CacheMapsFromCollections()

        _maps: dict = {}

        for cachedMap in MapDataWrapper.mapsFromCollectionCache:
            if(not isinstance(cachedMap, CSMap)): # Changed type() to isinstance()
                continue

            if(Tools.IsMapIdAlreadyInList(_maps, cachedMap.publishedfileid)):
                continue

            if(cachedMap.title in _maps.keys()):
                continue
            
            _maps[cachedMap.title] = {"id":cachedMap.publishedfileid,"tags":cachedMap.tags}

            
        for manuallyAddedMap in MapDataWrapper.manuallyAddedMaps:
            if(not isinstance(manuallyAddedMap, CSMap)): # Changed type() to isinstance()
                continue

            if(Tools.IsMapIdAlreadyInList(_maps, manuallyAddedMap.publishedfileid)):
                continue

            if(manuallyAddedMap.title in _maps.keys()):
                continue
            
            _maps[manuallyAddedMap.title] = {"id":manuallyAddedMap.publishedfileid, "tags":manuallyAddedMap.tags}

        return _maps