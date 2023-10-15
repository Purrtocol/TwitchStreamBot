import speech_recognition as sr
from twitchio.ext import commands
from chat import *
from google.cloud import texttospeech_v1beta1 as texttospeech
import vlc
import os 
import time
import nltk
import creds
import random
import asyncio
import threading
from sound_player import play_sound
from parse_text import parse

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
        micList = sr.Microphone.list_microphone_names()
        micIndex = micList.index("Microphone (NVIDIA Broadcast)")
        #self.mic = sr.Microphone(micIndex)
        self.mic = sr.Microphone()
        self.r = sr.Recognizer()
        self.current_buffer = ""
        with self.mic as source:
            #self.r.adjust_for_ambient_noise(source=source, duration=5)
            print("adjusted")
        self.response_chance = 0.2
        
    def run(self):
        audio_file = os.path.dirname(__file__) + '\\' + "output2.mp3"
        while 1:
            if not os.path.exists(audio_file):
                self.get_speech()
    
    def get_speech(self):
        with self.mic as source:
            #self.r.adjust_for_ambient_noise(source=source, duration=1)
            print("adjusted2")
            audio = self.r.listen(source, timeout = 3)
            try:
                words = self.r.recognize_google(audio)
            except:
                print("bad input")
                return
            print('------------------------------------------------------')
            print(words)
            
        #self.current_buffer += words
        self.current_buffer = words
        if (len(self.current_buffer) > 10):
            if  "help" in self.current_buffer or random.random() < self.response_chance:
                
                if  "help" in self.current_buffer:
                    ReadMyMic.conversation.append({ 'role': 'user', 'content': self.current_buffer })
                    response = parse(gpt3_completion(ReadMyMic.conversation))
                else:
                    ReadMyMic.conversation.append({ 'role': 'user', 'content': self.current_buffer })
                    #ReadMyMic.conversation.append({ 'role': 'user', 'content': 'Wouldn\'t you agree that ' + self.current_buffer })
                    #ReadMyMic.conversation.append({ 'role': 'user', 'content': 'Finish this sentence: ' + self.current_buffer })
                    response = parse(gpt3_completion_prompt('ROGER: ' + self.current_buffer + '\nPurr-bot: Yes, I agree with you. Furthermore, '))
                    
                if (len(response) == 0):
                    return
                # TODO: Move this into its own class
                print('Purr-bot:' , response)
                if(ReadMyMic.conversation.count({ 'role': 'assistant', 'content': response }) == 0):
                    ReadMyMic.conversation.append({ 'role': 'assistant', 'content': response })
                
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
                    name= "en-GB-Wavenet-B",
                    ssml_gender=texttospeech.SsmlVoiceGender.MALE,
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
                print('------------------------------------------------------')
                self.current_buffer = ""
                self.response_chance = 0.2
            else:
                print("response change failed at " + str(self.response_chance))
                self.response_chance += 0.2
            
        #play_sound("output2.mp3", ReadMyMic.lock)
        
class micThread(threading.Thread):
    def __init__(self, lock, conversation):
        threading.Thread.__init__(self)
        self.lock = lock
        self.conversation = conversation
    
    def run(self):
        mic = ReadMyMic(self.lock, self.conversation)
        mic.run()
