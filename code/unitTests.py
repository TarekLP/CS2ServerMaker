
from http import client
from socket import gaierror
from sys import argv
from cmdColors import bcolors
from exceptions import CollectionIsNotPublicException, CollectionNotFoundException
from dataStructs import SteamCollection, SteamFileElement
from steamWebAPI import SteamWebAPI

#
#   UNIT TESTS
#

class UnitTests:
    @staticmethod
    def TEST_WebConnection() -> bool:
        """
        Test Connectivity to steam web api services
        """
        return SteamWebAPI.TestConnectivity()

    @staticmethod
    def TEST_GetCollectionDetails() -> bool:
        """
        to test gathering valid collection details
        """
        data = SteamWebAPI.GetCollectionsDetails(1, [3513758895], True)

        expectedData = [SteamCollection(3513758895, "https://steamcommunity.com/sharedfiles/filedetails/?id=3513758895", "", ['3229373526', '3073797349', '626204362', '3130080493', '657428900', '580587145', '237611084', '836830191', '3088183343', '222213032', '3134280292'])]

        if(data[0].ToDict() != expectedData[0].ToDict()):
            print(data[0].ToDict())
            print(expectedData[0].ToDict())
            return False

        return True
    
    @staticmethod
    def TEST_GetNonPublicCollectionDetails() -> bool:
        """
        to test errors when collection is not public
        """
        try:
            data = SteamWebAPI.GetCollectionsDetails(1, [3514418698], True)
            return False
        except CollectionIsNotPublicException:
            return True
        except Exception as e:
            print(bcolors.FAIL, end="")
            print("not raising the right error (",type(e).__name__,")")
            print(bcolors.ENDC, end="")
            return False
    
    @staticmethod
    def TEST_CollectionNotFound() -> bool:
        """
        to test errors when collection is not public
        """
        try:
            data = SteamWebAPI.GetCollectionsDetails(1, [0], True)
            return False
        except CollectionNotFoundException:
            return True
        except Exception as e:
            print(bcolors.FAIL, end="")
            print("not raising the right error (",type(e).__name__,")")
            print(bcolors.ENDC, end="")
            return False

    @staticmethod
    def TEST_GetPublishedFileDetails() -> bool:
        """
        to test gathering valid collection details
        """
        data = SteamWebAPI.GetPublishedFileDetails(1, [3229373526], True)

        expectedData = [
            SteamFileElement(
                '3229373526',
                '76561198103562816',
                "Rond Point Express",
                "School project for ISART DIGITAL Paris Available/Compatible Game modes: - Casual & Competitive (defend the market) - Wingman (Defend the market) - Deathmatch (F4A and team deathmatch)\r\n\r\n\r\nUses Custom and ingame assets\r\n\r\nBeta workshop page:\r\nhttps://steamcommunity.com/sharedfiles/filedetails/?id=3178325186\r\n\r\nArtstation Post:\r\nhttps://www.artstation.com/artwork/LRKW2k",
                [{'tag': 'Classic'}, {'tag': 'Deathmatch'}, {'tag': 'Map'}, {'tag': 'Wingman'}, {'tag': 'Cs2'}],
                "Map")
            ]

        if(data[0].ToDict() != expectedData[0].ToDict()):
            print(data[0].ToDict())
            print(expectedData[0].ToDict())
            return False

        return True

    @staticmethod
    def TEST_GetMapsFromCollection() -> bool:
        """
        to test the gathering of map data from a steam collection
        """
        collections = SteamWebAPI.GetCollectionsDetails(1, [3513758895], True)

        data = SteamWebAPI.GetMapsFromCollectionsList(collections)

        print ("Total Remote Maps: ", len(data))

        # # print (data)
        # for _map in data:
        #     print (_map.ToDict())
        # return False
    
        expectedData = [{'publishedfileid': '3229373526', 'creator': '76561198103562816', 'title': 'Rond Point Express', 'description': 'School project for ISART DIGITAL Paris Available/Compatible Game modes: - Casual & Competitive (defend the market) - Wingman (Defend the market) - Deathmatch (F4A and team deathmatch)\r\n\r\n\r\nUses Custom and ingame assets\r\n\r\nBeta workshop page:\r\nhttps://steamcommunity.com/sharedfiles/filedetails/?id=3178325186\r\n\r\nArtstation Post:\r\nhttps://www.artstation.com/artwork/LRKW2k', 'tags': [{'tag': 'Classic'}, {'tag': 'Deathmatch'}, {'tag': 'Map'}, {'tag': 'Wingman'}, {'tag': 'Cs2'}]},
                        {'publishedfileid': '3073797349', 'creator': '76561198277826415', 'title': '1v1 Arena', 'description': 'Very nice', 'tags': [{'tag': 'Classic'}, {'tag': 'Deathmatch'}, {'tag': 'Custom'}, {'tag': 'Map'}, {'tag': 'Wingman'}, {'tag': 'Cs2'}]},
                        {'publishedfileid': '3130080493', 'creator': '76561199556158004', 'title': 'Aim Map 2v2', 'description': 'Gray Aim Map, Aim 2v2, very simple map that\'s meant to be smooth running so that anyone can run it and play cs2 with friends for fun. --COMMANDS TO KNOW-- Please type "bot_kick" into console to kick the bots. Please use "mp_freezetime 10" if you\'d like to make rounds load faster.', 'tags': [{'tag': 'Classic'}, {'tag': 'Custom'}, {'tag': 'Map'}, {'tag': 'Cs2'}]},
                        {'publishedfileid': '3088183343', 'creator': '76561197968653650', 'title': 'Bounce', 'description': 'Small symmetrical bounce house to warm up and have fun. \nRecommended for 2 - 8 players.\n\n\nDefault server commands:\nmp_freezetime 5\nmp_maxmoney 100000\nmp_startmoney 100000\nsv_falldamage_scale 0.1', 'tags': [{'tag': 'Classic'}, {'tag': 'Deathmatch'}, {'tag': 'Custom'}, {'tag': 'Map'}, {'tag': 'Wingman'}, {'tag': 'Cs2'}]}]

        print ("Expected: ", len(expectedData))

        if(data[0].ToDict() != expectedData[0]):
            print(data[0].ToDict())
            print(expectedData[0].ToDict())
            return False

        return True


