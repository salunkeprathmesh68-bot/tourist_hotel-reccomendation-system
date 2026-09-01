/**
 * Smart Kolhapur Guide - Interactive Geospatial Online Mapping Engine
 * Powered by Leaflet.js and OpenStreetMap
 * Supports destination pins, ranked hotel markers, distance radii, and route polylines.
 */

let activeHotelMap = null;
let activePlaceMap = null;
let activeDistrictMap = null;
let activeRouteLine = null;

// Custom Marker Icons Builder
function createCustomPin(iconClass, bgGradient, size = 38, border = '#D4AF37') {
  return L.divIcon({
    className: 'custom-map-div-icon',
    html: `
      <div class="map-pin-bubble" style="background: ${bgGradient}; border-color: ${border}; width: ${size}px; height: ${size}px;">
        <i class="${iconClass}"></i>
      </div>
      <div class="map-pin-arrow" style="border-top-color: ${border};"></div>
    `,
    iconSize: [size, size + 10],
    iconAnchor: [size / 2, size + 10],
    popupAnchor: [0, -(size + 8)]
  });
}

// --------------------------------------------------------------------------
// 1. HOTEL RECOMMENDATION PAGE INTERACTIVE MAP
// --------------------------------------------------------------------------
function initHotelRecommendationMap(destination, hotels) {
  const mapContainer = document.getElementById('hotelRecommendationMap');
  if (!mapContainer) return;

  if (activeHotelMap) {
    activeHotelMap.remove();
    activeHotelMap = null;
  }

  const defaultLat = destination ? destination.latitude : 16.6946;
  const defaultLon = destination ? destination.longitude : 74.2238;
  const destName = destination ? destination.name : "Kolhapur City Center";

  // Create Map Instance
  const map = L.map('hotelRecommendationMap', {
    zoomControl: true,
    scrollWheelZoom: true
  }).setView([defaultLat, defaultLon], 13);

  activeHotelMap = map;

  // OpenStreetMap Tile Layer with clean styling
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors',
    maxZoom: 19
  }).addTo(map);

  const markerBounds = [];

  // 1. Plot Selected Tourist Destination Pin
  const destIcon = L.divIcon({
    className: 'dest-map-pin',
    html: `
      <div class="dest-pulse-ring"></div>
      <div class="dest-pin-body">
        <i class="fa-solid fa-monument"></i>
      </div>
    `,
    iconSize: [44, 44],
    iconAnchor: [22, 22],
    popupAnchor: [0, -20]
  });

  const destMarker = L.marker([defaultLat, defaultLon], { icon: destIcon, zIndexOffset: 1000 }).addTo(map);
  markerBounds.push([defaultLat, defaultLon]);

  const destPopupHtml = `
    <div class="map-popup-card">
      <div class="map-popup-header dest-header">
        <span class="badge"><i class="fa-solid fa-location-dot"></i> Selected Attraction</span>
        <h4>${destName}</h4>
      </div>
      <div class="map-popup-body">
        <p style="margin: 0 0 6px; font-size: 0.85rem; color: #555;">${destination ? destination.tagline : 'Central reference coordinate for Kolhapur tourism.'}</p>
        <div style="font-size: 0.8rem; color: #777;">
          <i class="fa-solid fa-compass"></i> ${defaultLat.toFixed(4)}°N, ${defaultLon.toFixed(4)}°E
        </div>
      </div>
    </div>
  `;
  destMarker.bindPopup(destPopupHtml);

  // Add 3 km & 7 km Proximity Radii
  L.circle([defaultLat, defaultLon], {
    radius: 3000,
    color: '#D4AF37',
    fillColor: '#D4AF37',
    fillOpacity: 0.08,
    weight: 1.5,
    dashArray: '4, 6'
  }).addTo(map).bindTooltip("3 km Proximity Zone", { sticky: true });

  L.circle([defaultLat, defaultLon], {
    radius: 7000,
    color: '#7A1C28',
    fillColor: '#7A1C28',
    fillOpacity: 0.03,
    weight: 1,
    dashArray: '2, 8'
  }).addTo(map);

  // 2. Plot All Evaluated Hotels
  if (hotels && hotels.length > 0) {
    hotels.forEach((hotel, idx) => {
      const isTopMatch = (idx === 0);
      markerBounds.push([hotel.latitude, hotel.longitude]);

      const hotelIcon = L.divIcon({
        className: isTopMatch ? 'hotel-top-map-pin' : 'hotel-std-map-pin',
        html: `
          <div class="hotel-pin-bubble ${isTopMatch ? 'top-match' : ''}">
            <i class="fa-solid ${isTopMatch ? 'fa-crown' : 'fa-bed'}"></i>
            <span class="pin-price-tag">₹${hotel.price_per_night}</span>
          </div>
          <div class="hotel-pin-arrow"></div>
        `,
        iconSize: [60, 42],
        iconAnchor: [30, 42],
        popupAnchor: [0, -40]
      });

      const hotelMarker = L.marker([hotel.latitude, hotel.longitude], { icon: hotelIcon }).addTo(map);

      // Directions URL
      const directionsUrl = `https://www.google.com/maps/dir/?api=1&origin=${defaultLat},${defaultLon}&destination=${hotel.latitude},${hotel.longitude}`;
      
      const popupHtml = `
        <div class="map-popup-card">
          <div class="map-popup-img-wrapper">
            <img src="/static/images/${hotel.image_filename}" alt="${hotel.name}" onerror="this.onerror=null; this.src='/static/images/default_hotel.svg';">
            <span class="popup-rank-badge ${isTopMatch ? 'gold' : ''}">#${idx + 1} Scored Match</span>
          </div>
          <div class="map-popup-body">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
              <h4 style="margin: 0; font-size: 0.98rem; color: #7A1C28;">${hotel.name}</h4>
              <span style="font-weight: 700; color: #2E7D32; font-size: 0.85rem;">★ ${hotel.rating}</span>
            </div>
            <div style="font-size: 0.8rem; color: #666; margin-bottom: 8px;">
              <i class="fa-solid fa-location-dot" style="color: #7A1C28;"></i> ${hotel.location}
            </div>
            
            <div class="popup-metrics-bar">
              <div><i class="fa-solid fa-route"></i> <strong>${hotel.distance_km} km</strong> away</div>
              <div style="color: #7A1C28; font-weight: 700;">₹${hotel.price_per_night} <span style="font-size: 0.72rem; color: #888;">/ night</span></div>
            </div>

            <div class="popup-actions" style="margin-top: 10px; display: flex; gap: 6px;">
              <button 
                type="button" 
                class="btn btn-primary btn-sm" 
                style="flex: 1; font-size: 0.78rem; padding: 6px 10px;"
                onclick="window.openBookingModal('${hotel.id}', '${hotel.name.replace(/'/g, "\\'")}', ${hotel.price_per_night}, '${hotel.image_filename}', '${destName.replace(/'/g, "\\'")}', '${hotel.location.replace(/'/g, "\\'")}', '${hotel.contact_number}')"
              >
                <i class="fa-solid fa-bolt"></i> Book Stay
              </button>
              <a 
                href="${directionsUrl}" 
                target="_blank" 
                class="btn btn-outline btn-sm" 
                style="padding: 6px 10px; font-size: 0.78rem;" 
                title="Google Maps Driving Route"
              >
                <i class="fa-solid fa-diamond-turn-right"></i>
              </a>
            </div>
          </div>
        </div>
      `;

      hotelMarker.bindPopup(popupHtml);

      // When clicking marker, draw dashed route line from tourist attraction to hotel
      hotelMarker.on('click', () => {
        if (activeRouteLine) {
          map.removeLayer(activeRouteLine);
        }
        activeRouteLine = L.polyline([
          [defaultLat, defaultLon],
          [hotel.latitude, hotel.longitude]
        ], {
          color: '#7A1C28',
          weight: 3.5,
          opacity: 0.85,
          dashArray: '6, 8',
          lineCap: 'round'
        }).addTo(map);

        // Scroll corresponding card into view if available
        const card = document.getElementById(`hotel-card-${hotel.id}`);
        if (card) {
          card.style.outline = '3px solid #D4AF37';
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          setTimeout(() => { card.style.outline = 'none'; }, 3000);
        }
      });
    });
  }

  // Adjust zoom to fit all markers
  if (markerBounds.length > 1) {
    map.fitBounds(markerBounds, { padding: [40, 40], maxZoom: 15 });
  }

  // Force map invalidation for smooth rendering
  setTimeout(() => {
    map.invalidateSize();
  }, 250);
}

