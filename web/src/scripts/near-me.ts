// Ward Match in the browser. The point someone taps, or their location, is only ever
// used here with Turf's booleanPointInPolygon. Nothing is sent, and the map is never
// moved to the person's location (that would make the tile server load their area).
import { Map as MapLibreMap, Marker, NavigationControl, setWorkerUrl } from 'maplibre-gl';
import type { StyleSpecification } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
// MapLibre looks for its worker next to its own file, which the bundler doesn't copy.
// ?worker&url makes Vite bundle the worker as its own .js file and gives us its address.
// (A plain ?url import keeps the .mjs name, and many servers send .mjs with the wrong type.)
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import { booleanPointInPolygon } from '@turf/boolean-point-in-polygon';
import type { Feature, FeatureCollection, MultiPolygon, Polygon } from 'geojson';

type WardFeature = Feature<Polygon | MultiPolygon, { WARD_NO: number; WARD_NAME: string }>;

// OpenFreeMap needs no API key. Never point this at tile.openstreetmap.org.
const BASEMAP_STYLE = 'https://tiles.openfreemap.org/styles/positron';
// Used if the basemap can't load, so the ward outlines still show.
const PLAIN_STYLE: StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#f0eee6' } }],
};
const STORAGE_KEY = 'muni-ward';
setWorkerUrl(workerUrl);

const geoButton = document.getElementById('geo-btn') as HTMLButtonElement | null;
const geoStatus = document.getElementById('geo-status')!;
const mapStatus = document.getElementById('map-status')!;
const mapFallback = document.getElementById('map-fallback')!;
const remember = document.getElementById('remember') as HTMLInputElement | null;
const noneMessage = document.getElementById('ward-none')!;
const wardLinks = [...document.querySelectorAll<HTMLAnchorElement>('.ward-list a[data-ward]')];
const wardSections = [...document.querySelectorAll<HTMLElement>('.ward-result')];

let wards: WardFeature[] = [];
let map: MapLibreMap | null = null;
let marker: Marker | null = null;
let chosenWard: number | null = null;

function readSavedWard(): number | null {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? Number(saved) : null;
  } catch {
    return null;
  }
}

function saveWard(ward: number | null) {
  try {
    if (ward === null) localStorage.removeItem(STORAGE_KEY);
    else localStorage.setItem(STORAGE_KEY, String(ward));
  } catch {
    // Storage blocked: the ward still shows, it just won't be remembered.
  }
}

function wardAt(lng: number, lat: number): number | null {
  const ward = wards.find((feature) => booleanPointInPolygon([lng, lat], feature));
  return ward ? ward.properties.WARD_NO : null;
}

function highlightOnMap(ward: number | null) {
  if (!map || !map.getLayer('ward-selected')) return;
  map.setFilter('ward-selected', ['==', ['get', 'WARD_NO'], ward ?? -1]);
}

function showWard(ward: number, moveFocus: boolean) {
  const section = wardSections.find((s) => Number(s.dataset.ward) === ward);
  if (!section) return;
  chosenWard = ward;
  for (const s of wardSections) s.classList.toggle('is-shown', s === section);
  for (const link of wardLinks) {
    if (Number(link.dataset.ward) === ward) link.setAttribute('aria-current', 'true');
    else link.removeAttribute('aria-current');
  }
  noneMessage.hidden = true;
  highlightOnMap(ward);
  if (remember?.checked) saveWard(ward);
  history.replaceState(null, '', `#ward-${ward}`);
  if (moveFocus) section.focus();
}

function placeMarker(lng: number, lat: number) {
  if (!map) return;
  if (!marker) marker = new Marker({ color: '#2d5a9e' });
  marker.setLngLat([lng, lat]).addTo(map);
}

function wardBounds(): [[number, number], [number, number]] {
  let west = Infinity, south = Infinity, east = -Infinity, north = -Infinity;
  for (const ward of wards) {
    const polygons = ward.geometry.type === 'Polygon' ? [ward.geometry.coordinates] : ward.geometry.coordinates;
    for (const polygon of polygons) {
      for (const [lng, lat] of polygon[0]) {
        west = Math.min(west, lng);
        east = Math.max(east, lng);
        south = Math.min(south, lat);
        north = Math.max(north, lat);
      }
    }
  }
  return [[west, south], [east, north]];
}

