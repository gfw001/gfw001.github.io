# 3D Globe Visualization

An interactive 3D globe showing visited countries and cities using Globe.GL.

## Features

- **3D Interactive Globe** - Rotate, zoom, and explore with mouse/touch
- **Country Highlighting** - Visited countries highlighted with blue polygons
- **City Markers** - Points marking specific cities and locations visited
- **Interactive Tooltips** - Hover over locations to see names and dates
- **Auto-Rotation** - Optional automatic globe rotation
- **Responsive Design** - Works on desktop and mobile devices
- **Beautiful Visuals** - Earth textures with atmospheric effects and starry background

## File Structure

```
visitings/
├── index.html          # Main 3D globe visualization
├── data/
│   ├── cities.js      # Array of cities with coordinates and dates
│   └── countries.js   # Object of visited countries
└── README.md          # This file
```

## How to Use

### Viewing Locally

1. Open `index.html` in a web browser
2. The globe will load with your visited locations
3. Use mouse to rotate and zoom:
   - **Left click + drag** to rotate
   - **Scroll wheel** to zoom
   - **Right click + drag** to pan

### Adding New Locations

#### Add a City
Edit `data/cities.js` and add a new entry:
```javascript
{name: 'Paris, France', latitude: 48.8566, longitude: 2.3522, radius: 3, fillKey: 'city', date: '2025'},
```

#### Add a Country
Edit `data/countries.js` and add a new entry using ISO alpha-3 code:
```javascript
FRA: {fillKey: 'visited'},  // France
```

Find ISO codes here: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3

## Technology Stack

- **Globe.GL** - 3D globe visualization library
- **Three.js** - WebGL 3D graphics (used by Globe.GL)
- **TopojSON** - Geographic data format for countries
- **Bootstrap** - UI styling framework

## Customization

### Change Colors
Edit the CSS variables in `index.html`:
- Background gradient: `.body` background
- City color: `pointColor` in JavaScript
- Country color: `polygonCapColor` in JavaScript
- UI accent: `#A8DAF9` throughout

### Adjust Globe Settings
Modify globe parameters in JavaScript:
- Initial view: `globe.pointOfView({ lat, lng, altitude })`
- Rotation speed: `globe.controls().autoRotateSpeed`
- Atmosphere: `atmosphereColor` and `atmosphereAltitude`

## Browser Compatibility

Requires a modern browser with WebGL support:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Credits

Built with:
- [Globe.GL](https://globe.gl/) by Vasco Asturiano
- Earth textures from NASA Blue Marble
- Country data from Natural Earth
