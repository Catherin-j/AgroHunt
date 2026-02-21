import React from 'react'
import './RightPanel.css'

const RightPanel = ({ cropData }) => {
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
    <div className="right-panel">
      <div className="panel-header-right">
        <span className="live-indicator">🟢 LIVE</span>
        <h2 className="panel-title">🌾 Crop Analysis</h2>
      </div>

      {/* Crop Analysis Section */}
      <div className="analysis-section">
        <div className="stat-card highlight">
          <div className="stat-label">PLAUSIBILITY</div>
          <div className="stat-value large">{data.plausibility}</div>
        </div>
        
        <div className="stat-row">
          <div className="stat-card">
            <div className="stat-value">{data.area}</div>
            <div className="stat-label">FIELD AREA</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-value confidence">{data.confidence}</div>
            <div className="stat-label">NDVI</div>
          </div>
        </div>

        <div className="stat-row">
          <div className="stat-card">
            <div className="stat-value highlight-orange">{data.climate.temperature}</div>
            <div className="stat-label">NDVI</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-value highlight-blue">6.8</div>
            <div className="stat-label">NDVI</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">🌱 CROP</div>
          <div className="crop-info">
            <div className="info-row">
              <span>Target Crop</span>
              <span className="value">Unselected</span>
            </div>
            <div className="info-row">
              <span>Plausibility</span>
              <span className="value">--</span>
            </div>
            <div className="info-row">
              <span>Confidence</span>
              <span className="value">{data.confidence}</span>
            </div>
            <div className="info-row">
              <span>Growing Season</span>
              <span className="value">--</span>
            </div>
          </div>
        </div>
      </div>

      {/* Climate Section */}
      <div className="info-section">
        <div className="section-title">🌡️ CLIMATE</div>
        <div className="info-grid">
          <div className="info-item">
            <span className="label">Temperature</span>
            <span className="value highlight-orange">{data.climate.temperature}</span>
          </div>
          <div className="info-item">
            <span className="label">Humidity</span>
            <span className="value highlight-blue">{data.climate.humidity}</span>
          </div>
          <div className="info-item">
            <span className="label">Wind</span>
            <span className="value">{data.climate.wind}</span>
          </div>
          <div className="info-item">
            <span className="label">Precip/Week</span>
            <span className="value">{data.climate.precipitation}</span>
          </div>
          <div className="info-item">
            <span className="label">UV Index</span>
            <span className="value">{data.climate.uvIndex}</span>
          </div>
        </div>
      </div>

      {/* Soil Section */}
      <div className="info-section">
        <div className="section-title">🌱 SOIL</div>
        <div className="info-grid">
          <div className="info-item">
            <span className="label">Type</span>
            <span className="value">{data.soil.type}</span>
          </div>
          <div className="info-item">
            <span className="label">pH</span>
            <span className="value highlight-blue">{data.soil.ph}</span>
          </div>
          <div className="info-item">
            <span className="label">Nitrogen</span>
            <span className="value">{data.soil.nitrogen}</span>
          </div>
          <div className="info-item">
            <span className="label">Moisture</span>
            <span className="value highlight-blue">{data.soil.moisture}</span>
          </div>
          <div className="info-item">
            <span className="label">Organic Matter</span>
            <span className="value">{data.soil.organicMatter}</span>
          </div>
        </div>
      </div>

      {/* Risk Section */}
      <div className="info-section">
        <div className="section-title">⚠️ RISK</div>
        <div className="risk-indicator">
          <div className="risk-bar">
            <div className={`risk-level risk-${data.risk.toLowerCase()}`}></div>
          </div>
          <span className="risk-label">{data.risk}</span>
        </div>
      </div>
    </div>
  )
}

export default RightPanel
