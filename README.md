# Ancilla

> def: a person whose work provides necessary support to the primary activities of an organization, institution, or industry.

![Robot Head Image](https://dl.dropboxusercontent.com/u/14833653/robothead.jpg "Robot Head")

------------------------------------------------------------------------------------------------------
## Project Goal

Create a social robot which conforms to very simple human social rules and recognizes social cues such as eye contact, facial expressions, speaking and known objects.

## Supported Interactions

The overall goal is to mimic simple human social interaction:

* Move in a humanly natural way, not as a jerky robot
* Respond to people and known objects with attention
* Remember important faces, objects and be able to reference them
* Recognize and respond to facial expressions (Happy, Sad)
* Socially listen to a multi-person conversation following who is talking
* Respond to eye contact by looking back at someone
* Represent a simple set of emotions based on sensor inputs (Boredum, frustration, happiness, anger)
* Make my kids laugh
* ...

------------------------------------------------------------------------------------------------------
# Running the system

0. Check out code base
1. Install all dependencies [from setup script](SETUP.md).
2. Run /src/alive.py to start the robot
3. In your browser, connect to the IP address to watch what is happening

------------------------------------------------------------------------------------------------------
# Overall System Design Philosophy

Having gone through this before in multiple projects, the goal overall is to create a very easy to support set of hardware and software so there are not hidden elements which are going to break or be forgotten in the future. The decisions below are designed to make it easily supportable, cost effective and understandable for new people.

* **Hardware** is off the shelf using hobby servos, standard power supplies, etc
* **Complexity** of mechanics is simple, allowing me to assembly it easily and replace broken parts
* **Processing** is raspberry pi with standard daughter boards and minimal custom wiring
* **Cameras** don't try to push the limits, but instead use standard hardware and libraries

------------------------------------------------------------------------------------------------------
# Processing

The system contains full onboard processing so there are no external computers needed. It also has a full web interface allowing for easy understanding of what is going on inside the system by going to the support URL.

### Parts

* 2x - Raspberry Pi 3

One of the raspberry Pi's is for core processing and the other will be dedicated to environment processing. A 3rd may be necessary if the processing load is too much for controlling the robot and doing vision processing.

## Web Interface

One of the biggest challenges in embedded systems is being able to understand and interact with them successfully. Therefore, I am going to expose the key elements in a password protected web interface.


## Processing Code Libraries

* [Tornado python web server](http://www.tornadoweb.org/)



------------------------------------------------------------------------------------------------------
# Vision

The system will use two cameras to enable both full environment awareness and targeted vision. The reason is that for environmental awareness, background subtraction is the most important step. Knowing what elements matter and what are just walls. If a camera is moving on servos, it is very difficult to guess which pixels correspond to foreground or background data without 3D pixels (Maybe a future project :-) ). Therefore, by using a wide angle static camera, a standard background removal can be done to remove non-salient objects, color clustering can be done to segment the image into elements and then those can be clustered into people, objects, etc.

### Parts

* 1x - Raspberry Camera with 180 degree wide lens to track the entire range in front of the robot. It will be statically mounted on the front of the robot to give a fixed frame of reference for controlling gross movement. The image will be flattened and normalized to create a linear map of the environment from -90 degrees (left) to +90 degrees (right) and vertically from 0 degrees (flat) to 90 degrees (vertical).
* 1x = Raspberry Camera with narrow lens mounted in the robot's eye which is actuated by the servos to create direct eye contact with objects and accurate tracking.

## Vision Code Libraries
* [Raspberry Pi Tornado Websocket video server code](https://github.com/patrickfuller/camp/blob/master/server.py)

## Raspberry Pi Vision Install
'''
sudo apt-get install python-opencv libjpeg-dev


'''
------------------------------------------------------------------------------------------------------
# Movement

Robotic head with 5 DOF raspberry Pi robotic server and motion, video, sensor controller.

* neck rotate - Rotates the whole head left and right 180 degrees
* neck lean - Moves the head forward and backwards 30 degrees
* head tilt - Rotates the head up and down
* eye rotate - Rotates the eye left and right very quickly
* eye iris - Shrinks and enlarges the opening for the eye to show emotion

### Parts

* 1x - [Adafruit 16 channel servo controller](https://www.adafruit.com/product/2327) for Raspberry Pi
* 4x - [RobotGeek 180 degree servo](https://www.robotgeek.com/rg-180-servo)
* 1x - [RobotGeek Snapper Arm](http://www.trossenrobotics.com/rg-snapper-core) (For the bottom 3 servos, bearing and skeleton)

## Movement Code Libraries

* Python servo library for Adafruit 16 channel servo board. [GITHub](https://github.com/adafruit/Adafruit_Python_PCA9685) [Tutorial](https://learn.adafruit.com/adafruit-16-channel-pwm-servo-hat-for-raspberry-pi/using-the-python-library)

### Important Notes on Driving Hobby Servos

#### PWM does not mean PWM
NOTE: Even though servos have a 0 to 3.3 v control signal where 12-bits is 0 to 4095, for these, that will blow it up. The actual range of the server is 150 to 600 on RobotGeek servos. Therefore we need to map that to our positions correctly.

From here: https://www.raspberrypi.org/forums/viewtopic.php?t=32826

.5 ms / 4.8 usec = 104 the number required by our program to position the servo at 0 degreees
1.5 msec / 4.8 usec = 312 the number required by our program to position the servo at 90 degrees
2.5 msec / 4.8 usec = 521 the number required by our program to position the servo at 180 degrees

#### Smooth control of position at slow speeds is hard

The contorller only updates at 50 hz and it seems that the actual position control of servos is only accurate to about 0.5 degrees which means that the whole thing can jitter a LOT. To account for this, we need to adjust the interpolation algorithms.

A few things I have seen online:
* Add a 100uF cap across the power/ground to slow any surges in current making it not jitter as much. I don't think this will matter as much on the larger power supply I have.
* It takes multiple commands before some servos actually start moving, so there can be even bigger delays than commanded.

------------------------------------------------------------------------------------------------------
# Speaking

There are mupltiple 

## TTS Tutorials and resources
* [coding jarvis in python](https://ggulati.wordpress.com/2016/02/24/coding-jarvis-in-python-3-in-2016/)

## TTS Libraries
* [Python wrapper for Flite, Festival, etc](https://pypi.python.org/pypi/talkey/0.1.1)

------------------------------------------------------------------------------------------------------
# Hearing

There are two ways that speech recognition can be implemented. Either local(Sphinx) or cloud based (Amazon, Google). Cloud-based recognition will always be more accurate however there is a larger delay between speech and recognition. If local recognition is to be used, then a small vocabulary should be specified.

## Speech Recognition Libraries
* [Python Speech Recognition w/ Sphinx](https://pypi.python.org/pypi/SpeechRecognition/)
    * pocketsphinx_continuous is a cross-platfrom application which can be executed to listen for a vocabulary



