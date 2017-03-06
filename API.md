# ANCILLA WEB API

&copy; Hans Lee 2017

This web API allows you to securely log in to the robot with both low level and high level control of its functions. Multiple people can log in however users should take care to not overload the server as it is a Raspberry Pi.

#### Key Elements you can Access
* Authentication and session management
* Get state of the robot
    * Servo positions/speeds
    * Servo individual range and max speed
    * Speech - sentences robot has said
    * Hearing - sentences robot has heard
    * Vision
        * Envirnomental Camera (Wide angle on base)
        * Focus Camera (Narrow angle on head)
* Send commands to robot
    * Set Servo position / speed
    * Enable / Disable data streams
    * Visually track objects

## API Elements
The API is divided into two parts where you first authenticate with a password over HTTP then connect to the websocket for fast two-way communication. This allows for multiple or repeated connections to the robot and removes query connection overhead.

## Quickstart Guide

It is easy to connect and start using the system. You should log in to the API using the /login query with your password in the json body. You can then connect to the websocket using the /websocket endpoint. You can then send a websocket message for 'send_state' to start receiving data.

0. PUT to http://server_url:port/login with body of {"password":"{SECRET}"}
1. OPEN http://server_url:port/websocket as a client side websocket
2. Send a json formatted "send_state" true message to enable state blob
3. Send a json formatted "send_environment_camera" true message to enable frames
4. Listen for "state" message and JSON data
5. Listen for "environment_camera_frame" message and data blob
6. Always lisen for "error" messages to find issues
----------------------------------------------------------------------------------------------
# Authentication API

## [/ base URL](/) 
**(GET)** Returns a JSON object if logged in.

#### Response

If logged in, a json object with: HTTP 200

    {
        "api_docs": "http://{base server url}/docs"
        "booted": "2039-03-01 21:30",
        "status": "logged in", 
        "total_connections": 8
        "uptime": "12h 43m 11s",
        "your_connections": 3,
    }

If not logged in, a json object with: HTTP 401

    {
        "api_docs": "http://{base server url}/docs"
        "error": "not logged in"
        "message": "Please look at the api documentation to learn how to log in.", 
    }

## [/docs](/docs) 
**(GET)** Returns a HTML page with this GITHub markdown formatted API document defining the spec for the full API. You do not have to be logged in to access it.

## [/login](/login)
**(GET, PUT, POST)** Allows a user to authenticate themselves with the system password, allowing them to connect to the websocket API in the future. Multiple HTTP methods are allowed to enable easy programmatic (hacking) access to the system.

If you are currently logged in and call /login with an incorrect password, it will log you out of the system. If you are currently logged in and call it with a missing password, it will not log you out.

#### Request Body
The body must be of content-type 'application/json' with a payload of:

    {"password":"SECRET"}

#### Response

If correct password: HTTP 200

    {
        "status": "success", 
    }

If incorrect password: HTTP 401

    {
        "error": "incorrect password"
    }

If no password specified in body: HTTP 401

    {
        "error": "no password specified"
    }

## [/logout](/logout)
**(GET)** logs the user out of the system by removing the encrypted cookie.

#### Response

If logged in, a json object with: HTTP 200

    {
        "status": "successfully logged out",
        "websocket_connections_closed": 1
    }

If not logged in, a json object with: HTTP 401

    {
        "error": "not logged in"
        "api_docs": "http://{base server url}/docs"
        "message": "Please look at the api documentation to learn how to log in.", 
    }

## [/shutdown](/shutdown) 
**(GET)** Cleanly shuts down the robot. The WebSocket shutdown message can also be used to do this depending on how you are connected. You should not send websocket or http messages to the API after this point as there may be a small amount of time before it stops taking messages where behavior will not be guaranteed.

#### Response

If logged in, a json object with: HTTP 200

    {
        "status": "shutting down"
    }

If not logged in, a json object with: HTTP 401

    {
        "error": "not logged in"
        "api_docs": "http://{base server url}/docs"
        "message": "Please look at the api documentation to learn how to log in.", 
    }

## [/websocket](/websocket)
**(Websocket Connection)** Opens a connection to the server for message passing. See below for formatting definitions. This should be used for all control functions.

#### Authentication
401 if not logged in. You must call /login successfully before and pass in the encrypted cookie to open a connection.