function addWardLayers(wardData: FeatureCollection) {
  if (!map) return;
  map.addSource('wards', { type: 'geojson', data: wardData });
  map.addLayer({ id: 'ward-fill', type: 'fill', source: 'wards', paint: { 'fill-color': '#1aa7e0', 'fill-opacity': 0.08 } });
  map.addLayer({
    id: 'ward-selected', type: 'fill', source: 'wards',
    paint: { 'fill-color': '#66cdc8', 'fill-opacity': 0.45 },
    filter: ['==', ['get', 'WARD_NO'], chosenWard ?? -1],
  });
  map.addLayer({ id: 'ward-line', type: 'line', source: 'wards', paint: { 'line-color': '#2d5a9e', 'line-width': 2 } });
}

function startMap(wardData: FeatureCollection) {
  let styleLoaded = false;
  let usedPlainStyle = false;
  try {
    map = new MapLibreMap({
      container: 'ward-map',
      style: BASEMAP_STYLE,
      bounds: wardBounds(),
      fitBoundsOptions: { padding: 16 },
      attributionControl: { compact: false },
    });
  } catch {
    mapFallback.textContent = "The map couldn't start in this browser. Use the list or your location instead.";
    return;
  }
  mapFallback.hidden = true;
  map.addControl(new NavigationControl({ showCompass: false }), 'top-right');

  map.on('style.load', () => {
    styleLoaded = true;
    addWardLayers(wardData);
  });
  map.on('error', () => {
    if (styleLoaded || usedPlainStyle) return;
    usedPlainStyle = true;
    mapStatus.textContent = "The background map didn't load. The ward outlines still work.";
    map!.setStyle(PLAIN_STYLE);
  });
  map.on('click', (event) => {
    const { lng, lat } = event.lngLat;
    placeMarker(lng, lat);
    const ward = wardAt(lng, lat);
    if (ward === null) {
      mapStatus.textContent = 'That spot is outside the City of Waterloo wards.';
      return;
    }
    mapStatus.textContent = `That spot is in Ward ${ward}.`;
    showWard(ward, false);
  });
}

function useLocation() {
  if (!navigator.geolocation) {
    geoStatus.textContent = "This browser can't share a location. Pick your ward from the list.";
    return;
  }
  if (wards.length === 0) {
    geoStatus.textContent = 'The ward boundaries are still loading. Try again in a moment.';
    return;
  }
  geoStatus.textContent = 'Finding your location on this device…';
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { longitude, latitude } = position.coords;
      const ward = wardAt(longitude, latitude);
      if (ward === null) {
        geoStatus.textContent = 'Your location is outside the City of Waterloo wards.';
        return;
      }
      placeMarker(longitude, latitude);
      geoStatus.textContent = `You're in Ward ${ward}.`;
      showWard(ward, true);
    },
    () => {
      geoStatus.textContent = "We couldn't get your location. Pick your ward from the list.";
    },
    { timeout: 10000 },
  );
}

async function start() {
  for (const link of wardLinks) {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      showWard(Number(link.dataset.ward), true);
    });
  }
  geoButton?.addEventListener('click', useLocation);
  remember?.addEventListener('change', () => {
    saveWard(remember.checked ? chosenWard : null);
  });

  const saved = readSavedWard();
  const fromHash = /^#ward-(\d+)$/.exec(window.location.hash);
  if (saved) {
    if (remember) remember.checked = true;
    showWard(saved, false);
    geoStatus.textContent = `Showing Ward ${saved}, remembered on this device.`;
  } else if (fromHash) {
    showWard(Number(fromHash[1]), false);
  }

  const response = await fetch('/data/wards.geojson');
  if (!response.ok) throw new Error(`wards.geojson returned ${response.status}`);
  const wardData = (await response.json()) as FeatureCollection;
  wards = wardData.features as WardFeature[];
  startMap(wardData);
}

start().catch(() => {
  mapFallback.textContent = "The ward map didn't load. Pick your ward from the list.";
  if (geoButton) geoButton.disabled = true;
});