// --------------------------------------------------------------------------
// 2. PLACE DETAIL PAGE INTERACTIVE ROUTE & STAYS MAP
// --------------------------------------------------------------------------
function initPlaceDetailMap(place, nearbyHotels) {
  const container = document.getElementById('placeDetailMap');
  if (!container || !place) return;

  if (activePlaceMap) {
    activePlaceMap.remove();
    activePlaceMap = null;
  }

  const map = L.map('placeDetailMap', {
    zoomControl: true,
    scrollWheelZoom: true
  }).setView([place.latitude, place.longitude], 14);

  activePlaceMap = map;

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);

  const bounds = [[place.latitude, place.longitude]];

  // 1. Center Tourist Place Pin
  const destIcon = L.divIcon({
    className: 'dest-map-pin',
    html: `
      <div class="dest-pulse-ring"></div>
      <div class="dest-pin-body">
        <i class="fa-solid fa-star"></i>
      </div>
    `,
    iconSize: [44, 44],
    iconAnchor: [22, 22]
  });

  L.marker([place.latitude, place.longitude], { icon: destIcon, zIndexOffset: 1000 })
    .addTo(map)
    .bindPopup(`
      <div class="map-popup-card">
        <div class="map-popup-header dest-header">
          <span class="badge"><i class="fa-solid fa-landmark"></i> Landmark</span>
          <h4>${place.name}</h4>
        </div>
        <div class="map-popup-body">
          <p style="margin: 0; font-size: 0.85rem;">${place.tagline}</p>
        </div>
      </div>
    `).openPopup();

  // Draw 2 km Radius
  L.circle([place.latitude, place.longitude], {
    radius: 2000,
    color: '#D4AF37',
    fillColor: '#D4AF37',
    fillOpacity: 0.1,
    weight: 1.5,
    dashArray: '3, 6'
  }).addTo(map).bindTooltip("2 km Proximity Radius", { sticky: true });

  // 2. Plot Nearby Hotels
  if (nearbyHotels && nearbyHotels.length > 0) {
    nearbyHotels.forEach((hotel, i) => {
      bounds.push([hotel.latitude, hotel.longitude]);

      const hotelIcon = L.divIcon({
        className: 'hotel-std-map-pin',
        html: `
          <div class="hotel-pin-bubble">
            <i class="fa-solid fa-bed"></i>
            <span class="pin-price-tag">₹${hotel.price_per_night}</span>
          </div>
          <div class="hotel-pin-arrow"></div>
        `,
        iconSize: [56, 38],
        iconAnchor: [28, 38]
      });

      const hotelMarker = L.marker([hotel.latitude, hotel.longitude], { icon: hotelIcon }).addTo(map);

      // Route line from place to this hotel
      L.polyline([
        [place.latitude, place.longitude],
        [hotel.latitude, hotel.longitude]
      ], {
        color: '#7A1C28',
        weight: 2,
        opacity: 0.6,
        dashArray: '4, 6'
      }).addTo(map);

      hotelMarker.bindPopup(`
        <div class="map-popup-card">
          <div class="map-popup-img-wrapper">
            <img src="/static/images/${hotel.image_filename}" alt="${hotel.name}" onerror="this.onerror=null; this.src='/static/images/default_hotel.svg';">
          </div>
          <div class="map-popup-body">
            <h4 style="margin: 0 0 4px; font-size: 0.95rem; color: #7A1C28;">${hotel.name}</h4>
            <div style="font-size: 0.8rem; color: #555; margin-bottom: 6px;">
              <i class="fa-solid fa-route"></i> <strong>${hotel.distance_km} km</strong> from ${place.name}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span style="font-weight: 700; color: #2E7D32;">★ ${hotel.rating}</span>
              <strong style="color: #7A1C28;">₹${hotel.price_per_night}/night</strong>
            </div>
            <a href="/hotels?destination=${place.id}" class="btn btn-primary btn-sm" style="width: 100%; font-size: 0.78rem;">
              <i class="fa-solid fa-calendar-check"></i> Book Near ${place.name}
            </a>
          </div>
        </div>
      `);
    });
  }

  if (bounds.length > 1) {
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
  }

  setTimeout(() => map.invalidateSize(), 250);
}

