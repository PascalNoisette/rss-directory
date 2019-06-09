(function websocket () {
    var socket = new WebSocket(window.location.toString().replace("http", "ws"));
    socket.addEventListener('error', function (message) {
        console.log(["error", this, message]);
    });
    socket.addEventListener('open', function (event) {
        console.log(["open", this, event]);
        socket.send("Please let me know when " + window.location + " is ready");
    });
    socket.addEventListener('message', function (event) {
        console.log(event.data)
        //window.location=window.location;
    });
})();