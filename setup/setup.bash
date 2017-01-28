
################################################################################
# Figure out which platform we are on for platform dependent installs
platform='unknown'

case "$OSTYPE" in
  solaris*) platform="SOLARIS" ;;
  darwin*)  platform="OSX" ;; 
  linux*)   platform="LINUX" ;;
  bsd*)     platform="BSD" ;;
  msys*)    platform="WINDOWS" ;;
  *)        platform="unknown: $OSTYPE" ;;
esac

echo "$platform"

################################################################################
## DEPENDENCIES
################################################################################
# Install python for development and python opencv bindings
sudo apt-get install python-dev python-pip python-opencv libjpeg-dev

# Now install tornado python web server for our web interface
sudo pip install tornado 



################################################################################
## VISION
################################################################################

# Now install Pillow to do python drawing and image stuff
sudo pip install Pillow 

if [ "$platform" == "LINUX" ]
# Now install pic image drivers
    sudo pip install picamera
if


################################################################################
## MOTORS
################################################################################

if [ "$platform" == "LINUX" ]
# Install the Adafruit Servo drivers for python
# https://github.com/adafruit/Adafruit_Python_PCA9685
    sudo pip install adafruit-pca9685
fi

################################################################################
## SPEECH
################################################################################

if [ "$platform" == "LINUX" ]
# Festival Text to Speech for embedded systems. (Flite)
# https://learn.adafruit.com/speech-synthesis-on-the-raspberry-pi
    sudo apt-get install flite

    sudo apt-get install festival
if

if [ "$platform" == "OSX" ]
# Cross-browser python version for use on macs
    sudo pip install pyttsx
    brew install espeak
fi

################################################################################
## HEARING
################################################################################


if [ "$platform" == "OSX" ]
# Cross-browser python version for use on macs
    brew install portaudio
    pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio
    
    # PocketSphinx needs a custom install for latest
    brew tap watsonbox/cmu-sphinx
    brew install --HEAD watsonbox/cmu-sphinx/cmu-sphinxbase
    brew install --HEAD watsonbox/cmu-sphinx/cmu-pocketsphinx
    pip install --ignore-installed six
    sudo pip install --upgrade google-api-python-client

    # Test it on the terminal with a live mic feed: "pocketsphinx_continuous -inmic yes"
else
	sudo pip install pyaudio
fi

sudo pip install SpeechRecognition

