from playsound import playsound
import mutagen
from mutagen.mp3 import MP3
import time
import os 
import threading

#audio_file = os.path.dirname(__file__) + '/output.mp3'
#media = vlc.MediaPlayer(audio_file)
#media.play()

def play_sound(audio_file):
    
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

while 1:
    chat_audio_file = os.path.dirname(__file__) + '\\' + "output.mp3"
    mic_audio_file = os.path.dirname(__file__) + '\\' + "output2.mp3"
    if os.path.exists(chat_audio_file):
        play_sound(chat_audio_file)
    if os.path.exists(mic_audio_file):
        play_sound(mic_audio_file)
