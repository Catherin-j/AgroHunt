import React, { useState } from 'react'
import './LeftPanel.css'

const LeftPanel = ({ onFlyToLocation, onCropSelect }) => {
  const [location, setLocation] = useState({
    country: '',
    state: '',
    district: ''
  })
  
  const [coordinates, setCoordinates] = useState({
    latitude: '0.000000',
    longitude: '0.000000'
  })
  
  const [selectedCrop, setSelectedCrop] = useState('')

  const handleFlyToLocation = () => {
    if (coordinates.latitude && coordinates.longitude) {
      onFlyToLocation({
        lat: parseFloat(coordinates.latitude),
        lng: parseFloat(coordinates.longitude)
      })
    }
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
        <span className="pro-badge">PRO</span>
      </div>

      <div className="panel-section">
        <div className="section-header">
          <span className="section-icon">📍</span>
          <h3>LOCATION</h3>
        </div>
        
        <div className="form-group">
          <label>COUNTRY</label>
          <select 
            value={location.country}
            onChange={(e) => setLocation({...location, country: e.target.value})}
          >
            <option value="">Select country...</option>
            <option value="india">India</option>
            <option value="usa">United States</option>
            <option value="brazil">Brazil</option>
            <option value="china">China</option>
          </select>
        </div>

        <div className="form-group">
          <label>STATE</label>
          <select 
            value={location.state}
            onChange={(e) => setLocation({...location, state: e.target.value})}
          >
            <option value="">Select state...</option>
            <option value="kerala">Kerala</option>
            <option value="karnataka">Karnataka</option>
            <option value="tamil-nadu">Tamil Nadu</option>
          </select>
        </div>

        <div className="form-group">
          <label>DISTRICT</label>
          <select 
            value={location.district}
            onChange={(e) => setLocation({...location, district: e.target.value})}
          >
            <option value="">Select district...</option>
            <option value="thiruvananthapuram">Thiruvananthapuram</option>
            <option value="ernakulam">Ernakulam</option>
            <option value="kozhikode">Kozhikode</option>
          </select>
        </div>
      </div>

      <div className="panel-section">
        <div className="section-header">
          <span className="section-icon">🎯</span>
          <h3>COORDINATES</h3>
        </div>
        
        <div className="form-group">
          <label>LATITUDE</label>
          <input 
            type="text" 
            value={coordinates.latitude}
            onChange={(e) => setCoordinates({...coordinates, latitude: e.target.value})}
            placeholder="0.000000"
          />
        </div>

        <div className="form-group">
          <label>LONGITUDE</label>
          <input 
            type="text" 
            value={coordinates.longitude}
            onChange={(e) => setCoordinates({...coordinates, longitude: e.target.value})}
            placeholder="0.000000"
          />
        </div>

        <button className="fly-button" onClick={handleFlyToLocation}>
          ✈️ Fly to Location
        </button>
      </div>

      <div className="panel-section">
        <div className="section-header">
          <span className="section-icon">🌾</span>
          <h3>CROP</h3>
        </div>
        
        <div className="form-group">
          <label>CROP TYPE</label>
          <select value={selectedCrop} onChange={handleCropChange}>
            <option value="">Select crop...</option>
            <option value="rice">Rice</option>
            <option value="wheat">Wheat</option>
            <option value="corn">Corn</option>
            <option value="cotton">Cotton</option>
            <option value="sugarcane">Sugarcane</option>
            <option value="soybean">Soybean</option>
          </select>
        </div>
      </div>
    </div>
  )
}

export default LeftPanel
