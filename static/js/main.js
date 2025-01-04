document.addEventListener('DOMContentLoaded', function() {
    console.log("main.js is loaded and running.");

    // Initialize the map
    var map = L.map('map').setView([17.3600, 78.4800], 13);
    console.log("Map initialized.");

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(map);
    console.log("Tile layer added to map.");

    // Custom icon for markers
    const customIcon = (color) => L.icon({
        iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-shadow.png',
        shadowSize: [41, 41]
    });

    // Route button click event listener
    document.getElementById('route-btn').addEventListener('click', function(event) {
        event.preventDefault();
        console.log("Route button clicked.");

        // Get user input
        var origin = document.getElementById('origin').value.split(',');
        var destination = document.getElementById('destination').value.split(',');

        var startLat = parseFloat(origin[0].trim());
        var startLon = parseFloat(origin[1].trim());
        var endLat = parseFloat(destination[0].trim());
        var endLon = parseFloat(destination[1].trim());
        console.log(`User input received: startLat=${startLat}, startLon=${startLon}, endLat=${endLat}, endLon=${endLon}`);

        // Show loading message
        var loadingMessage = document.createElement('div');
        loadingMessage.id = 'loading';
        loadingMessage.innerHTML = 'Calculating route, please wait...';
        document.body.appendChild(loadingMessage);

        // Fetch route from the backend
        fetch(`/predict?startLat=${startLat}&startLon=${startLon}&endLat=${endLat}&endLon=${endLon}`)
            .then(response => response.json())
            .then(data => {
                console.log("Data fetched from backend:", data);

                // Remove loading message
                document.body.removeChild(loadingMessage);

                if (data.error) {
                    alert(data.error);
                    return;
                }

                // Clear existing markers and routes
                map.eachLayer(function (layer) {
                    if (layer instanceof L.Marker || layer instanceof L.Polyline) {
                        map.removeLayer(layer);
                    }
                });

                // Add markers for each coordinate in the route
                data.route.forEach((coord, index) => {
                    var markerIcon = (index === 0 || index === data.route.length - 1) ? customIcon('red') : customIcon('blue');
                    L.marker(coord, { icon: markerIcon }).addTo(map);
                });

                // Add a polyline to connect the route
                var polyline = L.polyline(data.route, {color: 'blue'}).addTo(map);

                // Zoom the map to fit the route
                map.fitBounds(polyline.getBounds());

                // Display distance and time
                document.getElementById('distance').textContent = data.distance.toFixed(2);
                document.getElementById('time').textContent = data.time.toFixed(2);

                // Ensure the route details box is visible
                document.getElementById('route-details').style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching route:', error);
                // Remove loading message
                document.body.removeChild(loadingMessage);
                alert('Failed to calculate the route. Please try again.');
            });
    });

    // Function to reset the map
    window.resetMap = function() {
        console.log("Reset button clicked.");

        // Clear existing markers and routes
        map.eachLayer(function (layer) {
            if (layer instanceof L.Marker || layer instanceof L.Polyline) {
                map.removeLayer(layer);
            }
        });

        // Reset distance and time display
        document.getElementById('distance').textContent = '--';
        document.getElementById('time').textContent = '--';
    }

    // Download button click event listener
    document.getElementById('download-btn').addEventListener('click', function() {
        leafletImage(map, function(err, canvas) {
            var img = document.createElement('a');
            img.download = 'map.png';
            img.href = canvas.toDataURL();
            img.click();
        });
    });
});
