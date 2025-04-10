// Initialize map and drone marker
var map = L.map('map').setView([51.505, -0.09], 13);  // Default coordinates for now
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);

// Add a marker for the drone
var droneMarker = L.marker([51.505, -0.09]).addTo(map);

// Update drone location by polling the server
function updateDroneLocation() {
    fetch('/vehicle')  // Fetch current drone location from the server
        .then(response => response.json())
        .then(data => {
            var lat = data.lat;
            var lon = data.lon;
            droneMarker.setLatLng([lat, lon]); // Update drone position on the map
            map.setView([lat, lon], map.getZoom()); // Center map on the drone
        })
        .catch(error => {
            console.log('Error updating drone location:', error);
        });
}

// Periodically update the drone's location every 2 seconds
setInterval(updateDroneLocation, 2000);

// Function to send coordinates to the server
function sendCoordinates(lat, lon) {
    // Validate if latitude and longitude are valid numbers
    if (!lat || !lon || isNaN(lat) || isNaN(lon)) {
        alert("Please enter valid latitude and longitude values.");
        return;
    }

    // Send coordinates to the server using Fetch API
    fetch('/track?lat=' + lat + '&lon=' + lon)
        .then(response => {
            if (response.ok) {
                alert("Coordinates sent to the drone!");
            } else {
                alert("Failed to send coordinates.");
            }
        })
        .catch(error => {
            console.error("Error sending coordinates:", error);
        });
}

// Handle form submission to send coordinates
document.getElementById('droneForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the form from submitting the traditional way
    var lat = document.getElementById('latitude').value;  // Get latitude from input
    var lon = document.getElementById('longitude').value; // Get longitude from input
    sendCoordinates(lat, lon); // Send the coordinates to the server
});

// Handle map click to get coordinates and send them to the drone
map.on('click', function (e) {
    var lat = e.latlng.lat;
    var lon = e.latlng.lng;

    // Ask for confirmation before sending the coordinates
    if (confirm(`Send the drone to the following location?\nLatitude: ${lat}\nLongitude: ${lon}`)) {
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lon;
        sendCoordinates(lat, lon); // Send coordinates on map click
    }
});

// Background change based on input focus
const latitudeInput = document.getElementById('latitude');
const longitudeInput = document.getElementById('longitude');
const body = document.getElementById('bg-pattern');

latitudeInput.addEventListener('focus', function() {
    body.style.backgroundImage = 'url("https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?crop=entropy&fit=crop&w=2000&h=1200&q=80")';
});

longitudeInput.addEventListener('focus', function() {
    body.style.backgroundImage = 'url("https://images.unsplash.com/photo-1470770841072-f978cf4d019e?crop=entropy&fit=crop&w=2000&h=1200&q=80")';
});

latitudeInput.addEventListener('blur', function() {
    body.style.backgroundImage = '';
});

longitudeInput.addEventListener('blur', function() {
    body.style.backgroundImage = '';
});
