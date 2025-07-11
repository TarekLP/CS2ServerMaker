from http import client
import json
import os

from tools import Tools
from exceptions import CollectionIsNotPublicException, CollectionNotFoundException, SteamFileElementIsAnIncompatibleMap, SteamFileElementIsNotACS2Item, SteamFileElementIsNotPublicException, SteamFileElementNotFoundException
from dataStructs import SteamCollection, SteamFileElement

#
#   STEAM WEB API
#

class SteamWebAPI:
    """
    Simple Wrapper for steam web api calls
    """

    steam_api_base_url: str = "api.steampowered.com"
    steam_api_version: str = "v1"

    steam_api_ISteamRemoteStorage_endpoint: str = "ISteamRemoteStorage"


    @staticmethod
    def ParseData(data: dict) -> str: # Changed map to dict
        """
        Parse data from dict to x-www-form-urlencoded format
        """
        datastr = ""

        i: int = 0
        for fieldKey in data.keys():
            if(i!= 0):
                datastr += "&"

            datastr += fieldKey
            datastr += "="
            datastr += str(data[fieldKey])

            i+=1

        return datastr

    @staticmethod
    def SendRequest(url: str, data: dict, method = "POST", verbose: bool = False) -> dict: # Changed map to dict
        """
        Sends HTTP request with x-www-form-urlencoded format body
        """
        connection = client.HTTPSConnection(SteamWebAPI.steam_api_base_url)

        connection.request(method, url, body = SteamWebAPI.ParseData(data), headers = {"Content-type":"application/x-www-form-urlencoded"})

        response = connection.getresponse()
        response_data = response.read().decode('utf-8')
        connection.close()

        if(verbose):
            print(f"Request URL: {url}")
            print(f"Request Data: {data}")
            print(f"Response Status: {response.status}")
            print(f"Response Reason: {response.reason}")
            print(f"Response Data: {response_data}")

        return json.loads(response_data)

    @staticmethod
    def GetCollectionDetails(collectionId: int) -> SteamCollection:
        data = {
            "collectioncount": 1,
            "publishedfileids[0]": collectionId
        }

        resp = SteamWebAPI.SendRequest(f"/{SteamWebAPI.steam_api_ISteamRemoteStorage_endpoint}/GetCollectionDetails/{SteamWebAPI.steam_api_version}/", data)

        if (resp["response"]["result"] != 1): # 1 means success
            raise CollectionNotFoundException()
        
        if (resp["response"]["collectiondetails"][0]["result"] != 1): # 1 means success
            raise CollectionIsNotPublicException()

        _collection = resp["response"]["collectiondetails"][0]

        _mapIds = Tools.GetValidMapsIDsFromSteamWebAPIList(_collection["children"])

        return SteamCollection(_collection["publishedfileid"], _collection["creator"], _collection["title"], _mapIds)

    @staticmethod
    def GetPublishedFileDetails(fileCount: int, fileids: list, raiseOnError: bool = True) -> list:
        data = {
            "itemcount": fileCount
        }
        for i, file_id in enumerate(fileids):
            data[f"publishedfileids[{i}]"] = file_id

        resp = SteamWebAPI.SendRequest(f"/{SteamWebAPI.steam_api_ISteamRemoteStorage_endpoint}/GetPublishedFileDetails/{SteamWebAPI.steam_api_version}/", data)

        if (resp["response"]["result"] != 1): # 1 means success
            if raiseOnError: raise SteamFileElementNotFoundException()
            return []
        
        steamElementsList: list = []

        for element in resp["response"]["publishedfiledetails"]:
            if (element["result"] != 1): # 1 means success
                if raiseOnError: raise SteamFileElementIsNotPublicException()
                continue
            
            if (element["creator_app_id"] != 730): # 730 is CSGO/CS2 AppID
                if raiseOnError: raise SteamFileElementIsNotACS2Item()
                continue

            fileType = "Unknown"
            # filetype == 0 indicates a map (or other game content like a weapon finish)
            # We need to rely on tags to differentiate
            
            # The 'file_type' field from the API is usually 0 for workshop items.
            # We classify based on tags.
            if(Tools.SteamFileHasTag(element["tags"], "Legacy Map") and raiseOnError): raise SteamFileElementIsAnIncompatibleMap()
            
            if(Tools.SteamFileHasTag(element["tags"], "Map")):
                fileType = "Map"
            elif(Tools.SteamFileHasTag(element["tags"], "Weapon Finish")):
                fileType = "Weapon Finish"

            _steamElement = SteamFileElement(element["publishedfileid"], element["creator"], element["title"], element["tags"], fileType)
            steamElementsList.append(_steamElement)

        return steamElementsList
    
    @staticmethod
    def GetMapsFromCollectionsList(collections: list) -> list:
        """
        Get Valid maps for every collections
        will ignore dupplicates
        collections: list elements must be of type SteamCollection, every element not of this type will be ignored
        """
        mapIDs = []

        for collection in collections:
            if(not isinstance(collection, SteamCollection)): # Changed type() to isinstance()
                continue
            for mapId in collection.mapIds:
                if (mapId in mapIDs):
                    continue
                mapIDs.append(mapId)

        if (mapIDs == []):
            return []

        maps = []

        _tmpFiles = SteamWebAPI.GetPublishedFileDetails(len(mapIDs), mapIDs, False)

        for file in _tmpFiles:
            if(not isinstance(file, SteamFileElement)): # Changed type() to isinstance()
                continue

            if(file.fileType != "Map"):
                continue

            maps.append(file.ToCSMap())

        return maps