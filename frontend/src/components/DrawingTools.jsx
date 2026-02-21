import React from 'react'
import { MousePointer2, Hexagon, PenTool, Square, Plus, Trash2, Check } from 'lucide-react'
import './DrawingTools.css'

const DrawingTools = ({ activeTool, onToolSelect, onFinishPolygon, drawingPointsCount, shapesCount }) => {
  const tools = [
    { id: 'select', icon: <MousePointer2 size={18} />, title: 'Pan / Select' },
    { id: 'polygon', icon: <Hexagon size={18} />, title: 'Draw Polygon' },
    { id: 'pen', icon: <PenTool size={18} />, title: 'Pen (Freeform Polygon)' },
    { id: 'rectangle', icon: <Square size={18} />, title: 'Draw Rectangle' },
    { id: 'add', icon: <Plus size={18} />, title: 'Add New Shape' },
    { id: 'delete', icon: <Trash2 size={18} />, title: 'Delete Shape' }
  ]

  const handleClick = (toolId) => {
    if (toolId === 'add') {
      onToolSelect('polygon')
      return
    }
    onToolSelect(toolId)
  }

  const isDrawing = (activeTool === 'polygon' || activeTool === 'pen') && drawingPointsCount >= 3

  return (
    <div className="drawing-tools-container">
      <div className="drawing-tools">
        {tools.map((tool) => (
          <button
            key={tool.id}
            className={`tool-button ${activeTool === tool.id ? 'active' : ''} ${tool.id === 'delete' ? 'delete-tool' : ''}`}
            onClick={() => handleClick(tool.id)}
            title={tool.title}
          >
            <span className="tool-icon">{tool.icon}</span>
          </button>
        ))}

        {isDrawing && (
          <button
            className="tool-button finish-btn"
            onClick={onFinishPolygon}
            title="Close & finish polygon"
          >
            <span className="tool-icon"><Check size={18} /></span>
          </button>
        )}
      </div>

      {shapesCount > 0 && (
        <div className="shapes-badge">
          <Hexagon size={12} fill="currentColor" />
          <span>{shapesCount} {shapesCount === 1 ? 'Shape' : 'Shapes'}</span>
        </div>
      )}
    </div>
  )
}

export default DrawingTools
