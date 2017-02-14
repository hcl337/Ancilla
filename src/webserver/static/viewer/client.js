/*global $, WebSocket, console, window, document*/
"use strict";

/**
 * Connects to Pi server and receives video data.
 */
var client = {
    degrees_per_second: 10,
    errors: "",
    environment_frame:"",
    focus_frame:"",
    state:{},
    // Connects to Pi via websocket
    connect: function (port) {
        var self = this, video = document.getElementById("video");

        this.socket = new WebSocket("ws://" + window.location.hostname + ":" + port + "/websocket");

        // Request the video stream once connected
        this.socket.onopen = function () {
            console.log("Connected!");
            self.enableState( true );
            self.enableEnvironmentCamera(true);

        };

        // Currently, all returned messages are video data. However, this is
        // extensible with full-spec JSON-RPC.
        this.socket.onmessage = function (messageEvent) {
            var message = JSON.parse(messageEvent.data);
            console.log(message);
            if( message.message == 'state' ){
                console.log("Got state");
                this.state = message.data,
                state_data.innerHTML = JSON.stringify( message.data, null, 2 );

                var c=document.getElementById("environment_camera");
                if (c != null){
                    var ctx=c.getContext("2d");
                    ctx.rect(20,20,150,100);
                    ctx.stroke();                
                }
            }
            else if( message.message == 'environment_camera_frame' ) {
                console.log("Got environment camera");
                environment_camera.src = "data:image/jpeg;base64," + message['image_data'];
            }
            else if( message.message == 'focus_camera_frame' ) {
                console.log("Got focus camera");
                frame_camera.src = "data:image/jpeg;base64," + message['image_data'];
            }
            else if( message.message == 'error'){
                this.errors += JSON.stringify(message) + "<br/>";
                errors_list.innerHTML = this.errors
            }
            else {
                console.log("Unknown message: " + messageEvent.data);
            }

            //.replace(/\r?\n/g, '<br />');//"data:image/jpeg;base64," + messageEvent.data;
        };
    },
    setSpeed: function( degrees_per_second) {
        this.degrees_per_second = degrees_per_second;
    },

    move: function (servo_name, angle, speed) {
        console.log("Requesting servo move!");
        var message = {"message":"set_servo_position", "servo_name":servo_name, "angle":angle, "speed":speed }
        this.socket.send(JSON.stringify(message));
    },
    // Requests video stream
    enableEnvironmentCamera: function ( enable ) {
        console.log("Requesting env video stream!");
        var message = {"message":"send_environment_camera", "fps":5, "enable":enable }
        this.socket.send(JSON.stringify(message));
    },
    // Requests video stream
    enableFocusCamera: function ( enable ) {
        console.log("Requesting focus video stream!");
        var message = {"message":"send_focus_camera", "fps":5, "enable":enable }
        this.socket.send(JSON.stringify(message));
    },
    shutdown: function () {
        console.log("MESSAGE: Shut down!");
        var message = {"message":"shutdown"}
        this.socket.send(JSON.stringify(message));
        document.body.innerHTML = "<h1>Server Shut Down</h1>"
    },
    // Requests video stream
    enableState: function ( enable ) {
        console.log(enable)
        var message = {"message":"send_state", "enable":enable, "mps":10 }
        message = JSON.stringify(message)
        console.log("Requesting state stream: " + message);
        this.socket.send(message);
    }
};