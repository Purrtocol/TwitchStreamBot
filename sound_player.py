from playsound import playsound
import mutagen
from mutagen.mp3 import MP3
import time
import os 
import threading

# Play an audio file, then delete it
def play_sound(filename, lock):
    print('acquiring lock')
    lock.acquire()
    print('lock acquired')
    
    audio_file = os.path.dirname(__file__) + '\\' + filename
    print('playing sound')
    playsound(audio_file)
    print('done playing sound')
    
    #media = vlc.MediaPlayer(audio_file)
    #print("aaaa") # TODO remove me
    #media.play()
    #print('------------------------------------------------------')
    # hold the lock until the player is finished
    time.sleep(1.5)
    #audio = MP3(audio_file)
    #duration = audio.info.length / 1000
    #time.sleep(duration)
    os.remove(audio_file)
    
    lock.release()
    
