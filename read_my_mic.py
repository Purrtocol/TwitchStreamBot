import speech_recognition as sr
from twitchio.ext import commands
from chat import *
from google.cloud import texttospeech_v1beta1 as texttospeech
import vlc
import os 
import time
import nltk
import creds
import asyncio
import threading
from sound_player import play_sound

#audio_file = os.path.dirname(__file__) + '/output.mp3'
#media = vlc.MediaPlayer(audio_file)
#media.play()

class ReadMyMic():
    #r = sr.Recognizer()
    #mic = sr.Microphone(device_index=2)
    #mic = sr.Microphone()
    #conversation = list()
    #conversation.append({ 'role': 'system', 'content': open_file('prompt_chat.txt') })
    #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds.GOOGLE_JSON_PATH

    def __init__(self, lock, conversation):
        # Initialise with a lock to prevent multiple simultaneous output
        ReadMyMic.lock = lock
        ReadMyMic.conversation = conversation
        self.mic = sr.Microphone()
        self.r = sr.Recognizer()
        with self.mic as source:
            self.r.adjust_for_ambient_noise(source, duration=5)
            print("adjusted")
        
    def run(self):
        audio_file = os.path.dirname(__file__) + '\\' + "output2.mp3"
        while 1:
            if not os.path.exists(audio_file):
                self.get_speech()
    
    def get_speech(self):
        with self.mic as source:
            audio = self.r.listen(source)
            try:
                words = self.r.recognize_google(audio)
            except:
                print("bad input")
                return
            print('------------------------------------------------------')
            print(words)
            
        ReadMyMic.conversation.append({ 'role': 'user', 'content': words })
        
        # TODO: Move this into its own class
        response = gpt3_completion(ReadMyMic.conversation).replace('~', '')
        print('Tana-chan:' , response)
        
        # TODO: Move this into its own class
        ssml_text = '<speak>'
        response_counter = 0
        mark_array = []
        for s in response.split(' '):
            ssml_text += f'<mark name="{response_counter}"/>{s}'
            mark_array.append(s)
            response_counter += 1
        ssml_text += '</speak>'

        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(ssml = ssml_text)

        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-GB",
            name= "en-GB-Wavenet-C",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )

        audio_config = texttospeech.AudioConfig(    
            audio_encoding=texttospeech.AudioEncoding.MP3,
        )
        

        response = client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config, "enable_time_pointing": ["SSML_MARK"]}
        )

        # The response's audio_content is binary.
        with open("output2.mp3", "wb") as out:
            out.write(response.audio_content)

        #play_sound("output2.mp3", ReadMyMic.lock)
        
class micThread(threading.Thread):
    def __init__(self, lock, conversation):
        threading.Thread.__init__(self)
        self.lock = lock
        self.conversation = conversation
    
    def run(self):
        mic = ReadMyMic(self.lock, self.conversation)
        mic.run()
