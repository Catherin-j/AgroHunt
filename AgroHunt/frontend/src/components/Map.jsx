import React, { useState, useRef } from 'react'
import { MapContainer, TileLayer, Polygon, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import './Map.css'
import LeftPanel from './LeftPanel'
import RightPanel from './RightPanel'
import DrawingTools from './DrawingTools'
import Header from './Header'

// Helper component to fly to location
const FlyToLocation = ({ position }) => {
  const map = useMap()
  
  React.useEffect(() => {
    if (position) {
      map.flyTo([position.lat, position.lng], 15, {
        duration: 2
      })
    }
  }, [position, map])
  
  return null
}

const Map = () => {
  // Default center coordinates (you can change this to your desired location)
  const [center] = useState([20.5937, 78.9629]) // India center coordinates
  const [zoom] = useState(6)
  const [flyToPosition, setFlyToPosition] = useState(null)
  const [selectedCrop, setSelectedCrop] = useState(null)
  const [activeTool, setActiveTool] = useState('select')

  // Sample polygon coordinates - replace with your actual field coordinates
  const polygonPositions = [
    [20.5937, 78.9629],
    [20.6037, 78.9729],
    [20.5937, 78.9829],
    [20.5837, 78.9729]
  ]

  const handleFlyToLocation = (position) => {
    setFlyToPosition(position)
  }

  const handleCropSelect = (crop) => {
    setSelectedCrop(crop)
  }

  const handleToolSelect = (tool) => {
    setActiveTool(tool)
    console.log('Selected tool:', tool)
    // Implement drawing functionality here
  }

  return (
    <>
      <Header />
      
      <LeftPanel 
        onFlyToLocation={handleFlyToLocation}
        onCropSelect={handleCropSelect}
      />
      
      <RightPanel cropData={null} />
      
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ width: '100%', height: '100%' }}
        zoomControl={true}
      >
        <FlyToLocation position={flyToPosition} />
        
        {/* Satellite imagery from Esri */}
        <TileLayer
          attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          maxZoom={19}
        />
        
        {/* Optional: Add labels overlay */}
        <TileLayer
          attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
          url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
          maxZoom={19}
        />

        {/* Sample field polygon */}
        <Polygon
          positions={polygonPositions}
          pathOptions={{
            color: '#00ff00',
            fillColor: '#00ff00',
            fillOpacity: 0.2,
            weight: 2
          }}
        />
      </MapContainer>
      
      <DrawingTools onToolSelect={handleToolSelect} />
    </>
  )
}

export default Map
