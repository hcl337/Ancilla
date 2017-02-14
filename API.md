# Websocket API

The websocket connection is how most communication with the system is accomplished. 

## Standard Format

It uses formatted JSON messages to identify which content is being sent or received. A JSON dictionary is sent with at least the "message" element with a value which is a string. The string is usually 5-20 characters long and human readable. It specifies fully what the rest of the content will be.

```js
{
    "message": "MESSAGE_NAME", // Only necessary element
    "attribute_1": "value",
    "attribute_2": 2,
    "attribute_3": {"a": 1, "b":2}
}
```

## Quickstart guide

It is easy to connect and start using the system.

0. POST to http://ip:8888/login?password=SECRET
1. OPEN http://ip:8888/websocket as a client side websocket
2. Send a json formatted "send_state" true message to enable state blob
3. Send a json formatted "send_environment_camera" true message to enable frames
4. Listen for "state" message and JSON data
5. Listen for "environment_camera_frame" message and data blob
6. Always lisen for "error" and "fatal_error" messages to find issues

----------------------------------------------------------------------------------------------
# Input Websocket Messages

Messages which can be sent to the system by the client

### send_state

Toggles if the system sends out the large "state" blob of everything.   

```js
{
    "message": "send_state",
    "enable": false  // true or false to turn on and off sending state message
    "mps": 10 // number of messages to send out each second from 1 to 30
}
```

### send_environment_camera

Turns on or off sending frames of video from the wider environment camera at the base of the robot. It should usually be requested at a slow frame rate as the goal is to understand the overall environment just like our peripheral vision as humans, not target fast moving objects (Focus camera is for this).

```js
{
    "message": "send_environment_camera",
    "enable": true,  // true or false to turn on and off 
    "fps": 5 // number of frames per second to send between 1 and 10
}
```

### send_focus_camera

Turns on or off sending frames of video from the narrow focus camera on they "eye" of the robot. It is meant for defining regions to track.

```js
{
    "message": "send_focus_camera",
    "enable": true,  // true or false to turn on and off 
    "fps": 5 // number of frames per second to send between 1 and 10
}
```
### set_focus_camera_tracking_region_of_interest

Sets a region of image from a previous focus frame to use for tracking. This will enable the "focus_region_tracking" control type and will have the camera look at the best approximation of that region of interest. 

Because the aspect ratio and orientation of objects changes over time, the tracking region should be updated at a regular interval such as 2 hz to account for these changes.

Types of elements to track:
* Faces
* Objects

```js
{
    "message": "set_focus_camera_tracking_region_of_interest",
    "image_data": "4a4ag243ADAHFDSH...",  //base64 encoded image data
    "data_type": "jpg",
    "width": 100,
    "height": 100
}
```

### set_control_type

```js
{
    "message": "set_control_type",
    "type": "position"  // "position", "focus_region_tracking"
}
```

### set_servo_position

Sets the commanded position for a dimension 

```js
{
    "message": "set_servo_position",
    "servo_name": "neck_rotate", // "neck_rotate", "neck_lean", "head_lean", "head_tilt", "eye_eyeris"
    "angle": 50, // from min to max for this dimension
    "speed": 10  // degrees per second
}
```

### shutdown

Immediately shut down robot and stop all processes. This will also disconnect the websocket connection at the end. It should only be used for powering down the system when fully done.

```js
{
    "message": "shutdown"
}
```

----------------------------------------------------------------------------------------------
# Output Websocket Messages

Messages which can come back from the robot when enabled.

### state

A full "whiteboard" of the current state of all systems and their parameters.

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

### environment_camera_frame

The data which describes the frame of video for the camera including base64 encoded data of the image, image type, size, etc.

```js
{
    "message": "environment_camera_frame",
    "image_data": "4a4ag243ADAHFDSH...",  //base64 encoded image data
    "data_type": "jpg",
    "width": 640,
    "height": 480
}
```


### focus_camera_frame

The data which describes the frame of video for the camera including base64 encoded data of the image, image type, size, etc.

```js
{
    "message": "focus_camera_frame",
    "image_data": "4a4ag243ADAHFDSH...",  //base64 encoded image data
    "data_type": "jpg",
    "width": 640,
    "height": 480
}
```

### error

Errors can be either in response to a message sent to the system or from an internal system issue. They are considered informational and will change the workings of the system but are not fatal and will not shut it down.

```js
{
    "message": "error",
    "type": "exception",
    "description": "Description text goes here",
    "stack trace": "..." // optional multi-line stack trace of where the error happened
}
```

### fatal_error

If a fatal error message is received, the system will immediately shut down so this should be used to log the error on the browser but no further commands should be sent and the system should assume 

```js
{
    "message": "error",
    "description": "Description text goes here",
    "stack trace": "..." // optional multi-line stack trace of where the error happened

}
```


### shutdown