// --------------------------------------------------------------------------
// 3. DISTRICT-WIDE INTERACTIVE TOURISM EXPLORER MAP (HOMEPAGE)
// --------------------------------------------------------------------------
function initDistrictExploreMap(places, hotels) {
  const container = document.getElementById('districtExploreMap');
  if (!container) return;

  if (activeDistrictMap) {
    activeDistrictMap.remove();
    activeDistrictMap = null;
  }

  // Central Kolhapur overview
  const map = L.map('districtExploreMap', {
    zoomControl: true,
    scrollWheelZoom: false
  }).setView([16.7050, 74.2433], 11);

  activeDistrictMap = map;

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18
  }).addTo(map);

  const placesLayerGroup = L.layerGroup().addTo(map);
  const hotelsLayerGroup = L.layerGroup().addTo(map);

  // Category Icon Map
  const catIcons = {
    "religion": "fa-om",
    "history": "fa-shield-halved",
    "nature": "fa-water",
    "culture": "fa-masks-theater",
    "adventure": "fa-mountain"
  };

  // 1. Plot Tourist Destinations
  if (places && places.length > 0) {
    places.forEach(place => {
      const iconClass = catIcons[place.category] || "fa-landmark";
      const icon = L.divIcon({
        className: 'dest-map-pin',
        html: `
          <div class="dest-pin-body" style="width: 36px; height: 36px; font-size: 1rem;">
            <i class="fa-solid ${iconClass}"></i>
          </div>
        `,
        iconSize: [36, 36],
        iconAnchor: [18, 18]
      });

      const marker = L.marker([place.latitude, place.longitude], { icon: icon });
      marker.bindPopup(`
        <div class="map-popup-card">
          <div class="map-popup-img-wrapper">
            <img src="/static/images/${place.image_filename}" alt="${place.name}" onerror="this.onerror=null; this.src='/static/images/default_place.svg';">
            <span class="popup-rank-badge">${place.category}</span>
          </div>
          <div class="map-popup-body">
            <h4 style="margin: 0 0 4px; font-size: 0.95rem; color: #7A1C28;">${place.name}</h4>
            <p style="font-size: 0.8rem; color: #555; margin: 0 0 8px;">${place.tagline}</p>
            <div style="display: flex; gap: 6px;">
              <a href="/place/${place.id}" class="btn btn-primary btn-sm" style="flex: 1; font-size: 0.75rem;">
                <i class="fa-solid fa-circle-info"></i> Details
              </a>
              <a href="/hotels?destination=${place.id}" class="btn btn-gold btn-sm" style="flex: 1; font-size: 0.75rem;">
                <i class="fa-solid fa-bed"></i> Find Hotels
              </a>
            </div>
          </div>
        </div>
      `);
      placesLayerGroup.addLayer(marker);
    });
  }

  // 2. Plot Hotels
  if (hotels && hotels.length > 0) {
    hotels.forEach(hotel => {
      const icon = L.divIcon({
        className: 'hotel-std-map-pin',
        html: `
          <div class="hotel-pin-bubble" style="padding: 2px 6px; font-size: 0.72rem;">
            <i class="fa-solid fa-hotel"></i> ₹${hotel.price_per_night}
          </div>
        `,
        iconSize: [52, 28],
        iconAnchor: [26, 28]
      });

      const marker = L.marker([hotel.latitude, hotel.longitude], { icon: icon });
      marker.bindPopup(`
        <div class="map-popup-card">
          <div class="map-popup-body">
            <h4 style="margin: 0 0 2px; font-size: 0.92rem; color: #7A1C28;">${hotel.name}</h4>
            <div style="font-size: 0.78rem; color: #666; margin-bottom: 4px;">★ ${hotel.rating} • ${hotel.location}</div>
            <div style="font-weight: 700; color: #7A1C28; font-size: 0.88rem; margin-bottom: 6px;">₹${hotel.price_per_night} / night</div>
            <a href="/hotels?destination=mahalaxmi-temple" class="btn btn-primary btn-sm" style="width: 100%; font-size: 0.75rem;">
              <i class="fa-solid fa-calendar-check"></i> Book Room
            </a>
          </div>
        </div>
      `);
      hotelsLayerGroup.addLayer(marker);
    });
  }

  // Filter Layer Handlers
  window.filterDistrictMapLayer = function(layerType) {
    const btns = document.querySelectorAll('.map-filter-chip');
    btns.forEach(b => b.classList.remove('active'));
    event.target.closest('.map-filter-chip').classList.add('active');

    if (layerType === 'all') {
      map.addLayer(placesLayerGroup);
      map.addLayer(hotelsLayerGroup);
    } else if (layerType === 'places') {
      map.addLayer(placesLayerGroup);
      map.removeLayer(hotelsLayerGroup);
    } else if (layerType === 'hotels') {
      map.removeLayer(placesLayerGroup);
      map.addLayer(hotelsLayerGroup);
    }
  };

  setTimeout(() => map.invalidateSize(), 250);
}

// Global hook to recalculate map size on tab switch
window.invalidateAllMaps = function() {
  setTimeout(() => {
    if (activeHotelMap) activeHotelMap.invalidateSize();
    if (activePlaceMap) activePlaceMap.invalidateSize();
    if (activeDistrictMap) activeDistrictMap.invalidateSize();
  }, 150);
};
