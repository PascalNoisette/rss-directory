(function websocket () {
    var socket = new WebSocket(window.location.toString().replace("http", "ws"));
    socket.addEventListener('error', function (message) {
        console.log(["error", this, message]);
    });
    socket.addEventListener('message', function (event) {
        window.location=window.location;
    });
})();