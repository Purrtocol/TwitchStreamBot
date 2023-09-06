from twitchio.ext import commands
from chat import *
from google.cloud import texttospeech_v1beta1 as texttospeech
import vlc
import os 
import time
import nltk
import creds
import asyncio
import read_my_mic as rmm
import _thread
import threading
from sound_player import play_sound
from multiprocessing import Process, Lock
from parse_text import parse


CONVERSATION_LIMIT = 20

class Bot(commands.Bot):

    def __init__(self, lock, conversation):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        Bot.conversation = conversation
        super().__init__(token= creds.TWITCH_TOKEN, prefix='!', initial_channels=[creds.TWITCH_CHANNEL])
        Bot.lock = lock

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # download the words corpus
        nltk.download('words')

        # Check if the message contains english words
        if not any(word in message.content for word in nltk.corpus.words.words()):
            return
        
        # Check if the message is too long or short
        if len(message.content) > 70 or len(message.content) < 3:
            return
        
        print('------------------------------------------------------')
        print(message.content)
        print(message.author.name)
        print(Bot.conversation)

        content = message.content.encode(encoding='ASCII',errors='ignore').decode()
        Bot.conversation.append({ 'role': 'user', 'content': content })
        print(content)

        response = parse(gpt3_completion(Bot.conversation))
        print('Tana-chan:' , response)

        if(Bot.conversation.count({ 'role': 'assistant', 'content': response }) == 0):
            Bot.conversation.append({ 'role': 'assistant', 'content': response })
        
        if len(Bot.conversation) > CONVERSATION_LIMIT:
            Bot.conversation = Bot.conversation[1:]
        
        client = texttospeech.TextToSpeechClient()

        #response = message.content + "? " + response #remove to remove initial message from speech output
        ssml_text = '<speak>'
        response_counter = 0
        mark_array = []
        for s in response.split(' '):
            ssml_text += f'<mark name="{response_counter}"/>{s}'
            mark_array.append(s)
            response_counter += 1
        ssml_text += '</speak>'

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
        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)


        #play_sound("output.mp3", Bot.lock)

        count = 0
        current = 0
        for i in range(len(response.timepoints)):
            count += 1
            current += 1
            with open("output.txt", "a", encoding="utf-8") as out:
                out.write(mark_array[int(response.timepoints[i].mark_name)] + " ")
            if i != len(response.timepoints) - 1:
                total_time = response.timepoints[i + 1].time_seconds
                #time.sleep(total_time - response.timepoints[i].time_seconds)
            if current == 25:
                    open('output.txt', 'w', encoding="utf-8").close()
                    current = 0
                    count = 0
            elif count % 7 == 0:
                with open("output.txt", "a", encoding="utf-8") as out:
                    out.write("\n")
        #time.sleep(2)
        open('output.txt', 'w').close()



        # Print the contents of our message to console...
        
        print('------------------------------------------------------')

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)
        
        #rmmClass = rmm.ReadMyMic()
        #await asyncio.gather(self.handle_commands(message), rmmClass.get_speech())

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with. 

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        await ctx.send(f'Hello {ctx.author.name}!')
        
class botThread(threading.Thread):
    def __init__(self, lock, conversation):
        threading.Thread.__init__(self)
        self.lock = lock
        self.conversation = conversation
    
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = Bot(self.lock, self.conversation)
        loop.run_until_complete(bot.run())
        #bot.run()



os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds.GOOGLE_JSON_PATH
conversation = list()
conversation.append({ 'role': 'system', 'content': open_file('prompt_chat.txt') })
#bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.

#mic_input = rmm.ReadMyMic(lock)
#mic_input.run()

def run_bot(lock, conversation):
    bot = Bot(lock, conversation)
    loop.run_until_complete(bot.run())
    
def run_mic(lock, conversation):
    mic = rmm.ReadMyMic(lock, conversation)
    mic.run()

if __name__ == '__main__':
    lock = threading.Lock()
    thread1 = botThread(lock, conversation)
    thread2 = rmm.micThread(lock, conversation)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

#if __name__ == '__main__':
#    lock = Lock()
#    proc1 = Process(target=run_bot, args=(lock, conversation))
#    proc2 = Process(target = run_mic, args = (lock, conversation))
#    proc1.start()
#    proc2.start()
#    proc1.join()
#    proc2.join()