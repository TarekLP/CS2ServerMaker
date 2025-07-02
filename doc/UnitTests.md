# Unit Tests

## Introduction

unitTests.py is a cli tool to test the features of the library.
you can use it as followed:

`py .\unitTests.py <testName>`

## Implemented Tests


**WebConnection:**

    test connectivity to steam web api services

**GetCollectionDetails:**

    used to check if the remote data matches expected data

**GetNonPublicCollectionDetails:**

    used to check if GetCollectionsDetails() catches non public collection. This error is raised
    only if one collection is asked. if multiple collections are asked, the invalid collection is
    ignored

**CollectionNotFound:**

    used to check if GetCollectionsDetails() catches non existant collection.

**GetPublishedFileDetails:**

    Test if GetPublishedFileDetails implmentation is done

**GetMapsFromCollection:**

    Test to see if GetMapsFromCollectionsList() works as intended
    Might fail if valve updates how they return data from unlisted workshop files

*"[ISteamRemoteStorage/GetPublishedFileDetails returns nothing for unlisted files](https://developer.valvesoftware.com/wiki/Steam_Web_API/Feedback#ISteamRemoteStorage/GetPublishedFileDetails_returns_nothing_for_unlisted_files)"*


## Adding new tests

to add a new test, add a new static method in the UnitTests class and update all the textes that serves
as documentation for your function

unit test example:

```py
# in the UnitTests Class
class UnitTests:
    # Other unit tests...

    @staticMethod
    def TEST_YourUnitTest()->bool:
        """
        your test description
        """
        # Do Someting ...
        YourTest: bool = False
        
        return YourTest # Boolean
    
    # Other unit tests...

# in the __main__ part of the script

if __name__ == "__main__":
    # basic unit test stuff and other tests...

    if argv[1] == "YourUnitTest":
        testVal = UnitTests.TEST_YourUnitTest()

        print ("\033[92m") if testVal else print ("\033[91m")

        print ("TEST_YourUnitTest() ::", testVal)

        print ("Test Pass","\033[0m") if testVal else print ("Test Failed","\033[0m")
        exit(0)

    # other tests...
```

## List of test data

**Test Collection - CS2 Server Starter**
a public collection made for unit testing
https://steamcommunity.com/sharedfiles/filedetails/?id=3513758895

**Test Collection - CS2 Server Starter Non public collection**
a private collection made for unit testing
https://steamcommunity.com/sharedfiles/filedetails/?id=3514418698