if __name__ == "__main__":
    print ("CS2 Server Maker - Unit Tests")
    print ("version 1.0.0\n")

    if len(argv) < 2:
        print ("Not enough arguments")
        print ("py .\\unitTests.py <testName>\n")
        print ("valid tests:")
        print (" - WebConnection")
        print (" - GetCollectionDetails")
        print (" - GetNonPublicCollectionDetails")
        print (" - CollectionNotFound")
        exit(1)

    #
    # CS2 SERVER TESTS
    #

    # TODO

    #
    # STEAM API TESTS
    #

    if(not UnitTests.TEST_WebConnection()):
        print(bcolors.FAIL, end="")
        print("Internet Connection Failed")
        print(bcolors.ENDC, end="")
        exit(-1)
    
    # Connectivity is allways tested so if python ends up here we can assume that it has passed
    if argv[1] == "WebConnection":

        print ("\033[92m")

        print ("TEST_WebConnection() :: True")

        print ("Test Pass","\033[0m")
        exit(0)

    if argv[1] == "GetCollectionDetails":
        testVal = UnitTests.TEST_GetCollectionDetails()

        print ("\033[92m") if testVal else print ("\033[91m")

        print ("TEST_GetCollectionDetails() ::", testVal)

        print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
        if testVal :
            exit(0)
        else:
            exit(1)

    if argv[1] == "GetNonPublicCollectionDetails":
        testVal = UnitTests.TEST_GetNonPublicCollectionDetails()

        print ("\033[92m") if testVal else print ("\033[91m")

        print ("TEST_GetNonPublicCollectionDetails() ::", testVal)

        print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
        if testVal :
            exit(0)
        else:
            exit(2)

    if argv[1] == "CollectionNotFound":
        testVal = UnitTests.TEST_CollectionNotFound()

        print ("\033[92m") if testVal else print ("\033[91m")

        print ("TEST_CollectionNotFound() ::", testVal)

        print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
        if testVal :
            exit(0)
        else:
            exit(3)

    if argv[1] == "GetPublishedFileDetails":
        """
        Test if GetPublishedFileDetails implmentation is done
        """
        testVal = UnitTests.TEST_GetPublishedFileDetails()

        print ("\033[92m") if testVal else print ("\033[91m")

        print ("TEST_GetPublishedFileDetails() ::", testVal)

        print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
        if testVal :
            exit(0)
        else:
            exit(4)

    if argv[1] == "GetMapsFromCollection":
        testVal = UnitTests.TEST_GetMapsFromCollection()

        print ("\033[92m") if testVal else print ("\033[91m")

        print ("TEST_GetPublishedFileDetails() ::", testVal)

        print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
        if testVal :
            exit(0)
        else:
            exit(5)

    print ("\033[91mTest not found.\033[0m")
    exit(2)