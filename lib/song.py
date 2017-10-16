from mutagen.id3 import ID3
from mutagen.mp3 import MP3

def getData(path, mediaSource):
    if mediaSource == 'file':
        audio = ID3(path)
        laudio = MP3(path)
        song = {}
        song["album"] = audio['TALB']
        song["art"] = audio['APIC']
        song["artist"] = audio['TPE1']
        song["length"] = laudio.info.length
        song["title"] = audio['TIT2']
    else:
        return False
    return song
