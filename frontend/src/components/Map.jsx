import React, { useState, useRef, useCallback } from 'react'
import { MapContainer, TileLayer, Polygon, Polyline, Rectangle, Marker, Tooltip, useMap, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import * as turf from '@turf/turf'
import 'leaflet/dist/leaflet.css'
import './Map.css'
import LeftPanel from './LeftPanel'
import RightPanel from './RightPanel'
import DrawingTools from './DrawingTools'

// ─── Fly to location helper ────────────────────────────────────
const FlyToLocation = ({ position }) => {
  const map = useMap()
  React.useEffect(() => {
    if (position) map.flyTo([position.lat, position.lng], 15, { duration: 2 })
  }, [position, map])
  return null
}

// ─── Drawing handler (lives inside MapContainer) ───────────────
const DrawingHandler = ({ activeTool, onAddPoint, onRectStart, onRectEnd, onDeleteClick }) => {
  const map = useMapEvents({
    click(e) {
      if (activeTool === 'polygon' || activeTool === 'pen') {
        onAddPoint([e.latlng.lat, e.latlng.lng])
      }
      if (activeTool === 'delete') {
        onDeleteClick(e.latlng)
      }
    },
    mousedown(e) {
      if (activeTool === 'rectangle') {
        map.dragging.disable()
        onRectStart([e.latlng.lat, e.latlng.lng])
      }
    },
    mousemove(e) {
      if (activeTool === 'rectangle') {
        onRectEnd([e.latlng.lat, e.latlng.lng])
      }
    },
    mouseup(e) {
      if (activeTool === 'rectangle') {
        map.dragging.enable()
        onRectEnd([e.latlng.lat, e.latlng.lng], true)
      }
    }
  })

  // Change cursor based on tool
  React.useEffect(() => {
    const container = map.getContainer()
    if (activeTool === 'select') container.style.cursor = ''
    else if (activeTool === 'delete') container.style.cursor = 'crosshair'
    else container.style.cursor = 'crosshair'

    return () => { container.style.cursor = '' }
  }, [activeTool, map])

  return null
}

// ─── Vertex icon ───────────────────────────────────────────────
const vertexIcon = new L.DivIcon({
  className: 'vertex-marker-icon',
  html: '<div style="width:10px;height:10px;background:#00ff88;border:2px solid #fff;border-radius:50%;box-shadow:0 0 6px rgba(0,0,0,0.5);"></div>',
  iconSize: [10, 10],
  iconAnchor: [5, 5]
})

const drawingVertexIcon = new L.DivIcon({
  className: 'vertex-marker-icon',
  html: '<div style="width:10px;height:10px;background:#ff9800;border:2px solid #fff;border-radius:50%;box-shadow:0 0 6px rgba(0,0,0,0.5);"></div>',
  iconSize: [10, 10],
  iconAnchor: [5, 5]
})

const suggestedVertexIcon = new L.DivIcon({
  className: 'vertex-marker-icon',
  html: '<div style="width:14px;height:14px;background:#ff9800;border:2px solid #fff;border-radius:50%;box-shadow:0 0 8px rgba(255,152,0,0.6);cursor:grab;"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7]
})

// ─── Main component ───────────────────────────────────────────
const MapComponent = () => {
  const [center] = useState([20.5937, 78.9629])
  const [zoom] = useState(6)
  const [flyToPosition, setFlyToPosition] = useState(null)
  const [selectedCrop, setSelectedCrop] = useState(null)
  const [activeTool, setActiveTool] = useState('select')

  // All completed polygons: [{ id, type:'polygon'|'rectangle', coords:[[lat,lng],...], bounds?:[[lat,lng],[lat,lng]] }]
  const [shapes, setShapes] = useState([])
  const [selectedShapeId, setSelectedShapeId] = useState(null)

  // Drawing-in-progress state
  const [drawingPoints, setDrawingPoints] = useState([])
  const [rectStart, setRectStart] = useState(null)
  const [rectEnd, setRectEnd] = useState(null)
  const [isDrawingRect, setIsDrawingRect] = useState(false)

  // Suggested area polygon (from "Generate Area on Map")
  const [suggestedPolygon, setSuggestedPolygon] = useState(null) // { coords: [[lat,lng],...], areaHa: number }

  const nextId = useRef(1)

  // ── Callbacks ──────────────────────────────────────────────
  const handleFlyToLocation = (position) => setFlyToPosition(position)
  const handleCropSelect = (crop) => setSelectedCrop(crop)

  // ── Generate area rectangle on map ────────────────────────
  const handleGenerateArea = ({ lat, lng, areaHectares }) => {
    // Convert hectares to m²
    const areaM2 = areaHectares * 10000
    // Calculate side length of a square in meters
    const sideM = Math.sqrt(areaM2)
    // Create a square bounding box centered on the GPS point
    const center = turf.point([lng, lat])
    const halfSideKm = (sideM / 2) / 1000
    const north = turf.destination(center, halfSideKm, 0).geometry.coordinates
    const south = turf.destination(center, halfSideKm, 180).geometry.coordinates
    const east = turf.destination(center, halfSideKm, 90).geometry.coordinates
    const west = turf.destination(center, halfSideKm, 270).geometry.coordinates

    const coords = [
      [north[1], west[0]],  // NW
      [north[1], east[0]],  // NE
      [south[1], east[0]],  // SE
      [south[1], west[0]]   // SW
    ]

    setSuggestedPolygon({ coords, areaHa: areaHectares })
    // Fly to the area
    setFlyToPosition({ lat, lng })
  }

  // ── Drag suggested vertex ─────────────────────────────────
  const handleSuggestedVertexDrag = useCallback((index, newLatLng) => {
    setSuggestedPolygon(prev => {
      if (!prev) return prev
      const newCoords = [...prev.coords]
      newCoords[index] = [newLatLng.lat, newLatLng.lng]
      // Recalculate area
      try {
        const ring = newCoords.map(c => [c[1], c[0]])
        ring.push(ring[0])
        const poly = turf.polygon([ring])
        const ha = turf.area(poly) / 10000
        return { coords: newCoords, areaHa: ha }
      } catch {
        return { coords: newCoords, areaHa: prev.areaHa }
      }
    })
  }, [])

  const handleToolSelect = (tool) => {
    // If switching away from a drawing tool, finalize current drawing
    if (activeTool === 'polygon' || activeTool === 'pen') {
      finalizePolygon()
    }
    setActiveTool(tool)
    setRectStart(null)
    setRectEnd(null)
    setIsDrawingRect(false)
  }

  // Add a point during polygon/pen drawing
  const handleAddPoint = useCallback((latlng) => {
    setDrawingPoints(prev => [...prev, latlng])
  }, [])

  // Finalize a polygon from the drawing points
  const finalizePolygon = useCallback(() => {
    setDrawingPoints(prev => {
      if (prev.length >= 3) {
        const id = nextId.current++
        setShapes(s => [...s, { id, type: 'polygon', coords: [...prev] }])
        setSelectedShapeId(id)
      }
      return []
    })
  }, [])

  // Double-click to close the polygon
  const handleDoubleClickFinish = useCallback(() => {
    finalizePolygon()
  }, [finalizePolygon])

  // Rectangle start
  const handleRectStart = useCallback((latlng) => {
    setRectStart(latlng)
    setRectEnd(latlng)
    setIsDrawingRect(true)
  }, [])

  // Rectangle move / end
  const handleRectEnd = useCallback((latlng, finished = false) => {
    if (!isDrawingRect && !finished) return
    setRectEnd(latlng)
    if (finished && rectStart) {
      const id = nextId.current++
      const bounds = [rectStart, latlng]
      // Convert rectangle to polygon coords (4 corners)
      const coords = [
        [bounds[0][0], bounds[0][1]],
        [bounds[0][0], bounds[1][1]],
        [bounds[1][0], bounds[1][1]],
        [bounds[1][0], bounds[0][1]]
      ]
      setShapes(s => [...s, { id, type: 'rectangle', coords, bounds }])
      setSelectedShapeId(id)
      setRectStart(null)
      setRectEnd(null)
      setIsDrawingRect(false)
    }
  }, [isDrawingRect, rectStart])

  // Delete: click near a shape to remove it
  const handleDeleteClick = useCallback((latlng) => {
    if (shapes.length === 0) return
    const clickPt = turf.point([latlng.lng, latlng.lat])

    let closestId = null
    let closestDist = Infinity

    shapes.forEach(shape => {
      // Find centroid of the shape
      const ring = shape.coords.map(c => [c[1], c[0]])
      ring.push(ring[0]) // close ring
      try {
        const poly = turf.polygon([ring])
        if (turf.booleanPointInPolygon(clickPt, poly)) {
          const centroid = turf.centroid(poly)
          const dist = turf.distance(clickPt, centroid)
          if (dist < closestDist) {
            closestDist = dist
            closestId = shape.id
          }
        }
      } catch (e) { /* skip invalid shapes */ }
    })

    if (closestId !== null) {
      setShapes(s => s.filter(sh => sh.id !== closestId))
      if (selectedShapeId === closestId) setSelectedShapeId(null)
    }
  }, [shapes, selectedShapeId])

  // Calculate area for a shape
  const calcArea = (coords) => {
    try {
      const ring = coords.map(c => [c[1], c[0]])
      ring.push(ring[0])
      const poly = turf.polygon([ring])
      return turf.area(poly) / 10000 // hectares
    } catch { return 0 }
  }

  // Submit plot to backend
  const submitPlot = async (shape) => {
    const ring = shape.coords.map(c => [c[1], c[0]])
    ring.push(ring[0])
    const geoJson = { type: 'Polygon', coordinates: [ring] }

    try {
      const response = await fetch('/api/validate-plot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farmer_id: 'farmer-001',
          crop: selectedCrop || 'rice',
          polygon: geoJson
        })
      })
      const result = await response.json()
      console.log('Validation result:', result)
      return result
    } catch (err) {
      console.error('Submit failed:', err)
    }
  }

  return (
    <>
      <LeftPanel
        onFlyToLocation={handleFlyToLocation}
        onCropSelect={handleCropSelect}
        onGenerateArea={handleGenerateArea}
        suggestedArea={suggestedPolygon ? suggestedPolygon.areaHa : null}
      />

      <RightPanel cropData={null} />

      <MapContainer
        center={center}
        zoom={zoom}
        style={{ width: '100%', height: '100%' }}
        zoomControl={true}
        doubleClickZoom={false}
      >
        <FlyToLocation position={flyToPosition} />

        <DrawingHandler
          activeTool={activeTool}
          onAddPoint={handleAddPoint}
          onRectStart={handleRectStart}
          onRectEnd={handleRectEnd}
          onDeleteClick={handleDeleteClick}
        />

        {/* Satellite imagery */}
        <TileLayer
          attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          maxZoom={19}
        />
        <TileLayer
          attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
          url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
          maxZoom={19}
        />

        {/* ── Completed shapes ─────────────────────────── */}
        {shapes.map(shape => (
          <React.Fragment key={shape.id}>
            <Polygon
              positions={shape.coords}
              pathOptions={{
                color: shape.id === selectedShapeId ? '#00ff88' : '#00ccff',
                fillColor: shape.id === selectedShapeId ? '#00ff88' : '#00ccff',
                fillOpacity: 0.2,
                weight: shape.id === selectedShapeId ? 3 : 2
              }}
              eventHandlers={{
                click: () => setSelectedShapeId(shape.id)
              }}
            >
              <Tooltip permanent direction="center" className="shape-tooltip">
                {calcArea(shape.coords).toFixed(2)} ha
              </Tooltip>
            </Polygon>
            {/* Vertex dots */}
            {shape.coords.map((coord, i) => (
              <Marker key={`v-${shape.id}-${i}`} position={coord} icon={vertexIcon} interactive={false} />
            ))}
          </React.Fragment>
        ))}

        {/* ── Drawing in-progress (polygon/pen) ────────── */}
        {drawingPoints.length >= 2 && (
          <Polyline
            positions={drawingPoints}
            pathOptions={{ color: '#ff9800', weight: 2, dashArray: '8,6' }}
          />
        )}
        {drawingPoints.length >= 3 && (
          <Polygon
            positions={drawingPoints}
            pathOptions={{ color: '#ff9800', fillColor: '#ff9800', fillOpacity: 0.1, weight: 1, dashArray: '6,4' }}
          />
        )}
        {drawingPoints.map((pt, i) => (
          <Marker
            key={`dp-${i}`}
            position={pt}
            icon={drawingVertexIcon}
            interactive={false}
          />
        ))}

        {/* ── Suggested area polygon (draggable) ──────── */}
        {suggestedPolygon && (
          <React.Fragment>
            <Polygon
              positions={suggestedPolygon.coords}
              pathOptions={{
                color: '#ff9800',
                fillColor: '#ff9800',
                fillOpacity: 0.12,
                weight: 2,
                dashArray: '10,8'
              }}
            >
              <Tooltip permanent direction="center" className="suggested-tooltip">
                {suggestedPolygon.areaHa.toFixed(4)} ha — drag corners
              </Tooltip>
            </Polygon>
            {suggestedPolygon.coords.map((coord, i) => (
              <Marker
                key={`sv-${i}`}
                position={coord}
                icon={suggestedVertexIcon}
                draggable={true}
                eventHandlers={{
                  dragend: (e) => {
                    handleSuggestedVertexDrag(i, e.target.getLatLng())
                  }
                }}
              />
            ))}
          </React.Fragment>
        )}

        {/* ── Rectangle drawing preview ────────────────── */}
        {isDrawingRect && rectStart && rectEnd && (
          <Rectangle
            bounds={[rectStart, rectEnd]}
            pathOptions={{ color: '#ff9800', fillColor: '#ff9800', fillOpacity: 0.1, weight: 2, dashArray: '8,6' }}
          />
        )}
      </MapContainer>

      <DrawingTools
        activeTool={activeTool}
        onToolSelect={handleToolSelect}
        onFinishPolygon={finalizePolygon}
        drawingPointsCount={drawingPoints.length}
        shapesCount={shapes.length}
      />
    </>
  )
}

export default MapComponent
