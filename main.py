import argparse
from pathlib import Path
import json
import pandas as pd

# Constants for field names in Spotify json files
SONG_NAME="master_metadata_track_name"
ARTIST_NAME="master_metadata_album_artist_name"
ALBUM_NAME="master_metadata_album_album_name"

# Mapping from json field names to better titles
betterFieldNames = {
    SONG_NAME: "Song Name",
    ARTIST_NAME: "Artist Name",
    ALBUM_NAME: "Album Name"
}

def getFilesList(directory):
    """
    Checks if the given directory exists
    
    :param directory: the directory to check
    """
    if not Path(directory).exists():
        raise ValueError("Directory does not exist")
    files = [Path(file) for file in Path(directory).glob("**/*.json")]
    if len(files) == 0:
        print("Warning: the directory you provided does not contain any files, "
              + "consider checking the path again, or remove the -d flag "
              + "if you are trying to provide a file")
    return files

def getFieldsToExtract(args):
    fields = []
    if args.song:
        fields.append(SONG_NAME)
    if args.artist:
        fields.append(ARTIST_NAME)
    if args.album:
        fields.append(ALBUM_NAME)
    return fields if len(fields) != 0 else [SONG_NAME, ARTIST_NAME, ALBUM_NAME]

def extractData(args):
    # Extract file list if needed
    try:
        files = getFilesList(args.file) if args.directory else [Path(args.file)]
    except ValueError:
        print("Error: directory does not exist")

    dataDict = {} # Dictionary for extracted data
    toExtract = getFieldsToExtract(args) # Setup fields to extract

    # Operate on each json file
    for file in files:
        # Load json data
        try:
            with open(file, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except:
            print(f"Error: the file {file} cannot be opened")
            continue

        # Process each entry
        for entry in data:
            key = tuple([entry[str(i)] for i in toExtract])
            if key not in dataDict:
                dataDict[key] = 1
            else:
                dataDict[key] += 1

    # Format data
    dataList = []
    for key in dataDict:
        songData = [i for i in key] + [dataDict[key]]
        dataList.append(songData)
    fullData = pd.DataFrame(dataList,
                            columns=[betterFieldNames[i] for i in toExtract]+["Times Played"])

    # Save extracted data
    fullData.to_csv(args.savefile + ".csv", index=False)

def main():
    # Set up arguments
    parser = argparse.ArgumentParser(
                    prog='python3 main.py',
                    description='''
                        This program helps extract data from Spotify user
                        data exports. You can specify which of the following
                        to export: song name, artist name, or album
                        name by specifying flags, or leave out all flags
                        to extract all three.
                    ''')
    parser.add_argument('-s','--song', 
                        action="store_true",
                        help="extract the song name from the user data")
    parser.add_argument('-al','--album', 
                        action="store_true",
                        help="extract the album name from the user data")
    parser.add_argument('-ar','--artist', 
                        action="store_true",
                        help="extract the artist name from the user data")
    parser.add_argument('-d','--directory',
                        action="store_true",
                        help="""
                        treat file string as directory and recursively search
                        for files in subdirectories to parse data from
                        """)
    parser.add_argument('file', help="file containg the information to extract")
    parser.add_argument('-o', '--savefile',
                        default="extractedData",
                        help="file to save the extracted data to. All data is exported as a csv")
    
    # Call main script
    extractData(parser.parse_args())

if __name__ == "__main__":
    main()
