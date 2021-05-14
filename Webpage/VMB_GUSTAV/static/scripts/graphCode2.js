// Event (START) --------------------------------------------------
// Get IP of the server
ip = location.host;

/*
Create connection between websocket (server) and client
These websockets are bound to client and server when the client asks for the permission to go into
"ws:/" url specified in the "routing.py" path that is connected with "asgi.py" file
*/
let socketButton = new WebSocket(`ws://${ip}/ws/receiveButton/`);
let socketControlState = new WebSocket(`ws://${ip}/ws/controlState/`);

/*
All events must be bound after the objects are build
because otherwise you get a empty object that is not built yet
That's why we wait till the whole page is built finish
 */
// Add events
for (i = 1; i <= 3; i++) {
    // Convert to string
    let number = i.toString();

    // Ad events to object clicks and bind it to a function
    document.getElementById("buttonON" + number).addEventListener("click", buttonTrigger, false);
    document.getElementById("buttonOFF" + number).addEventListener("click", buttonTrigger, false);
}

// Control state update
controlState();


// Control state MANUAL[1]/AUTO[0]
function controlState() {
    socketControlState.onmessage = function (e) {
        // Variable
        let count = 0;

        // Get all the data the message has sent
        let serverData = JSON.parse(e.data);

        /*
        Set the state of button
        If AUTO[0] => Button show
        If MANUAL[1] => Denial show
        */
        for (let controlStateTank in serverData) {
            // Variables
            count += 1;
            let cst = serverData[controlStateTank];

            // Get objects
            let buttonON = document.getElementById("buttonON" + count.toString());
            let buttonOFF = document.getElementById("buttonOFF" + count.toString());
            let ControlDennie = document.getElementById("ControlDennie" + count.toString());

            // Logic
            if (cst == "0") {
                // Show buttons
                buttonON.style.display = "block";
                buttonOFF.style.display = "block";

                // Hide dennie panel
                ControlDennie.style.display = "none";
            }
            else {
                // Show buttons
                buttonON.style.display = "none";
                buttonOFF.style.display = "none";

                // Hide dennie panel
                ControlDennie.style.display = "block";
            }
        }
    }
}


// On button click send message
function buttonTrigger() {
    // Get the id name of the object that has been passed
    let id = this.id;

    /*
    Get id ON/OFF value without number
    Get values from start til the last one
    */
    let idName = id.substr(0, (id.length - 1));
    let idValue = id[id.length - 1];

    // Send data back to server in JSON format
    socketButton.send(JSON.stringify(id));

    // Go through logic and select right color
    if (idName == "buttonON") {
        // Get the opposite button object
        let oppositeObject = document.getElementById("buttonOFF" + idValue);

        // Set color
        this.style.backgroundColor = "rgb(0, 255, 0)";
        oppositeObject.style.backgroundColor = "rgb(150, 100, 100)";
    }
    else {
        // Get the opposite button object
        let oppositeObject = document.getElementById("buttonON" + idValue);

        // Set color
        this.style.backgroundColor = "rgb(255, 0, 0)";
        oppositeObject.style.backgroundColor = "rgb(100, 150, 100)";
    }
}


