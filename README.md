# TwitchStreamBot
Twitch stream bot


This is my multithreaded implementation of adi-panda's [Twitch Chat AI Bot](https://github.com/adi-panda/Kuebiko).

I tried to make some improvements to the classes to make it easier to change parts in and out, i.e. audio player. Note: I'm not a python dev, so best practices are beyond me.

This bot (in theory) maintains a three-way conversation between the streamer's microphone input, the viewer's chat, and the chat GPT. Threading is used to prevent overlapping sounds from playing.

To run it:
In one prompt, run:
```
python play_sounds.py
```

This will play and delete audio files as they are created.

In a second prompt, run:
```
python main.py
```

Note: The first prompt is needed due to a weird bug I haven't been able to resolve where it never plays the sound. If any python experts can resolve it, uncommenting the play_sound lines will revert to the original implementation.