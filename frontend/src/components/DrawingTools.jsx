import React, { useState } from 'react'
import './DrawingTools.css'

const DrawingTools = ({ onToolSelect }) => {
  const [activeTool, setActiveTool] = useState('polygon')

  const tools = [
    { id: 'select', icon: '▶', title: 'Select' },
    { id: 'polygon', icon: '○', title: 'Draw Polygon' },
    { id: 'rectangle', icon: '▭', title: 'Draw Rectangle' },
    { id: 'polyline', icon: '✎', title: 'Draw Line' },
    { id: 'marker', icon: '+', title: 'Add Marker' },
    { id: 'delete', icon: '🗑', title: 'Delete' }
  ]

  const handleToolClick = (toolId) => {
    setActiveTool(toolId)
    if (onToolSelect) {
      onToolSelect(toolId)
    }
  }

  return (
    <div className="drawing-tools">
      {tools.map((tool) => (
        <button
          key={tool.id}
          className={`tool-button ${activeTool === tool.id ? 'active' : ''}`}
          onClick={() => handleToolClick(tool.id)}
          title={tool.title}
        >
          <span className="tool-icon">{tool.icon}</span>
        </button>
      ))}
    </div>
  )
}

export default DrawingTools
