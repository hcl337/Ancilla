# API Documentation

[Back to main readme](/../README.md)

## How to use the API

### Web Client
On a local network, enter the web address of the core Raspberry Pi in your browser and press enter. Enter your super-secret password. That is all you need to do!

### Direct API Access

    /                                                                       
    /update
    /setmode
    /connect


#### WebSocket Output Messages
    
    periferial_video    Raw frame of video
    focus_video         Raw frame of video
    raw_sensors
    visual_objects
    error

#### WebSocket Input Messages

    set_mode            {"mode": "raw"} from set of modes ["raw", "position", "object", "autonomous"]
    set_raw_dimension   {"JSON of a subset of the raw named dimensions. If a value is outside bounds, an error message will be returned.
    set_position        JSON of the visual 
    set_object
    set_emotion         

#### Modes

    position            define a position and velocity for each motor and LED
    object              define a named object for the system to track
    autonomous          allow the system to identify which objects are most interesting to interact with


#### Raw Dimensions

* neck_rotate
    * DESCRIPTION: Rotates the whole head left and right
    * RANGE: -90 to 90 degrees
    * MAX SPEED: 90 degrees / second
* neck_lean
    * DESCRIPTION: Moves the head forward and backwards 
    * RANGE -30 to +30 degrees
    * MAX SPEED: 60 degrees / second
* head_tilt
    * DESCRIPTION: Rotates the head up and down
    * RANGE: +45 to -15 degrees
    * MAX SPEED: 120 degrees / second
* eye_rotate
    * Rotates the eye left and right very quickly from -30 to 30 degrees
    * MAX SPEED: 90 degrees / second
* eye_iris
    * Shrinks and enlarges the opening for the eye to show emotion from 0 to 100 %
    * MAX SPEED: 90 degrees / second



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
    * View cameras
    * View known objects
    * Raw controller: Input motor, LED positions
    * High level controller: Follow objects, people, etc


Implementation

The API is implemented in Tornado in Python