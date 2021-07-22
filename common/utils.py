def checkSettings(settingsDict, key):
    try:
        return settingsDict[key]
    except KeyError:
        return f"The key({key}) requested isn't there in the dictionary"
