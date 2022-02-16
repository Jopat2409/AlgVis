import os
import glob
import hashlib
import pickle
import osrparse
import pandas as pd

cache_dir = "\\.temp\\BeatmapHash.dat"


def ListBeatmaps(*beatmap_dirs: str) -> list:
    """Gets an array of .osu paths given a collection of directories
    :param beatmap_dirs:
        a collection of directories all of which contain beatmaps
    :return:
        an array containing paths to .osu files
    """
    # value to return
    r_value = []
    # loop through all specified directories
    for _dir in beatmap_dirs:
        # loop through all beatmap folders within the directory
        for b_dir in os.listdir(_dir):
            # create the base path
            t_path = os.path.join(_dir, b_dir)
            # loop through all the beatmap files in the base path
            for _beatmap in glob.glob(os.path.join(t_path, "*.osu")):
                # append to the return value
                r_value.append(_beatmap)
    return r_value


def CreateFileHash(beatmap: str) -> str:
    """ Creates a hash value given a file path
    :param beatmap:
        the file path in question
    :return:
        md5 hash of the file
    """
    # initialize the md5 hash
    hash_md5 = hashlib.md5()
    # open the file im read binary mode
    with open(beatmap, "rb") as f:
        # split the file into chunks of 4096 bits (md5 hash can only take in 4096 at once)
        for chunk in iter(lambda: f.read(4096), b""):
            # update the hash with the data
            hash_md5.update(chunk)
    # return the hexadecimal hash
    return hash_md5.hexdigest()


def CreateBeatmapCache(*beatmap_dirs) -> dict:
    """Creates a cache file to store beatmap hashes in
    :param beatmap_dirs: beatmap directories to search
    :return: a mapping of beatmap hashes to their respective file paths
    """
    # validate if the temp directory exists
    if not os.path.isdir("\\.temp"):
        # if it doesn't, create it
        os.mkdir("\\.temp")
    # Get the array of beatmaps
    b_array = ListBeatmaps(*beatmap_dirs)
    # create the hash map
    b_hashMap = {}
    # loop through all the specified beatmaps
    for _beatmap in b_array:
        # add the beatmap hash and beatmap path to the map
        b_hashMap.update({CreateFileHash(_beatmap): _beatmap})

    # save the hash map to a cache
    global cache_dir
    with open(cache_dir, "wb+") as c_file:
        pickle.dump(b_hashMap, c_file)
    # return the map
    return b_hashMap


def LoadBeatmapCache(*beatmap_dirs) -> dict:
    """Loads a beatmap hash map from the specified cache directory
    :param beatmap_dirs: any additional beatmap folders to search
    :return: mapping of file hash to file path
    """
    # load the beatmap cache from the cache file
    global cache_dir
    with open(cache_dir, "rb") as c_file:
        # load dict using pickle
        b_hashMap = pickle.load(c_file)

    return b_hashMap


def ListReplays(replay_dir: str) -> list:
    r_value = []
    for _replay in glob.glob(os.path.join(replay_dir, "*.osr")):
        r_value.append(_replay)
    return r_value


def MapReplays(replay_array: list, *beatmap_dirs: str) -> pd.DataFrame:
    """ Takes an array of replays, as well as any number of beatmap directories, and maps
    the replays to the beatmaps
    :param replay_array: Array of paths to replay files (.osr)
    :param beatmap_dirs: Directories to search for beatmaps (.osu)
    :return: mapping of replays to beatmaps
    """
    # value to be returned
    r_map = {}
    # cache directory
    global cache_dir
    # validation to check if cache exists
    if os.path.isfile(cache_dir):
        # load the beatmap cache
        m_hashMap = LoadBeatmapCache(*beatmap_dirs)
    else:
        # create the beatmap cache
        m_hashMap = CreateBeatmapCache(*beatmap_dirs)
    # iterate through replay paths
    for _replay in replay_array:
        # parse the replay using osrparse
        p_replay = osrparse.parse_replay_file(_replay)
        # validate to ensure that the hash value is in the dict
        if p_replay.beatmap_hash in m_hashMap:
            # update the return value with the parsed replay and the beatmap
            r_map.update({p_replay: m_hashMap[p_replay.beatmap_hash]})
        else:
            # inform the user that the correct beatmap could not be found
            print(f"Could not find the corresponding beatmap for {_replay}")
    t_map = {"Replays": r_map.keys(), "Beatmaps": r_map.values()}
    m_dataframe = pd.DataFrame(data=t_map)
    return m_dataframe


def CreateDataframe(b_map: pd.DataFrame, FPS=24):
    



if __name__ == "__main__":
    print(MapReplays(ListReplays("C:\\Users\\Joe\\AppData\\Local\\osu!\\Replays"),
                     "C:\\Users\\Joe\\AppData\\Local\\osu!\\Songs"))
