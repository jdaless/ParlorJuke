from mutagen.id3 import ID3
from mutagen.mp3 import MP3

def getData(dirName, file):
    song = {}
    metadata = ["album", "artist", "title"]
    mutadata = ["TALB", "TPE1", "TIT2"]
    if file is None:
        song["album"] = None
        song["art"] = None
        song["artist"] = None
        song["length"] = None
        song["title"] = None
    elif file[0] == 'file':
        try:
            audio = ID3(dirName + "/music/" + file[1])
            laudio = MP3(dirName + "/music/" + file[1])
        except Exception as e:
            print(e)
            return False

        for i in range (0, len(metadata)):
            try:
                song[metadata[i]] = audio[mutadata[i]].text[0]
            except Exception as e:
                song[metadata[i]] = None

        # song["art"] = audio["APIC"].data[0]
        song["length"] = laudio.info.length

        if song["title"] == None:
            song["title"] = file[1].split('/')[-1]
    else:
        return False
    return song
