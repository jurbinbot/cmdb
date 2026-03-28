import { Handle, Position } from 'reactflow'
import { useNavigate } from 'react-router-dom'

const STATUS_COLORS = {
  active: '#22c55e',
  deprecated: '#eab308',
  decommissioned: '#6b7280',
  planned: '#3b82f6',
}

const TYPE_COLORS = {
  web_app: '#6366f1',
  api: '#8b5cf6',
  service: '#06b6d4',
  batch_job: '#f59e0b',
  database: '#10b981',
  other: '#64748b',
}

export default function AppNode({ data }) {
  const navigate = useNavigate()
  const borderColor = STATUS_COLORS[data.status] || '#6b7280'
  const typeBg = TYPE_COLORS[data.app_type] || '#64748b'

  return (
    <div
      onClick={() => navigate(`/applications/${data.id}`)}
      style={{
        background: 'var(--bg-secondary)',
        border: `2px solid ${borderColor}`,
        borderRadius: '8px',
        padding: '10px 14px',
        minWidth: 160,
        maxWidth: 200,
        cursor: 'pointer',
        boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
        transition: 'box-shadow 0.15s',
      }}
      onMouseEnter={e => e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.5)'}
      onMouseLeave={e => e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)'}
    >
      <Handle type="target" position={Position.Top} style={{ background: borderColor }} />

      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
        <div
          style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: borderColor,
            flexShrink: 0,
          }}
        />
        <div style={{
          fontSize: '13px',
          fontWeight: 600,
          color: 'var(--text-primary)',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>
          {data.label}
        </div>
      </div>

      {data.app_type && (
        <div style={{
          display: 'inline-block',
          padding: '1px 6px',
          background: typeBg + '33',
          color: typeBg,
          borderRadius: '4px',
          fontSize: '10px',
          fontWeight: 600,
          border: `1px solid ${typeBg}66`,
        }}>
          {data.app_type}
        </div>
      )}

      <Handle type="source" position={Position.Bottom} style={{ background: borderColor }} />
    </div>
  )
}
