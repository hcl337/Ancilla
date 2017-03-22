
[Back to main readme](README.md).
Setting up the system fully takes a few hours to complete the installs. Below is the install for both mac and raspberry pi however please use it as guidance only as I have not done dry installs to re-test it out. This is what I did to succed however the details may need slight tweaking.


# Raspberry Pi Setup Script

------------------------------------------------------------------------------------------------------
```sh
#!/bin/sh
set -ex

################################################################################
# CORE
################################################################################

# Standard updates to a linux system and install python stuff
sudo apt-get update
sudo apt-get upgrade
sudo rpi-update
sudo apt-get install python-dev python-pip

sudo pip install python

# Update ~/.bash_profile to have us use the new version of python. IMPORTANT!!
echo ""
echo ""
echo "Please update ~/.bash_profile adding:"
echo " export PATH=/usr/local/bin:\$PATH"
echo ""
read -n1 -r -p "Then press spacebar to continue..."

# Core util stuff to add
sudo pip install requests
sudo pip install psutil
sudo pip install inflection

# Help docs in markdown for the API
sudo pip install gfm

################################################################################
# WEB SERVER
################################################################################
sudo pip install tornado


################################################################################
# VISION
################################################################################
# Build packages which are necessary
sudo apt-get -y install build-essential git cmake pkg-config

# Image Libs
sudo apt-get -y install libjpeg-dev libtiff-dev libjasper-dev libpng-dev

# Video Libs
sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev

# UI Libs
sudo apt-get -y install libgtk2.0-dev

# Libs to Optimize OpenCV functions
sudo apt-get -y install libatlas-base-dev gfortran

# Pi Camera Interface
sudo pip install picamera

# Python image manipulation
sudo pip install Pillow

# Other
sudo apt-get install default-jdk ant
sudo apt-get install libgtkglext1-dev
sudo apt-get install v4l-utils

# NumPy, SciPi
sudo pip install scipy
sudo pip install numpy

# Install OpenCV 3 - this is fully compiled and saves a ton of steps
# Code is found here https://github.com/jabelone/OpenCV-for-Pi
wget "https://github.com/jabelone/OpenCV-for-Pi/raw/master/latest-OpenCV.deb"
sudo dpkg -i latest-OpenCV.deb

# For fisheye calculations we need this random library
sudo pip install joblib

# Now restart
sudo shutdown -r now

# On Raspberry pi to get OpenCV to recognize the PiCam
sudo modprobe bcm2835-v4l2


################################################################################
# SERVOS
################################################################################
sudo pip install adafruit-pca9685
sudo apt-get install python-smbus
sudo apt-get install i2c-tools


################################################################################
# TTS VOICE
################################################################################
sudo apt-get install espeak


################################################################################
# HEARING SPEECH RECOGNITION
################################################################################
sudo pip install pyaudio

#Installing required libraries
sudo apt-get install alsa-utils
sudo apt-get install alsamixer
sudo apt-get install bison
sudo apt-get install libasound2-dev
sudo apt-get install swig
sudo apt-get install python-dev
sudo apt-get install mplayer

# There is no fully built version of sphinx so we have to build our own here

#Building Sphinxbase

cd ~/
wget http://sourceforge.net/projects/cmusphinx/files/sphinxbase/5prealpha/sphinxbase-5prealpha.tar.gz
tar -zxvf ./sphinxbase-5prealpha.tar.gz
cd ./sphinxbase-5prealpha
./configure --enable-fixed
make clean all
make check
sudo make install

#Building PocketSphinx

cd ~/
wget http://sourceforge.net/projects/cmusphinx/files/pocketsphinx/5prealpha/pocketsphinx-5prealpha.tar.gz
tar -zxvf pocketsphinx-5prealpha.tar.gz
cd ./pocketsphinx-5prealpha
./configure
make clean all
make check
sudo make install
cd ~/
export LD_LIBRARY_PATH=/usr/local/lib
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig

```

## Additional Setup Steps

### Enable Audio Out
You will need to go into the BIOS and enable either the HDMI or 1/8 inch audio out as a default or TTS wil not work.

```sh
sudo raspi-config
```

Then go to advanced and set output to audio out rather than HDMI.

## Enable Microphone in

Remove alsa-base.conf because Raspbian Jessie does not use it like Wheezy did.

```sh
rm /etc/modprobe.d/alsa-base.conf
```

Make the USB microphone default by editing '''/home/pi.asoundrc''' (Create if it doesn't exist). Note that it is a hidden file so if you are using a file browser to open it you need to show hidden files. What you are doing here is setting the index for recording from card 0 to card 1. Card 0 is the internal soundcard which just has audio out.

```
pcm.~default {
    type hw
    card 1
    }
ctl.!default {
    type hw
    card 1
    }
```

### Make sure sound recording works

* To check it, type ```arecord -l``` and make sure it has the "USB" device name there.
* Set the gain for the microphone with ```alsamixer```. Mine started out at 0 for the USB mic and I had to raise it. I set it to 90 to be very responsive.
* Test by recording
*
------------------------------------------------------------------------------------------------------
# Mac OSX Setup Script
To enable easy development, most of the functionality can be executed on a Mac except for the motors which are virtual.

This takes advantage of brew and pip for most of the tasks.

```sh
#!/bin/sh
set -ex

################################################################################
# CORE
################################################################################

#sudo apt-get update
#sudo apt-get upgrade
#sudo rpi-update

sudo pip install python

# Update ~/.bash_profile to have us use the new version of python. IMPORTANT!!
echo ""
echo ""
echo "Please update ~/.bash_profile adding:"
echo " export PATH=/usr/local/bin:\$PATH"
echo ""
read -n1 -r -p "Then press spacebar to continue..."

# Support libs we need
sudo pip install pyobjc
sudo pip install requests
sudo pip install psutil
sudo pip install inflection

# Help docs in markdown for the API
sudo pip install gfm


################################################################################
# WEB SERVER
################################################################################
sudo pip install tornado


################################################################################
# VISION
################################################################################
brew tap homebrew/science

# OpenCV 2 which we are not going to use
# brew install opencv

# Set up paths in python
# cat ~/.bash_profile | grep PYTHONPATH
# ln -s /usr/local/Cellar/opencv/2.4.10/lib/python2.7/site-packages/cv.py cv.py
# ln -s /usr/local/Cellar/opencv/2.4.10/lib/python2.7/site-packages/cv2.so cv2.so

# OpenCV 3
brew cask install cuda
brew install opencv3 --with-contrib --with-ffmpeg --with-tbb --with-qt5

# For fisheye calculations 
sudo pip install joblib

sudo pip install Pillow

# Math libs for algorithm and matrix control
sudo pip install numpy
sudo pip install scipy


################################################################################
# SERVOS
################################################################################

# Nothing is installed given it is virtual.


################################################################################
# TTS VOICE
################################################################################
brew install espeak


################################################################################
# HEARING SPEECH RECOGNITION
################################################################################
# sudo pip install pyaudio 
brew install portaudio

# PocketSphinx needs a custom install for latest
brew tap watsonbox/cmu-sphinx
brew install --HEAD watsonbox/cmu-sphinx/cmu-sphinxbase
brew install --HEAD watsonbox/cmu-sphinx/cmu-pocketsphinx
pip install --ignore-installed six
sudo pip install --upgrade google-api-python-client

```