document.addEventListener('DOMContentLoaded', function() {
  // Initialize the map without auto-zoom adjustments
  const map = L.map('map').setView([12.971,77.5946], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  // Global variables
  let start = null, end = null;
  let obstacles = new Set();  // Obstacles stored as "lat,lng" with fixed 6 decimals
  let obstacleMarkers = [];   // Array to store obstacle circle markers
  let currentPath = [];
  let lastValidPath = null;   // Stores last valid non-trivial path
  // Options: 'astar' or 'dijkstra'
  let currentAlgorithm = 'astar'; // default
  const maxIterations = 1000;     // Iteration limit
  const step = 0.005;             // Grid step size (in degrees)
  let animationMarker = null;
  let animationInterval = null;
  let pathLine = null;

  // Obstacle penalty configuration
  let obstacleWeight = 100;       // Base penalty weight
  const baseThreshold = step * 2; // Base threshold for obstacle proximity
  const minObstacleWeight = 5;    // Minimum penalty weight to try

  // UI elements
  const pathInfoDiv = document.getElementById('pathInfo');
  const algoSelect = document.getElementById('algoSelect');
  const clearObstaclesBtn = document.getElementById('clearObstaclesBtn');
  const resetBtn = document.getElementById('resetBtn');

  // Create routing control with auto-fit disabled
  const routeControl = L.Routing.control({
    waypoints: [],
    routeWhileDragging: true,
    createMarker: () => null,
    fitSelectedRoutes: false
  }).addTo(map);

  // Update algorithm selection from dropdown
  algoSelect.addEventListener('change', function(e) {
    currentAlgorithm = e.target.value;
    console.log('Algorithm selected:', currentAlgorithm);
    if (start && end) recalculatePath();
  });

  // Euclidean distance heuristic (for grid cost computations)
  function heuristic(a, b) {
    return Math.sqrt(Math.pow(a.lat - b.lat, 2) + Math.pow(a.lng - b.lng, 2));
  }

  // Haversine distance (in km) between two latlng points
  function haversineDistance(a, b) {
    const R = 6371;
    const dLat = (b.lat - a.lat) * Math.PI / 180;
    const dLng = (b.lng - a.lng) * Math.PI / 180;
    const lat1 = a.lat * Math.PI / 180;
    const lat2 = b.lat * Math.PI / 180;
    const sinDLat = Math.sin(dLat / 2);
    const sinDLng = Math.sin(dLng / 2);
    const aHarv = sinDLat * sinDLat + Math.cos(lat1) * Math.cos(lat2) * sinDLng * sinDLng;
    const c = 2 * Math.atan2(Math.sqrt(aHarv), Math.sqrt(1 - aHarv));
    return R * c;
  }

  // Compute extra cost for nodes near obstacles
  function obstacleCost(node, threshold = baseThreshold, weight = obstacleWeight) {
    let cost = 0;
    obstacles.forEach(function(key) {
      let parts = key.split(',');
      let obs = { lat: parseFloat(parts[0]), lng: parseFloat(parts[1]) };
      let d = heuristic(node, obs);
      if (d < threshold) {
        cost += weight * (1 - d / threshold);
      }
    });
    return cost;
  }

  // Modified A* Algorithm Implementation with improved cycle avoidance.
  function aStarAlgorithm(s, e) {
    console.log('Running A* from', s, 'to', e);
    let openSet = [{ node: s, g: 0, f: heuristic(s, e), path: [s] }];
    let bestG = {};  // Best cost found for each node key.
    bestG[s.lat.toFixed(6) + ',' + s.lng.toFixed(6)] = 0;
    let iterations = 0;

    while (openSet.length > 0 && iterations < maxIterations) {
      iterations++;
      openSet.sort((a, b) => a.f - b.f);
      let current = openSet.shift();

      if (heuristic(current.node, e) < step) {
        console.log('A* completed in', iterations, 'iterations');
        return current.path.concat([e]);
      }

      let neighbors = getNeighbors(current.node);
      for (let neighbor of neighbors) {
        let nKey = neighbor.lat.toFixed(6) + ',' + neighbor.lng.toFixed(6);
        // Skip if neighbor is an obstacle.
        if (obstacles.has(nKey)) continue;
        // Avoid cycles by checking if neighbor is already in the current path.
        if (current.path.some(n => n.lat.toFixed(6) === neighbor.lat.toFixed(6) && n.lng.toFixed(6) === neighbor.lng.toFixed(6))) continue;

        let moveCost = heuristic(current.node, neighbor);
        let penalty = obstacleCost(neighbor);
        let newG = current.g + moveCost + penalty;

        // If we have already reached this node with a lower cost, skip.
        if (bestG[nKey] !== undefined && newG >= bestG[nKey]) continue;

        bestG[nKey] = newG;
        let newF = newG + heuristic(neighbor, e);
        openSet.push({ node: neighbor, g: newG, f: newF, path: [...current.path, neighbor] });
      }
    }
    console.warn('A* reached maximum iterations.');
    return [s];
  }

  // Modified Dijkstra Algorithm Implementation with improved cycle avoidance.
  function dijkstraAlgorithm(s, e) {
    console.log('Running Dijkstra from', s, 'to', e);
    let openSet = [{ node: s, g: 0, path: [s] }];
    let bestG = {};
    bestG[s.lat.toFixed(6) + ',' + s.lng.toFixed(6)] = 0;
    let iterations = 0;

    while (openSet.length > 0 && iterations < maxIterations) {
      iterations++;
      openSet.sort((a, b) => a.g - b.g);
      let current = openSet.shift();

      if (heuristic(current.node, e) < step) {
        console.log('Dijkstra completed in', iterations, 'iterations');
        return current.path.concat([e]);
      }

      let neighbors = getNeighbors(current.node);
      for (let neighbor of neighbors) {
        let nKey = neighbor.lat.toFixed(6) + ',' + neighbor.lng.toFixed(6);
        if (obstacles.has(nKey)) continue;
        if (current.path.some(n => n.lat.toFixed(6) === neighbor.lat.toFixed(6) && n.lng.toFixed(6) === neighbor.lng.toFixed(6))) continue;

        let moveCost = heuristic(current.node, neighbor);
        let penalty = obstacleCost(neighbor);
        let newG = current.g + moveCost + penalty;
        if (bestG[nKey] !== undefined && newG >= bestG[nKey]) continue;
        bestG[nKey] = newG;

        openSet.push({ node: neighbor, g: newG, path: [...current.path, neighbor] });
      }
    }
    console.warn('Dijkstra reached maximum iterations.');
    return [s];
  }

  // Return neighbors (includes diagonals)
  function getNeighbors(node) {
    return [
      { lat: node.lat + step, lng: node.lng },
      { lat: node.lat - step, lng: node.lng },
      { lat: node.lat, lng: node.lng + step },
      { lat: node.lat, lng: node.lng - step },
      { lat: node.lat + step, lng: node.lng + step },
      { lat: node.lat + step, lng: node.lng - step },
      { lat: node.lat - step, lng: node.lng + step },
      { lat: node.lat - step, lng: node.lng - step }
    ];
  }

  // Recalculate path starting from a given starting point.
  function recalculatePath(newStart) {
    let currentStart = newStart || start;
    if (!currentStart || !end) return;
    let path = [];

    if (currentAlgorithm === 'astar') {
      path = aStarAlgorithm(currentStart, end);
    } else if (currentAlgorithm === 'dijkstra') {
      path = dijkstraAlgorithm(currentStart, end);
    }
    
    // Iteratively reduce obstacle penalty weight if path is trivial.
    let fallbackWeight = obstacleWeight;
    while (path.length === 1 && fallbackWeight > minObstacleWeight) {
      console.warn('No valid path found. Lowering obstacle penalty weight and retrying.');
      fallbackWeight /= 2;
      let originalWeight = obstacleWeight;
      obstacleWeight = fallbackWeight;
      if (currentAlgorithm === 'astar') {
        path = aStarAlgorithm(currentStart, end);
      } else {
        path = dijkstraAlgorithm(currentStart, end);
      }
      obstacleWeight = originalWeight;
    }
    
    if (path.length === 1 && lastValidPath && lastValidPath.length > 1) {
      console.warn('Fallback did not yield a valid path. Reverting to last valid path.');
      path = lastValidPath;
    }
    if (path.length > 1) lastValidPath = path;
    visualizePath(path);
  }

  // Visualize the computed path: update routing control, draw polyline, animate marker, display path info.
  function visualizePath(path) {
    currentPath = path;
    const latLngPath = path.map(p => L.latLng(p.lat, p.lng));
    routeControl.setWaypoints(latLngPath);
    if (pathLine) map.removeLayer(pathLine);
    pathLine = L.polyline(latLngPath, { color: 'blue', weight: 4 }).addTo(map);
    displayPathInfo(path);
    animatePath(path);
  }

  // Animate a marker along the path.
  function animatePath(path) {
    if (animationMarker) map.removeLayer(animationMarker);
    if (animationInterval) clearInterval(animationInterval);
    let index = 0;
    animationMarker = L.marker(path[index]).addTo(map);
    animationInterval = setInterval(() => {
      if (index < path.length - 1) {
        index++;
        animationMarker.setLatLng(path[index]);
      } else {
        clearInterval(animationInterval);
      }
    }, 500);
  }

  // Display total path length in kilometers using haversineDistance.
  function displayPathInfo(path) {
    let totalDistance = 0;
    for (let i = 0; i < path.length - 1; i++) {
      totalDistance += haversineDistance(path[i], path[i + 1]);
    }
    pathInfoDiv.innerText = 'Path Length: ' + totalDistance.toFixed(2) + ' km';
  }

  // When an obstacle is added, recalculate the path starting from the original start.
  function addObstacle(lat, lng) {
    let key = lat.toFixed(6) + ',' + lng.toFixed(6);
    obstacles.add(key);
    const circle = L.circle([lat, lng], { color: 'red', radius: 50 }).addTo(map);
    obstacleMarkers.push(circle);
    recalculatePath(start);
  }

  // Clear obstacles, remove their circle markers, and recalculate the path.
  function clearObstacles() {
    obstacles.clear();
    obstacleMarkers.forEach(marker => map.removeLayer(marker));
    obstacleMarkers = [];
    recalculatePath(start);
  }

  // Reset the entire map.
  function resetMap() {
    start = null;
    end = null;
    currentPath = [];
    lastValidPath = null;
    obstacles.clear();
    obstacleMarkers.forEach(marker => map.removeLayer(marker));
    obstacleMarkers = [];
    pathInfoDiv.innerText = 'Path Length: 0 km';
    routeControl.setWaypoints([]);
    if (animationMarker) { map.removeLayer(animationMarker); animationMarker = null; }
    if (animationInterval) { clearInterval(animationInterval); animationInterval = null; }
    if (pathLine) { map.removeLayer(pathLine); pathLine = null; }
    map.eachLayer(function(layer) {
      if ((layer instanceof L.Marker || layer instanceof L.Circle) && !layer._url) {
        map.removeLayer(layer);
      }
    });
  }

  // Button event listeners.
  clearObstaclesBtn.addEventListener('click', clearObstacles);
  resetBtn.addEventListener('click', resetMap);

  // Map click handling:
  // 1st click: set start, 2nd click: set destination, later clicks: add obstacles.
  map.on('click', function(e) {
    if (!start) {
      start = e.latlng;
      L.marker(start).addTo(map).bindPopup('Start').openPopup();
    } else if (!end) {
      end = e.latlng;
      L.marker(end).addTo(map).bindPopup('End').openPopup();
      recalculatePath(start);
    } else {
      addObstacle(e.latlng.lat, e.latlng.lng);
    }
  });
});
