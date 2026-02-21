import React from 'react'
import { Activity, Thermometer, Droplets, Wind, CloudRain, Sun, Info, AlertTriangle } from 'lucide-react'
import './RightPanel.css'

const RightPanel = ({ cropData, selectedShapeId, activeTool, isValidating, onValidate }) => {
  // Default data structure
  const data = cropData || {
    area: '2.3 ha',
    plausibility: '--',
    confidence: 'IDLE',
    growingSeason: '--',
    climate: {
      temperature: '26.6°C',
      humidity: '65.5%',
      wind: '11.4 km/h',
      precipitation: '14.1 mm',
      uvIndex: '8.3'
    },
    soil: {
      type: 'Alluvial-Clay',
      ph: '6.8',
      nitrogen: '213.7 ppm',
      moisture: '51.7%',
      organicMatter: '2.1%'
    },
    risk: 'Low'
  }

  return (
    <aside className="right-panel">
      <div className="panel-header-right">
        <div className="status-badge">
          <span className="dot"></span>
          LIVE
        </div>
        <h2 className="panel-title">Crop Property</h2>
      </div>

      <div className="panel-content">
        {/* Validate Plot button (only when a shape is selected and not drawing) */}
        {selectedShapeId && activeTool !== 'polygon' && (
          <button
            className="validate-btn"
            style={{ width: '100%', marginBottom: 16 }}
            onClick={onValidate}
            disabled={isValidating}
          >
            {isValidating ? '\u23f3 Validating...' : '\u2705 Validate Plot'}
          </button>
        )}
        {/* Plausibility Highlight */}
        <div className="highlight-card">
          <div className="card-label">PLAUSIBILITY</div>
          <div className="card-value-large">{data.plausibility}</div>
          <div className="card-footer">
            <Activity size={12} />
            Computed from satellite data
          </div>
        </div>

        {/* Primary Stats */}
        <div className="stats-grid">
          <div className="stat-box">
            <span className="box-label">FIELD AREA</span>
            <span className="box-val">{data.area}</span>
          </div>
          <div className="stat-box">
            <span className="box-label">NDVI CONF.</span>
            <span className="box-val accent">{data.confidence}</span>
          </div>
        </div>

        {/* Secondary Info Sections */}
        <div className="info-group">
          <div className="group-header">
            <Thermometer size={14} />
            <span>CLIMATE DATA</span>
          </div>
          <div className="info-cards">
            <div className="info-mini-card">
              <span className="mini-label">Temp</span>
              <span className="mini-val warm">{data.climate.temperature}</span>
            </div>
            <div className="info-mini-card">
              <span className="mini-label">Humidity</span>
              <span className="mini-val cool">{data.climate.humidity}</span>
            </div>
            <div className="info-mini-card">
              <span className="mini-label">Wind</span>
              <span className="mini-val">{data.climate.wind}</span>
            </div>
            <div className="info-mini-card">
              <span className="mini-label">Precip</span>
              <span className="mini-val">{data.climate.precipitation}</span>
            </div>
          </div>
        </div>

        <div className="info-group">
          <div className="group-header">
            <Droplets size={14} />
            <span>SOIL ANALYSIS</span>
          </div>
          <div className="details-list">
            <div className="detail-row">
              <span className="row-label">Soil Type</span>
              <span className="row-val">{data.soil.type}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">pH Level</span>
              <span className="row-val highlight">{data.soil.ph}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Nitrogen</span>
              <span className="row-val">{data.soil.nitrogen}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Moisture</span>
              <span className="row-val highlight">{data.soil.moisture}</span>
            </div>
          </div>
        </div>

        {/* Risk Section */}
        <div className="risk-container">
          <div className="group-header">
            <AlertTriangle size={14} />
            <span>RISK ASSESSMENT</span>
          </div>
          <div className="risk-content">
            <div className="risk-bar-bg">
              <div className={`risk-fill fill-${data.risk.toLowerCase()}`}></div>
            </div>
            <div className="risk-meta">
              <span className="risk-text">{data.risk} Risk</span>
              <Info size={12} className="info-icon" />
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default RightPanel
