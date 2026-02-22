import React, { useState, useMemo } from 'react'
import { Crosshair, Plus, X, Ruler, Wheat } from 'lucide-react'
import * as turf from '@turf/turf'
import './LeftPanel.css'

const LeftPanel = ({ onCropSelect, onGenerateArea, suggestedArea }) => {

  const [coordsList, setCoordsList] = useState([
    { latitude: '', longitude: '' }
  ])

  const [areaValue, setAreaValue] = useState('')
  const [areaUnit, setAreaUnit] = useState('hectares')
  const [selectedCrop, setSelectedCrop] = useState('')

  // ── Coordinate helpers ─────────────────────────────────
  const updateCoord = (index, field, value) => {
    setCoordsList(prev => prev.map((c, i) => i === index ? { ...c, [field]: value } : c))
  }

  const addCoord = () => {
    setCoordsList(prev => [...prev, { latitude: '', longitude: '' }])
  }

  const removeCoord = (index) => {
    if (coordsList.length <= 1) return
    setCoordsList(prev => prev.filter((_, i) => i !== index))
  }

  // ── Valid coords for area calc ─────────────────────────
  const validCoords = useMemo(() =>
    coordsList.filter(c =>
      c.latitude !== '' && c.longitude !== '' &&
      !isNaN(parseFloat(c.latitude)) && !isNaN(parseFloat(c.longitude))
    ).map(c => ({
      lat: parseFloat(c.latitude),
      lng: parseFloat(c.longitude)
    })),
    [coordsList]
  )

  // ── Auto-calculate area from 3+ coords ────────────────
  const autoArea = useMemo(() => {
    if (validCoords.length < 3) return null
    try {
      const ring = validCoords.map(c => [c.lng, c.lat])
      ring.push(ring[0])
      const poly = turf.polygon([ring])
      const m2 = turf.area(poly)
      return {
        m2,
        hectares: m2 / 10000,
        acres: m2 / 4046.86,
        cents: m2 / 40.4686
      }
    } catch { return null }
  }, [validCoords])

  // ── Convert manual area to hectares ───────────────────
  const toHectares = (val, unit) => {
    const v = parseFloat(val)
    if (isNaN(v) || v <= 0) return 0
    switch (unit) {
      case 'hectares': return v
      case 'acres': return v * 0.404686
      case 'cents': return v * 0.00404686
      case 'm2': return v / 10000
      default: return v
    }
  }

  // ── Generate area on map ──────────────────────────────
  const handleGenerateArea = () => {
    if (validCoords.length === 0 || !areaValue) return
    const ha = toHectares(areaValue, areaUnit)
    if (ha <= 0) return
    onGenerateArea({
      lat: validCoords[0].lat,
      lng: validCoords[0].lng,
      areaHectares: ha
    })
  }

  const handleCropChange = (e) => {
    const crop = e.target.value
    setSelectedCrop(crop)
    if (onCropSelect) onCropSelect(crop)
  }

  return (
    <div className="left-panel">
      <div className="panel-header">
        <h2 className="app-title">AgroSight</h2>
      </div>

      {/* ── CROP ────────────────────────────────────── */}
      <div className="panel-section">
        <div className="section-header">
          <Wheat size={14} className="section-icon-svg" />
          <h3>CROP</h3>
        </div>

        <div className="form-group">
          <label>CROP TYPE</label>
          <select value={selectedCrop} onChange={handleCropChange}>
            <option value="">Select crop...</option>
            <option value="rice">Rice</option>
            <option value="wheat">Wheat</option>
          </select>
        </div>
      </div>

      {/* ── COORDINATES ─────────────────────────────── */}
      <div className="panel-section">
        <div className="section-header">
          <Crosshair size={14} className="section-icon-svg" />
          <h3>COORDINATES</h3>
        </div>

        {coordsList.map((coord, i) => (
          <div className="coord-row" key={i}>
            <div className="coord-row-header">
              <span className="coord-label">Point {i + 1}</span>
              {coordsList.length > 1 && (
                <button className="coord-remove-btn" onClick={() => removeCoord(i)} title="Remove">
                  <X size={12} />
                </button>
              )}
            </div>
            <div className="coord-inputs">
              <div className="coord-field">
                <label>LAT</label>
                <input
                  type="text"
                  value={coord.latitude}
                  onChange={(e) => updateCoord(i, 'latitude', e.target.value)}
                  placeholder="0.000000"
                />
              </div>
              <div className="coord-field">
                <label>LNG</label>
                <input
                  type="text"
                  value={coord.longitude}
                  onChange={(e) => updateCoord(i, 'longitude', e.target.value)}
                  placeholder="0.000000"
                />
              </div>
            </div>
          </div>
        ))}

        <button className="add-coord-btn" onClick={addCoord}>
          <Plus size={13} /> Add Coordinate
        </button>
      </div>

      {/* ── AREA ────────────────────────────────────── */}
      <div className="panel-section">
        <div className="section-header">
          <Ruler size={14} className="section-icon-svg" />
          <h3>AREA</h3>
        </div>

        {autoArea && (
          <div className="area-grid">
            <div className="area-item">
              <span className="area-value">{autoArea.hectares.toFixed(4)}</span>
              <span className="area-unit-label">Hectares</span>
            </div>
            <div className="area-item">
              <span className="area-value">{autoArea.cents.toFixed(2)}</span>
              <span className="area-unit-label">Cents</span>
            </div>
            <div className="area-item">
              <span className="area-value">{autoArea.acres.toFixed(4)}</span>
              <span className="area-unit-label">Acres</span>
            </div>
            <div className="area-item">
              <span className="area-value">{autoArea.m2.toFixed(1)}</span>
              <span className="area-unit-label">m²</span>
            </div>
          </div>
        )}

        {!autoArea && (
          <p className="area-hint">Enter 3+ coordinates above to auto-calculate area.</p>
        )}

        <div className="area-input-row">
          <input
            type="number"
            className="area-input-field"
            placeholder="Area value (ha)"
            value={areaValue}
            onChange={(e) => setAreaValue(e.target.value)}
            min="0"
            step="any"
          />
          <select
            className="area-unit-field"
            value={areaUnit}
            onChange={(e) => setAreaUnit(e.target.value)}
          >
            <option value="hectares">ha</option>
            <option value="acres">ac</option>
            <option value="cents">cnt</option>
            <option value="m2">m²</option>
          </select>
        </div>

        <button
          className="generate-area-btn"
          onClick={handleGenerateArea}
          disabled={validCoords.length === 0 || !areaValue}
        >
          📐 Generate Area on Map
        </button>

        {suggestedArea != null && suggestedArea > 0 && (
          <p className="area-hint" style={{ marginTop: 8, color: 'var(--warning)' }}>
            ⚠️ Suggested: {suggestedArea.toFixed(4)} ha — drag corners to adjust
          </p>
        )}
      </div>

    </div>
  )
}

export default LeftPanel
