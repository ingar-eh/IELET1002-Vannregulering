// Event (START) --------------------------------------------------
// Get IP of the server
let ip = location.host;

/*
Create connection between websocket (server) and client
These websockets are bound to client and server when the client asks for the permission to go into
"ws:/" url specified in the "routing.py" path that is connected with "asgi.py" file
*/
let socket1 = new WebSocket(`ws://${ip}/ws/graph/`);
let socket2 = new WebSocket(`ws://${ip}/ws/recommend/`);
let socket3 = new WebSocket(`ws://${ip}/ws/receiveMenuTimeline1/`);
let socket4 = new WebSocket(`ws://${ip}/ws/receiveMenuTimeline2/`);


/*
All events must be bound after the objects are build
because otherwise you get a empty object that is not built yet
That's why we wait till the whole page is built finish
 */
// Functions for level graphs
graphDisplay();

// Function for recommendations
recommend();

// Set event functions for changing level graph timelines with buttons
document.getElementById("menu1-1min").addEventListener("click", menuTimeline1, false);
document.getElementById("menu1-10min").addEventListener("click", menuTimeline1, false);
document.getElementById("menu1-1h").addEventListener("click", menuTimeline1, false);
document.getElementById("menu1-24h").addEventListener("click", menuTimeline1, false);
document.getElementById("menu1-ALL").addEventListener("click", menuTimeline1, false);

// Set event functions for changing price graph timeline with buttons
document.getElementById("menu2-1h").addEventListener("click", menuTimeline2, false);
document.getElementById("menu2-24h").addEventListener("click", menuTimeline2, false);
document.getElementById("menu2-ALL").addEventListener("click", menuTimeline2, false);


// Functions for level graphs
function graphDisplay() {
    // The Charts.js graph style
    let dataGraph1 = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "Tank 1 [mm]",
                data: [],
                backgroundColor: 'rgba(0,30,252,0.9)',
                borderColor: 'rgba(0,30,252,0.9)',
                borderWidth: 0.5,
                pointRadius: 1,
                pointHoverRadius: 5
            }]
        },
        options: {}
    }
    let dataGraph2 = {
        type: 'line',
        data: {
            labels: ['1', '2', '3', '4', '5', '6', "7", "8", "9", "10"],
            datasets: [{
                label: 'Tank 2 [mm]',
                data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                backgroundColor: 'rgba(30,255,0,0.9)',
                borderColor: 'rgba(30,255,0,0.9)',
                borderWidth: 0.5,
                pointRadius: 1,
                pointHoverRadius: 5
            }]
        },
        options: {}
    }
    let dataGraph3 = {
        type: 'line',
        data: {
            labels: ['1', '2', '3', '4', '5', '6', "7", "8", "9", "10"],
            datasets: [{
                label: 'Tank 3 [mm]',
                data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                backgroundColor: 'rgba(255,0,30,0.9)',
                borderColor: 'rgba(255,0,30,0.9)',
                borderWidth: 0.5,
                pointRadius: 1,
                pointHoverRadius: 5
            }]
        },
        options: {}
    }
    let dataGraph4 = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "Priser [kWh]",
                data: [],
                backgroundColor: 'rgba(200,0,200,0.9)',
                borderColor: 'rgba(200,0,200,0.9)',
                borderWidth: 1,
                pointRadius: 0.5,
                pointHoverRadius: 5
            }]
        },
        options: {}
    }

    // Get canvases
    let canvas1 = document.getElementById('graph1').getContext("2d");
    let canvas2 = document.getElementById('graph2').getContext("2d");
    let canvas3 = document.getElementById('graph3').getContext("2d");
    let canvas4 = document.getElementById('graph4').getContext("2d");

    // Make charts
    let chart1 = new Chart(canvas1, dataGraph1);
    let chart2 = new Chart(canvas2, dataGraph2);
    let chart3 = new Chart(canvas3, dataGraph3);
    let chart4 = new Chart(canvas4, dataGraph4);

    /*
    Go into that url and get messages sent to it from user connections
    Function expects to get a message event and that's when it reacts
    */
    socket1.onmessage = function (e) {
        /*
        Get all the data the message has sent
        the message is formatted to be JSON as a string
        Analyse event message data in JSON format, because we know it was sent as JSON string
        */
        let serverData = JSON.parse(e.data);

        // Replace data from graph with data that was sent from the server
        dataGraph1.data.datasets[0].data = serverData["level1"]["height"];
        dataGraph2.data.datasets[0].data = serverData["level2"]["height"];
        dataGraph3.data.datasets[0].data = serverData["level3"]["height"];
        dataGraph4.data.datasets[0].data = serverData["prices"]["prices"];

        // Replace timestamps from graph with timestamps sent from server
        dataGraph1.data.labels = serverData["level1"]["time"];
        dataGraph2.data.labels = serverData["level2"]["time"];
        dataGraph3.data.labels = serverData["level3"]["time"];
        dataGraph4.data.labels = serverData["prices"]["time"];

        // Update the chart with new data that was set in respective dataGraphs
        chart1.update();
        chart2.update();
        chart3.update();
        chart4.update();
    }
}


// Recommendations
function recommend() {
    /*
    Draw function
    Draw rectangle according to recommendation value
    If good recommendation the color will be green and rectangle big
    If bad recommendation the color will be red and rectangle small
    */
    function draw(canvas, recommend) {
        // Get canvas objects width and height
        let canvasWidth = canvas.width;
        let canvasHeight = canvas.height;

        // Take context from canvas
        let ctx = canvas.getContext("2d");

        // Select color to fill canvas objects with
        ctx.fillStyle = "rgb(200, 200, 200)";

        // Fill the background
        ctx.fillRect(0, 0, canvasWidth, canvasHeight);

        // Select color
        ctx.fillStyle = `rgb(${255 * (1 - recommend)}, ${255 * recommend},  ${50 * recommend})`;

        // Draw rectangle according to recommendations
        ctx.fillRect(0, canvasHeight * (1 - recommend), canvasWidth, canvasHeight);
    }

    // Get recommendation objects
    let recommendObject1 = document.getElementById("recommend1");
    let recommendObject2 = document.getElementById("recommend2");
    let recommendObject3 = document.getElementById("recommend3");

    // When websocket sends signal update recommendations
    socket2.onmessage = function (e) {
        // Get all the data the server has sent
        let serverData = JSON.parse(e.data);

        // Convert server data to int
        let recommend1 = serverData["recommend1"];
        let recommend2 = serverData["recommend2"];
        let recommend3 = serverData["recommend3"];

        // Draw recommendations accordingly
        draw(recommendObject1, recommend1);
        draw(recommendObject2, recommend2);
        draw(recommendObject3, recommend3);
    }
}


// Function for level graph timeline
function menuTimeline1() {
    // Get the id name of the object that has been passed
    let id = this.id;

    // Send data back to server in JSON format
    socket3.send(JSON.stringify(id));
}


// Function for price graph timeline
function menuTimeline2() {
    // Get the id name of the object that has been passed
    let id = this.id;

    // Send data back to server in JSON format
    socket4.send(JSON.stringify(id));
}

