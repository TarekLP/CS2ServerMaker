# Map Data Wrapper

tags (`python, class,
static methods,
static variables,
data handling`)

## Introduction

this class is used to store and gather data using the SteamApi implementation made for this project.

It uses static variables that can be accessed by everywhere and handle the gathering and caching of information.

## How to use

**initializeing the class**

to initialize the class, call `LoadFromConfig`

```py
@staticmethod
def LoadFromConfig(config_data: dict):
    """
    loads config data into the static variables from dict (json)
    """
```

usage:

```py
"""
initializeing the class
"""

from mapDataWrapper import MapDataWrapper

configFile: dict = json.load("filePath.json") # the json config file

MapDataWrapper.LoadFromConfig(configFile)

```


**adding new steam collection**

to add a new steam collection, call the `RegisterNewCollection`

this method does not add dupplicates and can handle invalid collections (hidden or non existing)

```py
@staticmethod
def RegisterNewCollection(collectionId: int = 0, forceRegister: bool = False, ptr_error: list = [])->bool:
    """
    register into collections static variable a steam collection from id

    forceRegister indicates if the collection should be added even though it's already present in the collection list

    ptr_error is an mutable variable to get error logs

    @throws gaierror: web socket error, raised when no connection, must be handled

    @returns Registration State: True = Success, False = Error
    """
```

usage:

```py
"""
Adding a new collection
"""

from mapDataWrapper import MapDataWrapper

colId: int = 3513758895 # Test collection made for the project

ptr_error: list = [] # this variable is a list, lists are mutable
                     # and can be modified in the method,
                     # functionning like a C pointer/ref

MapDataWrapper.RegisterNewCollection(colId, ptr_error)

```

**Caching the maps from added collections**

caching the maps should be done after loading a json config file for the server and when modifying
the steam collection list. It has to be implemented by hand when those events are handled.

to cache the maps, use MapDataWrapper.CacheMapsFromCollections()
