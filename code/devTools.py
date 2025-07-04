from sys import argv

from mapDataWrapper import MapDataWrapper
from steamWebAPI import SteamWebAPI

if __name__ == "__main__":

    if(len(argv) < 2):
        print("no args, nothing to do\n")
        print("tools:")
        print(" - testSteamConn")
        print(" - mutableData")
        exit(1)

    """
    just to get the actual web socket error type
    (gaierror)
    """
    if(argv[1] == 'testSteamConn'):
        SteamWebAPI.SendRequest("/", {}, "GET")
        exit(0)

    """
    depicts how mutable data can be used as C pointers to modify data in memory
    """
    if(argv[1] == 'mutableData'):
        dictTest: dict = {}
        MapDataWrapper.SaveConfig(dictTest)
        print(dictTest)
        MapDataWrapper.SaveConfigPtr(dictTest)
        print(dictTest)
        exit(0)