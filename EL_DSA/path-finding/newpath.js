// Initialize map
const map = L.map('map').setView([51.505, -0.09], 13); // Initial map view

// Add tile layer to map (OpenStreetMap tiles)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Store the current start and end points as global variables
let start = null;
let end = null;

// Store the waypoints for routing (start and end points)
let waypoints = [];

// Create a routing control for pathfinding visualization
const routeControl = L.Routing.control({
  waypoints: waypoints,
  routeWhileDragging: true,
  createMarker: function() { return null; }, // Hide route markers
}).addTo(map);

// Store obstacles as array of lat/lng pairs
let obstacles = [];

// Helper function: calculate distance from point p to line segment (v, w)
function pointLineDistance(p, v, w) {
  const A = p.lat - v.lat;
  const B = p.lng - v.lng;
  const C = w.lat - v.lat;
  const D = w.lng - v.lng;
  const dot = A * C + B * D;
  const len_sq = C * C + D * D;
  let param = -1;
  if (len_sq !== 0) { // in case of 0 length line
    param = dot / len_sq;
  }
  let xx, yy;
  if (param < 0) {
    xx = v.lat;
    yy = v.lng;
  } else if (param > 1) {
    xx = w.lat;
    yy = w.lng;
  } else {
    xx = v.lat + param * C;
    yy = v.lng + param * D;
  }
  const dx = p.lat - xx;
  const dy = p.lng - yy;
  return Math.sqrt(dx * dx + dy * dy);
}

// Modified A* algorithm demonstration with path blockage heuristic
function aStarAlgorithm(start, end) {
  // If there are no obstacles, simply return the direct path.
  if (obstacles.length === 0) {
    return [start, end];
  }
  
  // Threshold for blockage detection (adjust this value based on map scale)
  const blockageThreshold = 0.001; // roughly corresponds to ~100m depending on map scale
  
  // Check each obstacle to see if it is near the straight line between start and end
  let blockDetected = false;
  let blockingObstacle = null;
  for (let i = 0; i < obstacles.length; i++) {
    // Convert obstacle array to a latLng-like object
    const obs = { lat: obstacles[i][0], lng: obstacles[i][1] };
    const dist = pointLineDistance(obs, start, end);
    if (dist < blockageThreshold) {
      blockDetected = true;
      blockingObstacle = obs;
      break;
    }
  }
  
  // Build path: if a block is detected, add a detour waypoint to bypass the obstacle.
  let path = [];
  path.push(start);
  if (blockDetected && blockingObstacle) {
    // Calculate a detour point by shifting the blocking obstacle point perpendicular to the line
    const dx = end.lng - start.lng;
    const dy = end.lat - start.lat;
    const length = Math.sqrt(dx * dx + dy * dy);
    const offset = blockageThreshold * 2; // adjust how far to detour
    // Perpendicular vector (normalized)
    const perpLat = -dy / length;
    const perpLng = dx / length;
    const detourPoint = {
      lat: blockingObstacle.lat + perpLat * offset,
      lng: blockingObstacle.lng + perpLng * offset,
    };
    path.push(detourPoint);
  }
  path.push(end);
  
  return path;
}

// Original Dijkstra (simplified for demonstration)
function dijkstraAlgorithm(start, end) {
  return [start, end]; // Simplified version, replace with an actual Dijkstra implementation if needed
}

// Visualize the path on the map and animate the marker's movement
function visualizePath(path) {
  routeControl.setWaypoints(path); // Set the new waypoints for the route
  animatePath(path);  // Animate the marker along the path
}

// Function to animate path traversal with a moving marker
function animatePath(path) {
  let i = 0;
  const marker = L.marker(path[i]).addTo(map);
  const interval = setInterval(function() {
    if (i < path.length - 1) {
      marker.setLatLng(path[++i]);  // Move marker to next point in the path
    } else {
      clearInterval(interval);  // Stop the animation when the path ends
    }
  }, 500);  // Adjust speed (500ms between steps)
}

// Recalculate the path if obstacles change the available route
function recalculatePath() {
  // Use the chosen algorithm (Dijkstra or A*)
  const path = aStarAlgorithm(start, end);  // Or use dijkstraAlgorithm(start, end)
  visualizePath(path);  // Visualize the new path
}

// Add an obstacle to the map (for demo purposes)
function addObstacle(lat, lng) {
  obstacles.push([lat, lng]); // Add obstacle to the array

  // Visualize the obstacle as a red circle
  L.circle([lat, lng], {
    color: 'red',
    radius: 50,
  }).addTo(map);

  // Recalculate the path after adding the obstacle
  recalculatePath();
}

// Allow the user to click on the map to set the start or end point dynamically
let sourceSet = false;
let destinationSet = false;

// Button click to set source
document.getElementById('setSourceBtn').addEventListener('click', () => {
  map.once('click', function(e) {
    start = e.latlng;
    sourceSet = true;
    L.marker(start).addTo(map).bindPopup("Source").openPopup();
    if (sourceSet && destinationSet) {
      recalculatePath();  // Recalculate path when both source and destination are set
    }
    enableStartTraversal();
  });
});

// Button click to set destination
document.getElementById('setDestinationBtn').addEventListener('click', () => {
  map.once('click', function(e) {
    // Remove the old destination marker if it exists
    if (end) {
      map.eachLayer(function(layer) {
        if (layer instanceof L.Marker && layer.getLatLng().equals(end)) {
          map.removeLayer(layer); // Remove the old destination marker
        }
      });
    }

    // Set the new destination and add a marker
    end = e.latlng;
    destinationSet = true;
    L.marker(end).addTo(map).bindPopup("New Destination").openPopup();
    if (sourceSet && destinationSet) {
      recalculatePath();  // Recalculate path when both source and destination are set
    }
    enableStartTraversal();
  });
});

// Function to enable the "Start Traversal" button
function enableStartTraversal() {
  if (sourceSet && destinationSet) {
    document.getElementById('startTraversalBtn').disabled = false;
  }
}

// Button click to start traversal
document.getElementById('startTraversalBtn').addEventListener('click', () => {
  if (sourceSet && destinationSet) {
    const path = aStarAlgorithm(start, end);
    visualizePath(path);  // Visualize the path and start traversal
  }
});

// Handle destination change dynamically
map.on('click', function(e) {
  if (destinationSet) {
    // Remove the old destination marker if it exists
    map.eachLayer(function(layer) {
      if (layer instanceof L.Marker && layer.getLatLng().equals(end)) {
        map.removeLayer(layer); // Remove the old destination marker
      }
    });

    // Update the destination and add a new marker
    end = e.latlng;
    L.marker(end).addTo(map).bindPopup("New Destination").openPopup();
    recalculatePath(); // Recalculate the path with the updated destination
  }
});
