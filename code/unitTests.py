
from sys import argv
from cmdColors import bcolors
from mapDataWrapper import MapDataWrapper
from exceptions import CollectionIsNotPublicException, CollectionNotFoundException
from dataStructs import CSMap, SteamCollection, SteamFileElement
from steamWebAPI import SteamWebAPI

#
#   UNIT TESTS
#

class UnitTests:

    def EXEC_Tests(args, ExitOnSuccess = True):
        if len(args) < 2:
            print ("Not enough arguments")
            print ("py .\\unitTests.py <testName>\n")
            print ("valid tests:")
            print (" ")
            print ("-- Data Tests --")
            print (" - ConfigDeserializeSteamCollectionsData")
            print (" - ConfigSerializeSteamCollectionsData")
            print (" - ConfigDeserializeManuallyAddedMaps")
            print (" - ConfigSerializeManuallyAddedMaps")
            print (" - ConfigSaveMapDataWrapper")
            print (" - ConfigRegisterNewCollection")
            print (" ")
            print ("-- Steam Tests --")
            print (" - WebConnection")
            print (" - GetCollectionDetails")
            print (" - GetNonPublicCollectionDetails")
            print (" - CollectionNotFound")
            print (" - GetPublishedFileDetails")
            print (" - GetMapsFromCollection")
            print (" ")
            print (" - All")
            print (" - DataFeatures")
            print (" - SteamFeatures")
            exit(1000)

        TestNum = 0

        #
        # DATA TESTS
        #

        if args[1] == "ConfigDeserializeSteamCollectionsData":
            testVal = UnitTests.TEST_ConfigDeserializeSteamCollectionsData()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_ConfigDeserializeSteamCollectionsData() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")

            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True

        if args[1] == "ConfigSerializeSteamCollectionsData":
            testVal = UnitTests.TEST_ConfigSerializeSteamCollectionsData()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_ConfigSerializeSteamCollectionsData() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
            
            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True

        if args[1] == "ConfigDeserializeManuallyAddedMaps":
            testVal = UnitTests.TEST_ConfigDeserializeManuallyAddedMaps()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_ConfigDeserializeManuallyAddedMaps() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
            
            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True
        
        if args[1] == "ConfigSerializeManuallyAddedMaps":
            testVal = UnitTests.TEST_ConfigSerializeManuallyAddedMaps()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_ConfigSerializeManuallyAddedMaps() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
            
            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True

        if args[1] == "ConfigSaveMapDataWrapper":


            testVal = UnitTests.TEST_ConfigSaveMapDataWrapper()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_ConfigSaveMapDataWrapper() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
            
            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True

        if args[1] == "ConfigRegisterNewCollection":
            testVal = UnitTests.TEST_ConfigRegisterNewCollection()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_ConfigRegisterNewCollection() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
            
            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True
        #
        # STEAM API TESTS
        #

        if(not UnitTests.TEST_WebConnection()):
            print(bcolors.FAIL, end="")
            print("Internet Connection Failed")
            print(bcolors.ENDC, end="")
            exit(-1)
        
        # Connectivity is allways tested so if python ends up here we can assume that it has passed
        if args[1] == "WebConnection":

            print ("\033[92m")

            print ("TEST_WebConnection() :: True")

            print ("Test Pass","\033[0m")
            
            TestNum+=1
            if ExitOnSuccess : exit(0)
            return True

        if args[1] == "GetCollectionDetails":
            testVal = UnitTests.TEST_GetCollectionDetails()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_GetCollectionDetails() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
            
            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True

        if args[1] == "GetNonPublicCollectionDetails":
            testVal = UnitTests.TEST_GetNonPublicCollectionDetails()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_GetNonPublicCollectionDetails() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
            
            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True
        
        if args[1] == "CollectionNotFound":
            testVal = UnitTests.TEST_CollectionNotFound()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_CollectionNotFound() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
            
            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True

        if args[1] == "GetPublishedFileDetails":
            """
            Test if GetPublishedFileDetails implmentation is done
            """
            testVal = UnitTests.TEST_GetPublishedFileDetails()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_GetPublishedFileDetails() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
            
            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True

        if args[1] == "GetMapsFromCollection":
            testVal = UnitTests.TEST_GetMapsFromCollection()

            print ("\033[92m") if testVal else print ("\033[91m")

            print ("TEST_GetPublishedFileDetails() ::", testVal)

            print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
            
            TestNum+=1
            if not testVal :
                exit(TestNum)
            if ExitOnSuccess : exit(0)
            return True

        if args[1] == "All":
            test = 0
            test += int(UnitTests.EXEC_Tests(["","ConfigDeserializeSteamCollectionsData"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","ConfigSerializeSteamCollectionsData"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","ConfigDeserializeManuallyAddedMaps"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","ConfigSerializeManuallyAddedMaps"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","ConfigSaveMapDataWrapper"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","ConfigRegisterNewCollection"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","WebConnection"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","GetCollectionDetails"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","GetNonPublicCollectionDetails"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","CollectionNotFound"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","GetPublishedFileDetails"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","GetMapsFromCollection"], ExitOnSuccess = False))

            print("tested "+str(test)+" tests")
            if ExitOnSuccess : exit(1)
            return True
        
        if args[1] == "DataFeatures":
            test = 0
            test += int(UnitTests.EXEC_Tests(["","ConfigDeserializeSteamCollectionsData"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","ConfigSerializeSteamCollectionsData"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","ConfigDeserializeManuallyAddedMaps"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","ConfigSerializeManuallyAddedMaps"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","ConfigSaveMapDataWrapper"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","ConfigRegisterNewCollection"], ExitOnSuccess = False))

            print("tested "+str(test)+" tests")
            if ExitOnSuccess : exit(1)
            return True
        
        if args[1] == "SteamFeatures":
            test = 0
            test += int(UnitTests.EXEC_Tests(["","WebConnection"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","GetCollectionDetails"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","GetNonPublicCollectionDetails"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","CollectionNotFound"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","GetPublishedFileDetails"], ExitOnSuccess = False))
            test += int(UnitTests.EXEC_Tests(["","GetMapsFromCollection"], ExitOnSuccess = False))

            print("tested "+str(test)+" tests")
            if ExitOnSuccess : exit(1)
            return True

        print ("\033[91mTest not found.\033[0m")
        exit(2)

    @staticmethod
    def TEST_ConfigDeserializeSteamCollectionsData(Clear = True) -> bool:
        
        if Clear : MapDataWrapper.Clear()

        _data = {"mapDataWrapper_collections": [
            {
                "id": 3513758895,
                "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=3513758895",
                "name": "Test Collection - CS2 Server Starter",
                "mapIds": []
            }
        ]}

        _expectedData = SteamCollection(
            _data["mapDataWrapper_collections"][0]["id"],
            _data["mapDataWrapper_collections"][0]["url"],
            _data["mapDataWrapper_collections"][0]["name"],
            _data["mapDataWrapper_collections"][0]["mapIds"])

        MapDataWrapper.collections = MapDataWrapper.DeserializeCollections(_data["mapDataWrapper_collections"])

        if(MapDataWrapper.collections[0].ToDict() != _expectedData.ToDict()):
            print(MapDataWrapper.collections[0].ToDict())
            print(_expectedData.ToDict())
            return False
        
        return True
    
    @staticmethod
    def TEST_ConfigSerializeSteamCollectionsData(Clear = True) -> bool:
        
        if Clear : MapDataWrapper.Clear()
        
        _expectedData = [
            {
                "id": 3513758895,
                "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=3513758895",
                "name": "Test Collection - CS2 Server Starter",
                "mapIds": []
            }
        ]

        initialData = [SteamCollection(
            _expectedData[0]["id"],
            _expectedData[0]["url"],
            _expectedData[0]["name"],
            _expectedData[0]["mapIds"])]

        MapDataWrapper.collections = initialData

        _data = MapDataWrapper.SerializeCollections()

        if(_data != _expectedData):
            print(_data)
            print(_expectedData)
            return False
        
        return True

    @staticmethod
    def TEST_ConfigDeserializeManuallyAddedMaps(Clear = True) -> bool:
        
        if Clear : MapDataWrapper.Clear()

        exceptedData = CSMap(100, 0, "Foo Map Test", tags=["CS2", "Demolition"])

        csmapToDict = [exceptedData.ToDict()]

        MapDataWrapper.manuallyAddedMaps = MapDataWrapper.DeserializeManuallyAddedMaps(csmapToDict)

        
        if(MapDataWrapper.manuallyAddedMaps[0].ToDict() != exceptedData.ToDict()):
            print(MapDataWrapper.manuallyAddedMaps[0].ToDict())
            print(exceptedData.ToDict())
            return False

        return True
    
    @staticmethod
    def TEST_ConfigSerializeManuallyAddedMaps(Clear = True) -> bool:
        
        if Clear : MapDataWrapper.Clear()

        csmap = CSMap(100, 0, "Foo Map Test", tags=["CS2", "Demolition"])

        expectedData = [csmap.ToDict()]

        MapDataWrapper.manuallyAddedMaps = [csmap]

        data = MapDataWrapper.SerializeManuallyAddedMaps()
        
        if(data != expectedData):
            print(data)
            print(expectedData)
            return False

        return True

    @staticmethod
    def TEST_ConfigSaveMapDataWrapper(Clear = True) -> bool:
        
        if Clear : MapDataWrapper.Clear()

        UnitTests.TEST_ConfigDeserializeManuallyAddedMaps(False)
        UnitTests.TEST_ConfigDeserializeSteamCollectionsData(False)
        
        gatheredData = {}
        expectedData = {'mapDataWrapper_isFeatureActivated': True, 'mapDataWrapper_collections': [{'id': 3513758895, 'url': 'https://steamcommunity.com/sharedfiles/filedetails/?id=3513758895', 'name': 'Test Collection - CS2 Server Starter', 'mapIds': []}], 'mapDataWrapper_manuallyAddedMaps': [{'publishedfileid': 100, 'creator': 0, 'title': 'Foo Map Test', 'tags': ['CS2', 'Demolition']}]}

        MapDataWrapper.SaveConfigPtr(gatheredData)

        if(gatheredData != expectedData):
            print(gatheredData)
            print(expectedData)
            return False

        return True
    
    @staticmethod
    def TEST_ConfigRegisterNewCollection() -> bool:

        MapDataWrapper.Clear()

        colId: int = 3513758895 # Test collection made for the project

        ptr_error: list = []    # this variable is a list, lists are mutable
                                # and can be modified in the method,
                                # functionning like a C pointer/ref

        MapDataWrapper.RegisterNewCollection(colId, ptr_error)

        return MapDataWrapper.collections[0].id == colId

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

        print ("\nTotal Remote Maps: ", len(data))

        # # print (data)
        # for _map in data:
        #     print (_map.ToDict())
        # return False
    
        expectedData = [{'publishedfileid': '3229373526', 'creator': '76561198103562816', 'title': 'Rond Point Express', 'tags': [{'tag': 'Classic'}, {'tag': 'Deathmatch'}, {'tag': 'Map'}, {'tag': 'Wingman'}, {'tag': 'Cs2'}]},
                        {'publishedfileid': '3073797349', 'creator': '76561198277826415', 'title': '1v1 Arena', 'tags': [{'tag': 'Classic'}, {'tag': 'Deathmatch'}, {'tag': 'Custom'}, {'tag': 'Map'}, {'tag': 'Wingman'}, {'tag': 'Cs2'}]},
                        {'publishedfileid': '3130080493', 'creator': '76561199556158004', 'title': 'Aim Map 2v2', 'tags': [{'tag': 'Classic'}, {'tag': 'Custom'}, {'tag': 'Map'}, {'tag': 'Cs2'}]},
                        {'publishedfileid': '3088183343', 'creator': '76561197968653650', 'title': 'Bounce', 'tags': [{'tag': 'Classic'}, {'tag': 'Deathmatch'}, {'tag': 'Custom'}, {'tag': 'Map'}, {'tag': 'Wingman'}, {'tag': 'Cs2'}]}]

        print ("Expected: ", len(expectedData))

        if(data[0].ToDict() != expectedData[0]):
            print(data[0].ToDict())
            print(expectedData[0])
            return False

        return True


if __name__ == "__main__":
    print ("CS2 Server Maker - Unit Tests")
    print ("version 1.0.0\n")

    UnitTests.EXEC_Tests(argv)