/*global $, WebSocket, console, window, document*/
"use strict";

/**
 * Connects to Pi server and receives video data.
 */
var client = {

    // Connects to Pi via websocket
    connect: function (port) {
        var self = this, video = document.getElementById("video");

        this.socket = new WebSocket("ws://" + window.location.hostname + ":" + port + "/websocket");

        // Request the video stream once connected
        this.socket.onopen = function () {
            console.log("Connected!");
            //self.enableEnvironmentCamera();
            self.enableState();
        };

        // Currently, all returned messages are video data. However, this is
        // extensible with full-spec JSON-RPC.
        this.socket.onmessage = function (messageEvent) {
            var message = JSON.parse(messageEvent.data);
            if( message.type == 'state' ){
                console.log("Got state");
                state_data.innerHTML = message['data'];
            }
            else if( message.type == 'environment_camera' ) {
                console.log("Got environment camera");
                environment_camera.src = "data:image/jpeg;base64," + JSON.stringify( message['data'] );
            }
            else {
                console.log("Unknown message: " + messageEvent.data);
            }

            //.replace(/\r?\n/g, '<br />');//"data:image/jpeg;base64," + messageEvent.data;
        };
    },

    // Requests video stream
    enableEnvironmentCamera: function () {
        console.log("Requesting video stream!");
        this.socket.send("read_environment_camera");
    },
    // Requests video stream
    enableState: function () {
        console.log("Requesting state stream!");
        this.socket.send("read_state");
    }
};