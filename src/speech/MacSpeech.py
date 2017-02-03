from AppKit import NSSpeechSynthesizer
import time
import sys


class MacSpeech:
    voice = "com.apple.speech.synthesis.voice.serena.premium"
    synthesizer = None

    def __init__(self):
        # Create the Mac version of speech synthesis
        self.synthesizer = NSSpeechSynthesizer.alloc().init()


        if not (self.voice in NSSpeechSynthesizer.availableVoices() ):
            raise Exception("Specified voice not found: " + voice)

        self.synthesizer.setVoice_(self.voice)



    def sayAndWait( self, phrase ):
        '''
        Speak the phrase and wait until it is done, blocking the thread
        '''
        self.synthesizer.startSpeakingString_(phrase)
        time.sleep(0.5)
        while self.synthesizer.isSpeaking():
            time.sleep(0.1)
