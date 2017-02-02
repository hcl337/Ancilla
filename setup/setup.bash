
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

    sudo apt-get update
    sudo apt-get upgrade
    sudo rpi-update    
    sudo apt-get install build-essential git cmake pkg-config
    sudo apt-get install libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev
    sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
    sudo apt-get install libgtk2.0-dev
    sudo apt-get install libatlas-base-dev gfortran

    cd ~
    git clone https://github.com/Itseez/opencv_contrib.git
    cd opencv_contrib
    git checkout 3.1.0
    sudo rm -rf ~/.cache/pip/
    pip install numpy
else
    # OpenCV
    brew tap homebrew/science
    brew install opencv
    sudo pip install numpy
    # Set up paths in python
    cat ~/.bash_profile | grep PYTHONPATH
    ln -s /usr/local/Cellar/opencv/2.4.10/lib/python2.7/site-packages/cv.py cv.py
    ln -s /usr/local/Cellar/opencv/2.4.10/lib/python2.7/site-packages/cv2.so cv2.so
if


################################################################################
## MOTORS
################################################################################

if [ "$platform" == "LINUX" ]
# Install the Adafruit Servo drivers for python
# https://github.com/adafruit/Adafruit_Python_PCA9685
    sudo pip install adafruit-pca9685
    sudo apt-get install python-smbus
    sudo apt-get install i2c-tools

# NOTE!!! Need to add 'i2c-bcm2708' to /etc/modules also. Replace with auto-command
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

