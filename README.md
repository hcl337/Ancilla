# Ancilla

*def: a person whose work provides necessary support to the primary activities of an organization, institution, or industry.*

## Project Goal

Create a social robot which conforms to very simple human social rules and recognizes social cues such as eye contact, facial expressions, speaking and known objects.

## Supported Interactions

The overall goal is to mimic simple human social interaction

* Move in a humanly natural way, not as a jerky robot
* Track people and known objects visually and with motor positions
* Remember important faces, objects and be able to reference them
* Recognize and respond to facial expressions
* Socially listen to a multi-person conversation following who is talking
* Respond to eye contact by looking back at someone
* Represent a simple set of emotions based on sensor inputs (Boredum, frustration, happiness, anger)
* ...

# Processing

Having gone through this before, the goal overall is to create a very easy to support set of hardware and software so there are not hidden elements which are going to break or be forgotten in the future. The decisions below 

## Processing Hardware

* 2x - Raspberry Pi 3

One of the raspberry Pi's is for core processing and the other will be dedicated to environment processing. A 3rd may be necessary if the processing load is too much for controlling the robot and doing vision processing.

## Web Interface

One of the biggest challenges in embedded systems is being able to understand and interact with them successfully. Therefore, I am going to expose the key elements in a password protected web interface.

* Websocket
    * Output
        * Video
        * Raw sensor / motor values
        * Object tracking
    * Input
        * Raw motor positions
        * LED colors
        * High level robot positioning
            * Object following
            * "Emotional state"
* Actions
    * restartSystem - Shuts down all running code, does a GIT checkout and restarts
    * setControlMode [raw, natural, guidance, autonomous] - allows for either raw motor commands, naturally damped angle commands, high level guidance or fully autonomous motion based on inputs. This changes what commands can be sent into the system.
* HTML User Interface
    * Visualize raw motor position
    * View camera 
    * Raw controller: Input motor, LED positions
    * High level controller: Follow objects, people, etc

## Vision Hardware

The system will use two cameras to enable both full environment awareness and targeted vision. The reason is that for environmental awareness, background subtraction is the most important step. Knowing what elements matter and what are just walls. If a camera is moving on servos, it is very difficult to guess which pixels correspond to foreground or background data without 3D pixels (Maybe a future project :-) ). Therefore, by using a wide angle static camera, a standard background removal can be done to remove non-salient objects, color clustering can be done to segment the image into elements and then those can be clustered into people, objects, etc.

* 1x - Raspberry Camera with 180 degree wide lens to track the entire range in front of the robot. It will be statically mounted on the front of the robot to give a fixed frame of reference for controlling gross movement. The image will be flattened and normalized to create a linear map of the environment from -90 degrees (left) to +90 degrees (right) and vertically from 0 degrees (flat) to 90 degrees (vertical).
* 1x = Raspberry Camera with narrow lens mounted in the robot's eye which is actuated by the servos to create direct eye contact with objects and accurate tracking. 

## Skeleton and Motors

Robotic head with 5 DOF raspberry Pi robotic server and motion, video, sensor controller.

* neck rotate - Rotates the whole head left and right 180 degrees
* neck lean - Moves the head forward and backwards 30 degrees
* head tilt - Rotates the head up and down
* eye rotate - Rotates the eye left and right very quickly
* eye iris - Shrinks and enlarges the opening for the eye to show emotion

### Skeleton and Motor Hardware

* 1x - [Adafruit 16 channel servo controller](https://www.adafruit.com/product/2327) for Raspberry Pi
* 4x - [RobotGeek 180 degree servo] (https://www.robotgeek.com/rg-180-servo)
* 1x - [RobotGeek Snapper Arm](http://www.trossenrobotics.com/rg-snapper-core) (For the bottom 3 servos) 

## Movement Code Libraries

* Python servo library for Adafruit 16 channel servo board. [GITHub](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code) [Tutorial](https://learn.adafruit.com/adafruit-16-channel-pwm-servo-hat-for-raspberry-pi/using-the-python-library)





