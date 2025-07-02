
from http import client
import json
import os

from tools import Tools
from exceptions import CollectionIsNotPublicException, CollectionNotFoundException, SteamFileElementIsAnIncompatibleMap, SteamFileElementIsNotACS2Item, SteamFileElementIsNotPublicException, SteamFileElementNotFoundException
from dataStructs import CSMap, SteamCollection, SteamFileElement

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
    def ParseData(data: map) -> str:
        """
        Parse data from map to x-www-form-urlencoded format
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
    def SendRequest(url: str, data: map, method = "POST", verbose: bool = False) -> map:
        """
        Sends HTTP request with x-www-form-urlencoded format body
        """
        connection = client.HTTPSConnection(SteamWebAPI.steam_api_base_url)

        connection.request(method, url, body = SteamWebAPI.ParseData(data), headers = {"Content-type":"application/x-www-form-urlencoded"})

        return json.loads(connection.getresponse().read())
    
    @staticmethod
    def TestConnectivity()-> bool:
        """
        Test Connectivity to steam web api services
        """
        try:
            # Test Ping on Steam API
            connection = client.HTTPSConnection(SteamWebAPI.steam_api_base_url)

            connection.request("GET", "/")

            return True
        except:
            return False

    @staticmethod
    def GetCollectionsDetails(collectioncount: int, publishedfileids: list, verbose: bool = False, raiseOnError = True) -> list:
        """
        Sends HTTP request with x-www-form-urlencoded format body
        """
        url = "/" + SteamWebAPI.steam_api_ISteamRemoteStorage_endpoint + "/GetCollectionDetails/" + SteamWebAPI.steam_api_version + "/"
        body = {
            'collectioncount': collectioncount,
        }

        i: int = 0
        for itemId in publishedfileids:
            if(type(itemId) != int):
                continue

            body['publishedfileids['+str(i)+']'] = itemId
            i+=1

        rawData = SteamWebAPI.SendRequest(url, body, verbose = verbose)

        if(len(rawData) == 0 and raiseOnError):
            raise CollectionNotFoundException()

        data = rawData["response"]["collectiondetails"]

        collectionList = []

        for collection in data:
            
            if("children" not in collection.keys()):
                if len(publishedfileids) == 1 and raiseOnError: raise CollectionIsNotPublicException()
                continue

            mapIds: list = Tools.GetValidMapsIDsFromSteamWebAPIList(collection["children"])


            url = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + str(collection["publishedfileid"])
            _col = SteamCollection(int(collection["publishedfileid"]), url, "", mapIds)

            collectionList.append(_col)

        return collectionList


        #x = requests.post(url, json = myobj)

        # if verbose: print ("[STEAM API] GetCollectionDetails")
        # if verbose: print ("[STEAM API] remote data:")

        #return SteamWebAPI.SendRequest(url, body, verbose = verbose)["response"]["collectiondetails"][0]

        # return x["response"]["collectiondetails"][0]

    @staticmethod
    def GetPublishedFileDetails(itemcount: int, publishedfileids: list, verbose: bool = False, raiseOnError = False) -> list:
        """
        Sends HTTP request with x-www-form-urlencoded format body
        """
        url = "/" + SteamWebAPI.steam_api_ISteamRemoteStorage_endpoint + "/GetPublishedFileDetails/" + SteamWebAPI.steam_api_version + "/"
        body = {
            'itemcount': itemcount,
        }

        i: int = 0
        for itemId in publishedfileids:
            # if(type(itemId) != int):
            #     continue

            body['publishedfileids['+str(i)+']'] = itemId
            i+=1

        rawData = SteamWebAPI.SendRequest(url, body, verbose = verbose)

        if(len(rawData) == 0 and raiseOnError):
            raise SteamFileElementNotFoundException()

        data = rawData["response"]["publishedfiledetails"]

        steamElementsList = []

        for element in data:
            
            if("creator" not in element.keys()):
                if len(publishedfileids) and raiseOnError: raise SteamFileElementIsNotPublicException()
                continue
            
            fileType: str = "unkown"
            
            if(element["consumer_app_id"] != 730):
                if len(publishedfileids) and raiseOnError: raise SteamFileElementIsNotACS2Item()
                continue
            elif(element["creator_app_id"] == 766):
                fileType = "Collection"
            elif(Tools.SteamFileHasTag(element["tags"], "Other")):
                fileType = "Other"
            elif(not Tools.SteamFileHasTag(element["tags"], "Cs2") and not Tools.SteamFileHasTag(element["tags"], "CS2")):
                if len(publishedfileids) and raiseOnError: raise SteamFileElementIsAnIncompatibleMap()
                continue
            elif(Tools.SteamFileHasTag(element["tags"], "Map")):
                fileType = "Map"
            elif(Tools.SteamFileHasTag(element["tags"], "Weapon Finish")):
                fileType = "Weapon Finish"

            _steamElement = SteamFileElement(element["publishedfileid"], element["creator"], element["title"], element["description"], element["tags"], fileType)
            steamElementsList.append(_steamElement)

        return steamElementsList
    

    
    @staticmethod
    def GetMapsFromCollectionsList(collections: list):
        """
        Get Valid maps for every collections
        will ignore dupplicates
        collections: list elements must be of type SteamCollection, every element not of this type will be ignored
        """
        mapIDs = []

        for collection in collections:
            if(type(collection) != SteamCollection):
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
            if(type(file) != SteamFileElement):
                continue

            if(file.fileType != "Map"):
                continue

            maps.append(file.ToCSMap())

        return maps