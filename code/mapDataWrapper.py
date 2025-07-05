from dataStructs import CSMap, SteamCollection
from steamWebAPI import SteamWebAPI
from exceptions import CollectionIsNotPublicException, CollectionNotFoundException, SteamFileElementIsAnIncompatibleMap, SteamFileElementIsNotACS2Item, SteamFileElementIsNotPublicException


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
            if(type(collection) != SteamCollection):
                continue

            _col.append(collection.ToDict())

        return _col

    @staticmethod
    def DeserializeCollections(serializedList: list)->list:
        _col = []
        if(type(serializedList) != list):
            return _col
        
        for collection in serializedList:
            if(type(collection) != dict):
                continue

            if("id" not in collection.keys()):
                continue

            _c = SteamCollection(collection["id"],  collection["url"] or "",  collection["name"] or "",  collection["mapIds"] or [])
            _col.append(_c)
        
        return _col

    @staticmethod
    def SerializeManuallyAddedMaps()->list:
        _col = []

        for csmap in MapDataWrapper.manuallyAddedMaps:
            if(type(csmap) != CSMap):
                continue

            _col.append(csmap.ToDict())
            
        return _col

    @staticmethod
    def DeserializeManuallyAddedMaps(serializedList: list)->list:
        _col = []
        if(type(serializedList) != list):
            return _col
        
        for csmap in serializedList:
            if(type(csmap) != dict):
                continue

            if("publishedfileid" not in csmap.keys()):
                continue

            _c = CSMap(csmap["publishedfileid"],  csmap["creator"] or 0,  csmap["title"] or "",  csmap["tags"] or [])
            _col.append(_c)
        
        return _col


    @staticmethod
    def LoadFromConfig(config_data: dict):
        """
        loads config data into the static variables from dict (json)
        """
        MapDataWrapper.isFeatureActivated   = MapDataWrapper.DeserializeCollections(config_data.get("mapDataWrapper_isFeatureActivated", True))
        MapDataWrapper.collections          = MapDataWrapper.DeserializeCollections(config_data.get("mapDataWrapper_collections", []))
        MapDataWrapper.manuallyAddedMaps    = MapDataWrapper.DeserializeManuallyAddedMaps(config_data.get("mapDataWrapper_manuallyAddedMaps", []))
    
    @staticmethod
    def SaveConfig(config_data: dict)->dict:
        """
        returns the config data with updated fields
        """
        _config_data = config_data.copy()

        _config_data["mapDataWrapper_isFeatureActivated"]    = MapDataWrapper.isFeatureActivated
        _config_data["mapDataWrapper_collections"]           = MapDataWrapper.SerializeCollections()
        _config_data["mapDataWrapper_manuallyAddedMaps"]     = MapDataWrapper.SerializeManuallyAddedMaps()

        return _config_data
    
    @staticmethod
    def SaveConfigPtr(ptr_config_data: dict = {})->None:
        """
        ptr_config_data is an Mutable list, used as pointer (see Mutable data documentation: https://docs.python.org/3/reference/datamodel.html)
        
        used update data at memory pointer
        """

        if(type(ptr_config_data) != dict):
            return
        
        ptr_config_data["mapDataWrapper_isFeatureActivated"]    = MapDataWrapper.isFeatureActivated
        ptr_config_data["mapDataWrapper_collections"]           = MapDataWrapper.SerializeCollections()
        ptr_config_data["mapDataWrapper_manuallyAddedMaps"]     = MapDataWrapper.SerializeManuallyAddedMaps()

    @staticmethod
    def IsCollectionAllreadyAdded(collectionId)->bool:
        """
        iterates on every collections added and check if the collectionId parametter matches with one
        of the registered collections.
        """
        for collection in MapDataWrapper.collections:
            if(type(collection) != SteamCollection):
                continue
            if(collection.id == collectionId):
                return True
        return False

    @staticmethod
    def DoesMapListContainsMap(mapList: list, mapId: int)->bool:
        """
        iterates on every collections in the given list and check if the collectionId parametter matches with one
        of the registered collections.

        mapList is a list of SteamCollections
        """
        for map in mapList:
            if(type(map) != CSMap):
                continue
            if(map.publishedfileid == mapId):
                return True
        return False

    @staticmethod
    def DoesMapCacheContainsMap(mapId: int)->bool:
        """
        iterates on every collections added and check if the collectionId parametter matches with one
        of the registered collections.
        """
        return MapDataWrapper.DoesMapListContainsMap(MapDataWrapper.mapsFromCollectionCache, mapId)

    @staticmethod
    def RegisterNewCollection(collectionId: int = 0, forceRegister: bool = False, ptr_error: list = [])->bool:
        """
        register into collections static variable a steam collection from id
        
        forceRegister indicates if the collection should be added even though it's already present in the collection list

        ptr_error is an mutable variable to get error logs

        @throws gaierror: web socket error, raised when no connection, must be handled

        @returns Registration State: True = Success, False = Error
        """
        try:
            if(MapDataWrapper.IsCollectionAllreadyAdded(collectionId) and not forceRegister):
                ptr_error.append({"CollectionAllreadyAdded":"The collection with id "+str(collectionId)+" has already been added to the steam collection list, wont register again"})
                return False

            _col = SteamWebAPI.GetCollectionsDetails(1, [collectionId], False)

            MapDataWrapper.collections.append(_col[0])

            return True

        except CollectionNotFoundException as e:
            ptr_error.append({"CollectionNotFoundException":"The collection with id "+str(collectionId)+" could not be found"})
            return False
        except CollectionIsNotPublicException as e:
            ptr_error.append({"CollectionIsNotPublicException":"The collection with id "+str(collectionId)+" appears to not be public, therefor cannot be accessed"})
            return False

    @staticmethod
    def CacheMapsFromCollections(ptr_error: list = [])->bool:
        """
        Caches maps from the collections static list into the mapsFromCollectionCache

        ptr_error is an Mutable list used for error logging

        @throws gaierror: web socket error, raised when no connection, must be handled
        """
        if(MapDataWrapper.collections == []):
            ptr_error.append({"SteamCollectionListIsEmpty":"the steam collections list is empty. cannot cache"})
            return False
        
        try:
            _mapCache = SteamWebAPI.GetMapsFromCollectionsList(MapDataWrapper.collections)
        except SteamFileElementIsNotPublicException as e:
            ptr_error.append({"SteamFileElementIsNotPublicException":"could not find any public maps in the given collection.s to cache."})
            return False
        except SteamFileElementIsNotACS2Item as e:
            ptr_error.append({"SteamFileElementIsNotACS2Item":"could not find any maps in the given collection.s to cache."})
            return False
        except SteamFileElementIsAnIncompatibleMap as e:
            ptr_error.append({"SteamFileElementIsAnIncompatibleMap":"could not find any compatible maps in the given collection.s to cache."})
            return False

        if(_mapCache == []):
            ptr_error.append({"SteamFileElementIsAnIncompatibleMap":"could not find any compatible or public maps in the given collections to cache."})
            return False

        MapDataWrapper.mapsFromCollectionCache = _mapCache.copy()

        return True
    
    @staticmethod
    def ManuallyRegisterMaps(mapIds:list = [], ptr_error: list = [])->bool:
        """
        adds maps to the manuallyAddedMaps static variable

        non public maps will be added with empty information, public maps will be added with file information from steam

        mapIds: list<int> = list of your map ids to add, make an array of one element if you want to add a single file

        ptr_error: list = the mutable variable for error logging
        """
        print("TODO: Not Implmented (MapDataWrapper.ManuallyRegisterMap())")
        return False