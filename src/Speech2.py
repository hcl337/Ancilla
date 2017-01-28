from AppKit import NSSpeechSynthesizer
import time
import sys



text = "Hi there"


print("Will say: " + text)

nssp = NSSpeechSynthesizer

ve = nssp.alloc().init()

voices = ["com.apple.speech.synthesis.voice.Alex",
"com.apple.speech.synthesis.voice.Vicki",
"com.apple.speech.synthesis.voice.Ava",
"com.apple.speech.synthesis.voice.BAD",
"com.apple.speech.synthesis.voice.Victoria",
"com.apple.speech.synthesis.voice.Zarvox" ]

voice = "com.apple.speech.synthesis.voice.serena.premium"
ve.setVoice_(voice)

print(str(nssp.availableVoices()))

def sayAndWait( phrase ):
    print "going to say: " + phrase
    ve.startSpeakingString_(phrase)    
    time.sleep(0.5)
    while ve.isSpeaking():
        time.sleep(0.1)
        print "    Still speaking"

sayAndWait("Hello, my name is AQ-3")
sayAndWait("Nice to meet you!")
sayAndWait("What is your name?")


'''
# for voice in nssp.availableVoices():
for voice in voices:
   ve.setVoice_(voice)
   print voice
   ve.startSpeakingString_(text)
   while ve.isSpeaking():
      time.sleep(1)

'''