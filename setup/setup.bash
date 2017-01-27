

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

# Now install pic image drivers
sudo pip install picamera



################################################################################
## MOTORS
################################################################################

# Install the Adafruit Servo drivers for python
# https://github.com/adafruit/Adafruit_Python_PCA9685
sudo pip install adafruit-pca9685


# Festival Text to Speech for embedded systems. (Flite)
# https://learn.adafruit.com/speech-synthesis-on-the-raspberry-pi
sudo apt-get install flite