----------------------------------------------------------------------------------------------

# Websocket API

The websocket connection is how most communication with the system is accomplished. 

#### Session Management
You may connect to the server with as many websockets as you want with the current authentication token given when you logged in. That said, we recommend keeping the number very small as it can quickly overload the server (Especially when videos are turned on).

All websocket connections for the specific user will be logged out if /logout is called and every websocket connection will be closed if /shutdown is called.

#### Standard Format

The server uses formatted JSON messages to identify which content is being sent or received. A JSON dictionary is sent with at least the "message" element with a value which is a known string representing a message type defined in this document. The string is usually 5-20 characters long and human readable. It specifies fully what the rest of the content will be.

```js
{
    "message": "KNOWN_MESSAGE_NAME", // Only necessary element
    "attribute_1": "value",
    "attribute_2": 2,
    "attribute_3": {"a": 1, "b":2}
}
```

----------------------------------------------------------------------------------------------
# Input Websocket Messages

Messages which can be sent to the system by the client are defined below.

## send_state

Toggles if the system sends out the large "state" blob of everything and defined a given number of messages per second to send. As the robot only updates itself at a maximum of 50 hz and there is real-world lag, usually 10hz or less makes sense for real data.

#### Example Message
```js
{
    "message": "send_state",
    "enable": true  // true or false to turn on and off sending state message
    "mps": 10 // number of messages to send out each second from 1 to 30
}
```

## send_environment_camera

Turns on or off sending frames of video from the wider environment camera at the base of the robot. It should usually be requested at a slow frame rate as the goal is to understand the overall environment just like our peripheral vision as humans, not target fast moving objects (Focus camera is for this).

Because the robot has to transcode and send out each frame, 5-10 hz maximum is recommended with 5hz as the standard value for the environment camera.

#### Example Message
```js
{
    "message": "send_environment_camera",
    "enable": true,  // true or false to turn on and off 
    "fps": 5 // number of frames per second to send between 1 and 10
}
```

## send_focus_camera

Turns on or off sending frames of video from the narrow focus camera on they "eye" of the robot. It is meant for defining regions to track.

Because the robot has to transcode and send out each frame, 5-15 hz maximum is recommended with 10hz as the standard value for the focus camera.

#### Example Message
```js
{
    "message": "send_focus_camera",
    "enable": true,  // true or false to turn on and off 
    "fps": 5 // number of frames per second to send between 1 and 10
}
```
## set_focus_camera_tracking_region_of_interest

Sets a region of image from a previous focus frame to use for tracking. This will enable the "focus_region_tracking" control type and will have the camera look at the best approximation of that region of interest. 

Because the aspect ratio and orientation of objects changes over time, the tracking region should be updated at a regular interval such as 2 hz to account for these changes.

Types of elements to track:

* 'face'
* 'object'

#### Example Message
```js
{
    "message": "set_focus_camera_tracking_region_of_interest",
    "image_data": "4a4ag243ADAHFDSH...",  //base64 encoded image data
    "data_type": "image/jpg",
    "width": 100,
    "height": 100
}
```

## set_control_type
Not yet implemented.
#### Example Message
```js
{
    "message": "set_control_type",
    "type": "position"  // "position", "focus_region_tracking"
}
```

## set_servo_position

Sets the commanded position for a dimension 

#### Example Message
```js
{
    "message": "set_servo_position",
    "servo_name": "neck_rotate", // "neck_rotate", "neck_lean", "head_lean", "head_tilt", "eye_eyeris"
    "angle": 50, // from min to max for this dimension
    "speed": 10  // degrees per second
}
```

## shutdown

Immediately shut down robot and stop all processes. This will also disconnect the websocket connection at the end. It should only be used for powering down the system when fully done.

#### Example Message
```js
{
    "message": "shutdown"
}
```

----------------------------------------------------------------------------------------------
# Output Websocket Messages

These are the messages which can come back from the robot when enabled by an input message.

## state

A full "whiteboard" of the current state of all systems and their parameters. This is the core message which defines the current state of all dimensions of the robot plus the constants for each dimension to help the user interpret the data dynamically. It is a fully described format.

A few key elements:

* Speed is in degrees per second in real-world space
* Each dimension has a bound on the angle it can traverse
* Each dimension has a maximum speed for moving which corresponds to the correct 'feel' for that dimension. Some things such as eyes can move very fast while others move quite slow.
* If you set a position or speed outside of the bounds, it will accept it but only move to the maximal point.
* The number and type of servo may change dynamically.

#### Example Message
```js
{
    "message": "state",
    "data": {
        "movement":{
            "servos": {
                "head_rotate": }
                    "requested_speed": 10,          // Current requested speed for last move
                    "current_speed": 0,             // Current speed for current move
                    "requested_angle": 30,          // Requested end angle
                    "current_angle": 30,            // Current angle
                    "resting_angle": 0,             // Position to go to when at rest
                    "hardware_zero_offset": -90,    // READ ONLY: All servos are 0 to 180 degreees. Translate by this to center things
                    "precision_threshold_angle": 3, // READ ONLY: Number of degrees where we are "close" and should start decelerating
                    "servo_index": 1,               // READ ONLY: Hardware index of servo
                    "max_speed": 20,                // READ ONLY: Max speed allowed
                    "min_angle": -50,               // READ ONLY: Minimum angle before it stops
                    "max_angle": 50                 // READ ONLY: Maximum angle after hardware_zero_offset to move before it stops
                },  
                "head_lean": { ... },
                "neck_lean": { ... },
                "head_tilt": { ... },
                "eye_rotate": { ... },
                "eye_eyeris": { ... }
            }
        }
    }
    }
}
```

## environment_camera_frame

The environment camera is a normalized ~180 degree camera used for periperal awareness of objects and to guide the overall movement of the robot. It is a fixed camera which is centered vertically and horizontally. Usually it updates at ~5 hz as it is meant to be a background set of data and is not for fast tracking.

The data which describes the frame of video for the camera including base64 encoded data of the image, image type, size, etc. 

Because the camera has a fish-eye lense, the image is pre-normalized and scaled before it comes out. This significantly helps in interpretation of the data but is not perfect so expect some warping. The image may also be downsampled as it is a background image so a full 1080p frame is not appropriate (and would slow down processing / transmission significantly).

#### Example Message
```js
{
    "message": "environment_camera_frame",
    "image_data": "4a4ag243ADAHFDSH...",  //base64 encoded image data
    "data_type": "image/jpg",
    "width": 640,
    "height": 480
}
```

#### Usage

To use this image data in HTML, you can prepend 'data:image/jpeg;base64' to the 'image_data' and pass it in as the 'src' variable for an image element on the page or load it as a data blob into a canvas. 

## focus_camera_frame

The focus camera is attached to the head of the robot and moves with all of the elements of the robot. It is a narrow-field camera meant for detailed tracking to make 'eye contact' with the person or object in front of the robot. It is always aligned with the front plane of the robot's face so centering the camera on an object will make the robot look at it.

The data which describes the frame of video for the camera including base64 encoded data of the image, image type, size, etc. 

#### Example Message
```js
{
    "message": "focus_camera_frame",
    "image_data": "4a4ag243ADAHFDSH...",  //base64 encoded image data
    "data_type": "image/jpg",
    "width": 640,
    "height": 480
}
```

#### Usage

To use this image data in HTML, you can prepend 'data:image/jpeg;base64' to the 'image_data' and pass it in as the 'src' variable for an image element on the page or load it as a data blob into a canvas.

## error

Errors can be either in response to a message sent to the system or from an internal system issue. They are considered informational and will change the workings of the system but are not fatal and will not shut it down.

#### Example Message
```js
{
    "message": "error",
    "type": "error",
    "description": "Description text goes here",
    "stack trace": "..." // optional multi-line stack trace of where the error happened
}
```

## fatal_error

If a fatal error message is received, the system will immediately shut down so this should be used to log the error on the browser but no further commands should be sent and the system should assume 

#### Example Message
```js
{
    "message": "error",
    "type": "fatal",
    "description": "Description text goes here",
    "stack trace": "..." // optional multi-line stack trace of where the error happened
}
```


## shutdown

If the system is shut down either from a user of this API or from the hardware side of the system, it will endevour to send out a 'shutdown' message, however this is not guaranteed if there is a major issue. It can also have an optional 'reason' why the shut down happened.

#### Example Message
```js
{
    "message": "shutdown"
    "reason": "" //Optional reason why the system was shut down
}
```





