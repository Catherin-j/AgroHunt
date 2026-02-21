# AgroHunt Frontend

A precision agriculture application with satellite map view and crop analysis tools.

## Features

### Left Panel (AgroSight)
- **Location Selection**: Select country, state, and district
- **Coordinates Input**: Enter latitude and longitude to fly to specific location
- **Crop Selection**: Choose target crop type
- **Fly to Location**: Navigate to specified coordinates with smooth animation

### Right Panel (Crop Analysis)
- **Live Data**: Real-time crop analysis display
- **Plausibility Metrics**: Field area, confidence levels
- **Climate Data**: Temperature, humidity, wind, precipitation, UV index
- **Soil Information**: Type, pH, nitrogen, moisture, organic matter
- **Risk Assessment**: Visual risk indicator

### Drawing Tools (Bottom Center)
- **Select Tool**: Navigate and select features (▶️)
- **Draw Polygon**: Create custom field boundaries (⬡)
- **Draw Rectangle**: Draw rectangular areas (▢)
- **Draw Line**: Add polylines and paths (✏️)
- **Add Marker**: Place location markers (➕)
- **Delete Tool**: Remove drawn features (🗑️)

### Map Features
- **Satellite Imagery**: High-resolution Esri World Imagery
- **Labels Overlay**: Place names and boundaries
- **Interactive Controls**: Zoom and pan
- **Sample Polygon**: Pre-drawn field example

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Usage

### Development Mode
Start the development server:
```bash
npm run dev
```

The application will open at http://localhost:3000

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Map.jsx              # Main map component
│   │   ├── Map.css
│   │   ├── LeftPanel.jsx        # Location and crop controls
│   │   ├── LeftPanel.css
│   │   ├── RightPanel.jsx       # Analysis data display
│   │   ├── RightPanel.css
│   │   ├── DrawingTools.jsx     # Map drawing toolbar
│   │   └── DrawingTools.css
│   ├── App.jsx                  # Root component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── index.html
├── package.json
└── vite.config.js
```

## Technologies

- **React 18**: UI framework
- **Leaflet**: Interactive map library
- **React-Leaflet**: React components for Leaflet
- **Vite**: Build tool and dev server
- **Esri World Imagery**: Satellite imagery provider

## Customization

### Change Default Map Center
Edit the `center` state in [Map.jsx](src/components/Map.jsx):
```javascript
const [center] = useState([latitude, longitude])
```

### Modify Polygon Colors
Update the `pathOptions` in [Map.jsx](src/components/Map.jsx):
```javascript
pathOptions={{
  color: '#00ff00',        // Border color
  fillColor: '#00ff00',    // Fill color
  fillOpacity: 0.2,        // Transparency
  weight: 2                // Border width
}}
```

### Add More Crop Types
Edit the crop dropdown in [LeftPanel.jsx](src/components/LeftPanel.jsx).

### Update Climate/Soil Data
Pass custom `cropData` prop to [RightPanel.jsx](src/components/RightPanel.jsx).

## License

MIT
