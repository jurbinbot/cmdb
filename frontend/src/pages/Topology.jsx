import { useState, useEffect, useCallback, useMemo } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow'
import dagre from 'dagre'
import 'reactflow/dist/style.css'
import { applications, relationships } from '../api/index'
import AppNode from '../components/graph/AppNode'

const nodeTypes = { appNode: AppNode }

const NODE_WIDTH = 200
const NODE_HEIGHT = 70

function applyDagreLayout(nodes, edges) {
  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ rankdir: 'TB', nodesep: 60, ranksep: 80 })

  nodes.forEach(n => g.setNode(n.id, { width: NODE_WIDTH, height: NODE_HEIGHT }))
  edges.forEach(e => g.setEdge(e.source, e.target))
  dagre.layout(g)

  return nodes.map(n => {
    const pos = g.node(n.id)
    return {
      ...n,
      position: { x: pos.x - NODE_WIDTH / 2, y: pos.y - NODE_HEIGHT / 2 },
    }
  })
}

const APP_TYPES = ['web_app', 'api', 'service', 'batch_job', 'database', 'other']

export default function Topology() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filterType, setFilterType] = useState('')
  const [hideDeprecated, setHideDeprecated] = useState(false)
  const [hideDecommissioned, setHideDecommissioned] = useState(false)
  const [allApps, setAllApps] = useState([])
  const [allRels, setAllRels] = useState([])

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const [appsRes, relsRes] = await Promise.all([
          applications.getAll(),
          relationships.getAll(),
        ])
        setAllApps(appsRes.data)
        setAllRels(relsRes.data)
      } catch (e) {
        setError('Failed to load topology data')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  useEffect(() => {
    if (!allApps.length) return

    let visibleApps = allApps
    if (filterType) visibleApps = visibleApps.filter(a => a.app_type === filterType)
    if (hideDeprecated) visibleApps = visibleApps.filter(a => a.status !== 'deprecated')
    if (hideDecommissioned) visibleApps = visibleApps.filter(a => a.status !== 'decommissioned')

    const visibleIds = new Set(visibleApps.map(a => a.id))

    const rawNodes = visibleApps.map(app => ({
      id: app.id,
      type: 'appNode',
      position: { x: 0, y: 0 },
      data: {
        id: app.id,
        label: app.name,
        status: app.status,
        app_type: app.app_type,
      },
    }))

    const rawEdges = allRels
      .filter(r =>
        r.source_ci_type === 'application' &&
        r.target_ci_type === 'application' &&
        visibleIds.has(r.source_ci_id) &&
        visibleIds.has(r.target_ci_id)
      )
      .map(r => ({
        id: r.id,
        source: r.source_ci_id,
        target: r.target_ci_id,
        label: r.relationship_type.replace(/_/g, ' '),
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: '#64748b', strokeWidth: 1.5 },
        labelStyle: { fontSize: 10, fill: '#94a3b8' },
        labelBgStyle: { fill: 'var(--bg-secondary)', fillOpacity: 0.9 },
        labelBgPadding: [4, 2],
        type: 'smoothstep',
      }))

    const laid = applyDagreLayout(rawNodes, rawEdges)
    setNodes(laid)
    setEdges(rawEdges)
  }, [allApps, allRels, filterType, hideDeprecated, hideDecommissioned])

  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
      <div className="spinner" />
    </div>
  )

  if (error) return <div className="card" style={{ color: 'var(--danger)' }}>{error}</div>

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)' }}>
      {/* Filter bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '0.75rem 0',
        marginBottom: '0.5rem',
        flexWrap: 'wrap',
      }}>
        <select
          value={filterType}
          onChange={e => setFilterType(e.target.value)}
          style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border)',
            borderRadius: '6px',
            color: 'var(--text-primary)',
            padding: '0.4rem 0.75rem',
            fontSize: '13px',
          }}
        >
          <option value="">All Types</option>
          {APP_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '13px', color: 'var(--text-secondary)', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={hideDeprecated}
            onChange={e => setHideDeprecated(e.target.checked)}
          />
          Hide deprecated
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '13px', color: 'var(--text-secondary)', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={hideDecommissioned}
            onChange={e => setHideDecommissioned(e.target.checked)}
          />
          Hide decommissioned
        </label>

        <div style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-muted)' }}>
          {nodes.length} nodes · {edges.length} edges
        </div>
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
        {[
          { label: 'Active', color: '#22c55e' },
          { label: 'Deprecated', color: '#eab308' },
          { label: 'Decommissioned', color: '#6b7280' },
          { label: 'Planned', color: '#3b82f6' },
        ].map(({ label, color }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '12px', color: 'var(--text-secondary)' }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: color }} />
            {label}
          </div>
        ))}
      </div>

      {/* Graph */}
      <div style={{ flex: 1, border: '1px solid var(--border)', borderRadius: '8px', overflow: 'hidden', background: 'var(--bg-primary)' }}>
        {nodes.length === 0 ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
            No applications to display.
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            minZoom={0.1}
            maxZoom={2}
          >
            <Background color="var(--border)" gap={20} />
            <Controls />
            <MiniMap
              nodeColor={n => {
                const colors = { active: '#22c55e', deprecated: '#eab308', decommissioned: '#6b7280', planned: '#3b82f6' }
                return colors[n.data?.status] || '#6b7280'
              }}
              style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}
            />
          </ReactFlow>
        )}
      </div>
    </div>
  )
}
