import React from 'react'
import {
  Activity,
  Thermometer,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock3,
  FileText,
  BarChart3,
  Map,
  Leaf,
  ShieldAlert
} from 'lucide-react'
import './RightPanel.css'

const toPercent = (value) => {
  if (value == null || Number.isNaN(Number(value))) return '--'
  return `${(Number(value) * 100).toFixed(1)}%`
}

const formatNumber = (value, digits = 2, unit = '') => {
  if (value == null || Number.isNaN(Number(value))) return '--'
  return `${Number(value).toFixed(digits)}${unit}`
}

const getRiskLabel = (decision) => {
  if (decision === 'PASS') return 'Low'
  if (decision === 'REVIEW') return 'Medium'
  if (decision === 'FAIL') return 'High'
  return 'Unknown'
}

const DecisionIcon = ({ decision }) => {
  if (decision === 'PASS') return <CheckCircle2 size={14} />
  if (decision === 'REVIEW') return <Clock3 size={14} />
  if (decision === 'FAIL') return <XCircle size={14} />
  return <Activity size={14} />
}

const RightPanel = ({ validationResult, isValidating, selectedCrop, selectedShape, calcArea }) => {
  const hasResult = !!validationResult && validationResult.decision !== 'ERROR'

  const decision = hasResult ? validationResult.decision : '--'
  const finalScore = hasResult ? validationResult.final_score : null
  const geometry = hasResult ? (validationResult.geometry || {}) : {}
  const ndvi = hasResult ? (validationResult.ndvi || {}) : {}
  const landUse = hasResult ? (validationResult.land_use || {}) : {}
  const cropEngine = hasResult ? (validationResult.crop_engine || {}) : {}
  const overlap = hasResult ? (validationResult.overlap || {}) : {}
  const explainability = hasResult ? (validationResult.explainability || {}) : {}

  const contributionBreakdown = explainability.contribution_breakdown || {}
  const explanationList = explainability.explanation || []

  const areaHa = selectedShape && calcArea ? calcArea(selectedShape.coords) : null
  const risk = getRiskLabel(decision)

  const statusText = isValidating
    ? 'Validating plot...'
    : hasResult
      ? 'Validation complete'
      : 'Draw/select a plot and validate'

  return (
    <aside className="right-panel">
      <div className="panel-header-right">
        <div className="status-badge">
          <span className="dot"></span>
          {isValidating ? 'PROCESSING' : 'LIVE'}
        </div>
        <h2 className="panel-title">Plot Validation Details</h2>
        <p className="panel-subtitle">{statusText}</p>
      </div>

      <div className="panel-content">
        <div className="highlight-card">
          <div className="card-label">DECISION</div>
          <div className={`card-value-large decision-${String(decision).toLowerCase()}`}>
            {decision}
          </div>
          <div className="card-footer">
            <DecisionIcon decision={decision} />
            Explainable automated plot validation
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-box">
            <span className="box-label">FINAL SCORE</span>
            <span className="box-val">{toPercent(finalScore)}</span>
          </div>
          <div className="stat-box">
            <span className="box-label">RISK LEVEL</span>
            <span className="box-val accent">{risk}</span>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-box">
            <span className="box-label">FIELD AREA</span>
            <span className="box-val">{areaHa != null ? `${areaHa.toFixed(2)} ha` : '--'}</span>
          </div>
          <div className="stat-box">
            <span className="box-label">CLAIMED CROP</span>
            <span className="box-val">{selectedCrop || '--'}</span>
          </div>
        </div>

        <div className="info-group">
          <div className="group-header">
            <Map size={14} />
            <span>GEOMETRY EVIDENCE</span>
          </div>
          <div className="details-list">
            <div className="detail-row">
              <span className="row-label">Geometry Score</span>
              <span className="row-val">{toPercent(geometry.geometry_score)}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Area (hectares)</span>
              <span className="row-val">{formatNumber(geometry.area_hectares, 2)}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Compactness</span>
              <span className="row-val">{formatNumber(geometry.compactness, 3)}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Country</span>
              <span className="row-val">{geometry.country || '--'}</span>
            </div>
          </div>
        </div>

        <div className="info-group">
          <div className="group-header">
            <Leaf size={14} />
            <span>NDVI & LAND USE</span>
          </div>
          <div className="details-list">
            <div className="detail-row">
              <span className="row-label">Mean NDVI</span>
              <span className="row-val">{formatNumber(ndvi.mean_ndvi, 3)}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Vegetation Ratio</span>
              <span className="row-val highlight">{toPercent(ndvi.vegetation_ratio)}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">NDVI Agriculture Score</span>
              <span className="row-val">{toPercent(ndvi.agriculture_score)}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Cropland Ratio</span>
              <span className="row-val">{toPercent(landUse.crop_ratio)}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Land Score</span>
              <span className="row-val">{toPercent(landUse.land_score)}</span>
            </div>
          </div>
        </div>

        <div className="info-group">
          <div className="group-header">
            <Thermometer size={14} />
            <span>CROP PLAUSIBILITY</span>
          </div>
          <div className="details-list">
            <div className="detail-row">
              <span className="row-label">Rainfall</span>
              <span className="row-val">{formatNumber(cropEngine.rainfall_mm, 1, ' mm')}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Temperature</span>
              <span className="row-val">{formatNumber(cropEngine.temperature_c, 2, ' °C')}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Elevation</span>
              <span className="row-val">{formatNumber(cropEngine.elevation_m, 1, ' m')}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Crop Suitability Score</span>
              <span className="row-val highlight">{toPercent(cropEngine.crop_score)}</span>
            </div>
          </div>
        </div>

        <div className="info-group">
          <div className="group-header">
            <ShieldAlert size={14} />
            <span>OVERLAP CHECK</span>
          </div>
          <div className="details-list">
            <div className="detail-row">
              <span className="row-label">Overlap Ratio</span>
              <span className="row-val">{toPercent(overlap.overlap_ratio)}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Overlap Severity</span>
              <span className="row-val">{overlap.severity || '--'}</span>
            </div>
            <div className="detail-row">
              <span className="row-label">Overlap Score</span>
              <span className="row-val">{toPercent(overlap.overlap_score)}</span>
            </div>
          </div>
        </div>

        <div className="info-group">
          <div className="group-header">
            <BarChart3 size={14} />
            <span>SCORE BREAKDOWN</span>
          </div>
          <div className="details-list">
            {Object.keys(contributionBreakdown).length === 0 && (
              <div className="detail-row">
                <span className="row-label">No scores yet</span>
                <span className="row-val">--</span>
              </div>
            )}
            {Object.entries(contributionBreakdown).map(([key, value]) => (
              <div className="detail-row" key={key}>
                <span className="row-label">{key}</span>
                <span className="row-val">{toPercent(value)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="risk-container">
          <div className="group-header">
            <AlertTriangle size={14} />
            <span>RISK ASSESSMENT</span>
          </div>
          <div className="risk-content">
            <div className="risk-bar-bg">
              <div className={`risk-fill fill-${risk.toLowerCase()}`}></div>
            </div>
            <div className="risk-meta">
              <span className="risk-text">{risk} Risk</span>
              <span className="risk-caption">Derived from final decision</span>
            </div>
          </div>
        </div>

        <div className="info-group">
          <div className="group-header">
            <FileText size={14} />
            <span>EXPLAINABILITY</span>
          </div>
          <div className="explainability-list">
            {explanationList.length === 0 && (
              <p className="explainability-item muted">Validate a plot to see detailed reasoning.</p>
            )}
            {explanationList.map((line, index) => (
              <p className="explainability-item" key={`${index}-${line}`}>
                {index + 1}. {line}
              </p>
            ))}

            {validationResult?.reason && (
              <p className="explainability-item muted">Reason: {validationResult.reason}</p>
            )}
            {(geometry.reason || ndvi.reason || overlap.explanation) && (
              <p className="explainability-item muted">
                {(geometry.reason || ndvi.reason || overlap.explanation)}
              </p>
            )}
          </div>
        </div>
      </div>
    </aside>
  )
}

export default RightPanel
