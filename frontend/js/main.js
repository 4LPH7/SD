// --- CONFIGURATION ---
Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYWE1OWMzOC0zNWIwLTQxZWYtYTIxMy1kZjA1NDU5YjFlY2EiLCJpZCI6NDU0Mywic2NvcGVzIjpbImFzbCIsImFzciIsImFzdyIsImdjIl0sImlhdCI6MTU0MDQ4ODYyOX0.82r2mR038G24d3Y3-1t5Hwrx2Kb2fg5Ay9hF7cR4yVs';
const API_URL = 'http://127.0.0.1:8000/api/debris/positions';
const UPDATE_INTERVAL_SECONDS = 10;

// --- UI ELEMENTS ---
const loadingIndicator = document.getElementById('loadingIndicator');
const tooltipElement = document.getElementById('tooltip');
const infoCard = document.getElementById('infoCard');
const infoName = document.getElementById('infoName');
const infoNorad = document.getElementById('infoNorad');
const infoSpeed = document.getElementById('infoSpeed');
const infoAltitude = document.getElementById('infoAltitude');
const closeButton = document.getElementById('closeButton');


// --- GLOBAL STATE ---
let viewer;
const debrisEntities = new Map();

// --- INITIALIZE THE CESIUM VIEWER ---
async function initializeGlobe() {
    try {
        viewer = new Cesium.Viewer('cesiumContainer', {
            animation: false,
            timeline: false,
            geocoder: false,
            homeButton: false,
            sceneModePicker: false,
            baseLayerPicker: false,
            navigationHelpButton: false,
            infoBox: false,
            selectionIndicator: false,
            imageryProvider: new Cesium.IonImageryProvider({ assetId: 3954 }),
            terrainProvider: await Cesium.Terrain.fromWorldTerrain(),
        });

        viewer.screenSpaceEventHandler.removeInputAction(Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);
        viewer.scene.globe.enableLighting = true;
        
        setupEventHandlers();

        updateDebrisPositions();
        setInterval(updateDebrisPositions, UPDATE_INTERVAL_SECONDS * 1000);

    } catch (error) {
        console.error("Error initializing Cesium viewer:", error);
        loadingIndicator.innerText = "Error initializing globe. See console for details.";
    }
}


// --- SETUP EVENT HANDLERS ---
function setupEventHandlers() {
    const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

    // HOVER HANDLER for the tooltip
    handler.setInputAction((movement) => {
        const pickedObject = viewer.scene.pick(movement.endPosition);
        if (Cesium.defined(pickedObject) && pickedObject.id && pickedObject.id.properties) {
            const properties = pickedObject.id.properties;
            tooltipElement.style.display = 'block';
            tooltipElement.style.left = `${movement.endPosition.x + 10}px`;
            tooltipElement.style.top = `${movement.endPosition.y + 10}px`;
            tooltipElement.innerHTML = `<strong>${properties.name.getValue()}</strong>`;
        } else {
            tooltipElement.style.display = 'none';
        }
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    // SINGLE-CLICK HANDLER for the info card and zoom effect
    handler.setInputAction((click) => {
        const pickedObject = viewer.scene.pick(click.position);
        if (Cesium.defined(pickedObject) && pickedObject.id && pickedObject.id.properties) {
            const properties = pickedObject.id.properties;
            
            infoName.textContent = properties.name.getValue() || 'N/A';
            infoNorad.textContent = pickedObject.id.id || 'N/A';
            infoSpeed.textContent = properties.vel.getValue().toFixed(2);
            infoAltitude.textContent = properties.alt.getValue().toFixed(2);
            
            infoCard.classList.remove('card-hidden');
            infoCard.classList.add('card-visible');

            viewer.flyTo(pickedObject.id, {
                duration: 1.5,
                offset: new Cesium.HeadingPitchRange(
                    0,
                    Cesium.Math.toRadians(-45),
                    (properties.alt.getValue() * 1000) * 2.5
                ),
            });
        } else {
            infoCard.classList.add('card-hidden');
            infoCard.classList.remove('card-visible');
        }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
}

// --- CLOSE BUTTON LOGIC ---
closeButton.addEventListener('click', () => {
    infoCard.classList.add('card-hidden');
    infoCard.classList.remove('card-visible');

    // MODIFIED: Reset the camera view on close
    viewer.camera.flyHome(1.5);
});


// --- DATA FETCHING AND RENDERING ---
async function updateDebrisPositions() {
    if (!viewer) return;
    console.log("Fetching new debris positions...");
    loadingIndicator.style.display = 'block';

    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const debrisData = await response.json();
        const currentIds = new Set();

        debrisData.forEach(debris => {
            currentIds.add(debris.id);
            const position = Cesium.Cartesian3.fromDegrees(debris.lon, debris.lat, debris.alt * 1000);
            let entity = debrisEntities.get(debris.id);

            if (entity) {
                entity.position = position;
                entity.properties.vel = debris.vel;
                entity.properties.alt = debris.alt;
            } else {
                const newEntity = viewer.entities.add({
                    id: debris.id,
                    position: position,
                    point: {
                        pixelSize: getPixelSizeForAltitude(debris.alt),
                        color: getColorForVelocity(debris.vel)
                    },
                    properties: { name: debris.name, vel: debris.vel, alt: debris.alt }
                });
                debrisEntities.set(debris.id, newEntity);
            }
        });

        for (const id of debrisEntities.keys()) {
            if (!currentIds.has(id)) {
                viewer.entities.removeById(id);
                debrisEntities.delete(id);
            }
        }
        console.log(`Updated ${debrisEntities.size} debris objects.`);
    } catch (error) {
        console.error("Failed to fetch or render debris data:", error);
    } finally {
        loadingIndicator.style.display = 'none';
    }
}

// --- HELPER FUNCTIONS ---
function getColorForVelocity(velocity) {
    if (velocity > 10) return Cesium.Color.RED;
    if (velocity > 7.5) return Cesium.Color.ORANGE;
    if (velocity > 5) return Cesium.Color.YELLOW;
    return Cesium.Color.CYAN;
}

function getPixelSizeForAltitude(altitude) {
    if (altitude < 500) return 4;
    if (altitude < 1000) return 3;
    return 2;
}

// --- MAIN EXECUTION ---
initializeGlobe();