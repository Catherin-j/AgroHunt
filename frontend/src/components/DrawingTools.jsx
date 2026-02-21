import React from 'react'
import { MousePointer2, Hexagon, PenTool, Square, Plus, Trash2, Check } from 'lucide-react'
import './DrawingTools.css'

const DrawingTools = ({ activeTool, onToolSelect, onFinishPolygon, drawingPointsCount, shapesCount, showValidate, onValidate, isValidating }) => {
  const tools = [
    { id: 'select', icon: <MousePointer2 size={18} />, title: 'Pan / Select' },
    { id: 'polygon', icon: <Hexagon size={18} />, title: 'Draw Polygon' },
    { id: 'pen', icon: <PenTool size={18} />, title: 'Pen (Freeform Polygon)' },
    { id: 'rectangle', icon: <Square size={18} />, title: 'Draw Rectangle' },
    { id: 'add', icon: <Plus size={18} />, title: 'Add New Shape' },
    { id: 'delete', icon: <Trash2 size={18} />, title: 'Delete Shape' },
    // Validate tool is conditionally rendered as a peer tool
    ...(showValidate ? [{ id: 'validate', icon: <span style={{fontSize:18}}>{isValidating ? '\u23f3' : '\u2705'}</span>, title: 'Validate Plot', isValidate: true }] : [])
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
        {tools.map((tool) => {
          if (tool.isValidate) {
            return (
              <button
                key={tool.id}
                className="tool-button validate-btn"
                style={{ background: '#00ff88', color: '#181818', fontWeight: 600, fontSize: 15, borderRadius: 8, padding: '0 16px', minWidth: 44, boxShadow: '0 2px 8px #00ff8855', border: 'none', transition: 'background 0.2s' }}
                onClick={onValidate}
                disabled={isValidating}
                title={tool.title}
              >
                {tool.icon}
              </button>
            );
          }
          return (
            <button
              key={tool.id}
              className={`tool-button ${activeTool === tool.id ? 'active' : ''} ${tool.id === 'delete' ? 'delete-tool' : ''}`}
              onClick={() => handleClick(tool.id)}
              title={tool.title}
            >
              <span className="tool-icon">{tool.icon}</span>
            </button>
          );
        })}

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
