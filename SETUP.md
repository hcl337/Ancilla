
[Back to main readme](README.md).
Setting up the system fully takes a few hours to complete the installs. Below is the install for both mac and raspberry pi however please use it as guidance only as I have not done dry installs to re-test it out. This is what I did to succed however the details may need slight tweaking.


# Raspberry Pi Setup Script

------------------------------------------------------------------------------------------------------
```
################################################################################
# CORE
################################################################################

sudo apt-get update
sudo apt-get upgrade
sudo rpi-update
sudo apt-get install python-dev python-pip

sudo pip install python

# Update ~/.bash_profile to have
# export PATH=/usr/local/bin:$PATH

sudo pip install pyobjc
sudo pip install requests
sudo pip install psutil

################################################################################
# WEB SERVER
################################################################################
sudo pip install tornado


################################################################################
# VISION
################################################################################
sudo apt-get install python-opencv libjpeg-dev
sudo apt-get install build-essential git cmake pkg-config
sudo apt-get install libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libgtk2.0-dev
sudo apt-get install libatlas-base-dev gfortran
sudo pip install picamera
sudo pip install numpy
sudo pip install Pillow


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
#Installing build tools and required libraries

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install bison
sudo apt-get install libasound2-dev
sudo apt-get install swig
sudo apt-get install python-dev
sudo apt-get install mplayer

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

------------------------------------------------------------------------------------------------------
# Mac Setup Script
To enable easy development, most of the functionality can be executed on a Mac except for the motors which are virtual.

This takes advantage of brew for many of the tasks.

```
################################################################################
# CORE
################################################################################

sudo apt-get update
sudo apt-get upgrade
sudo rpi-update

sudo pip install python

# Update ~/.bash_profile to have
# export PATH=/usr/local/bin:$PATH

sudo pip install pyobjc
sudo pip install requests
sudo pip install psutil

################################################################################
# WEB SERVER
################################################################################
sudo pip install tornado


################################################################################
# VISION
################################################################################
brew tap homebrew/science
brew install opencv
sudo pip install numpy
# Set up paths in python
cat ~/.bash_profile | grep PYTHONPATH
ln -s /usr/local/Cellar/opencv/2.4.10/lib/python2.7/site-packages/cv.py cv.py
ln -s /usr/local/Cellar/opencv/2.4.10/lib/python2.7/site-packages/cv2.so cv2.so

sudo pip install picamera
sudo pip install numpy
sudo pip install Pillow


################################################################################
# SERVOS
################################################################################

# Nothing is installed given it is virtual

################################################################################
# TTS VOICE
################################################################################
brew install espeak


################################################################################
# HEARING SPEECH RECOGNITION
################################################################################
sudo pip install pyaudio
brew install portaudio

# PocketSphinx needs a custom install for latest
brew tap watsonbox/cmu-sphinx
brew install --HEAD watsonbox/cmu-sphinx/cmu-sphinxbase
brew install --HEAD watsonbox/cmu-sphinx/cmu-pocketsphinx
pip install --ignore-installed six
sudo pip install --upgrade google-api-python-client
```