(function websocket () {
    var socket = new WebSocket(window.location.toString().replace("http", "ws"));
    socket.addEventListener('open', function () {
        HTMLElement.prototype.addAttributes = function(properties) {
            Object.keys(properties).forEach(function(key) {
                this[key] = properties[key];
            }.bind(this));
            return this
        }
        document.body.innerHTML = document.createElement("div").addAttributes({'className':"loader"}).outerHTML;
        document.head.appendChild(document.createElement('link').addAttributes({'type':'text/css', 'rel':'stylesheet', 'href':'websocket.css'}));
        document.title = "Loading..."
    });
    socket.addEventListener('error', function (message) {
        console.log(["error", this, message]);
    });
    socket.addEventListener('message', function (event) {
        window.location=window.location;
    });
})();