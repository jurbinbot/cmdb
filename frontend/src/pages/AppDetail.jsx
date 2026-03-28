import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  useNodesState,
  useEdgesState,
} from 'reactflow'
import dagre from 'dagre'
import 'reactflow/dist/style.css'
import { applications, relationships } from '../api/index'
import AppModal from '../components/AppModal'
import AppNode from '../components/graph/AppNode'
import RelationshipModal from '../components/RelationshipModal'

const nodeTypes = { appNode: AppNode }

const STATUS_BADGE = {
  active: 'badge-success',
  deprecated: 'badge-warning',
  decommissioned: 'badge-gray',
  planned: 'badge-info',
}

const REL_TYPE_COLORS = {
  depends_on: '#6366f1',
  hosted_on: '#06b6d4',
  connects_to: '#8b5cf6',
  owned_by: '#f59e0b',
  deployed_on: '#10b981',
  uses_database: '#ec4899',
  exposes_endpoint: '#64748b',
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString()
}

function InfoRow({ label, value }) {
  return (
    <div style={{ display: 'flex', gap: '1rem', padding: '0.625rem 0', borderBottom: '1px solid var(--border)' }}>
      <div style={{ width: 140, flexShrink: 0, color: 'var(--text-secondary)', fontSize: '13px' }}>{label}</div>
      <div>{value || <span style={{ color: 'var(--text-muted)' }}>—</span>}</div>
    </div>
  )
}

const NODE_W = 200
const NODE_H = 70

function layoutNodes(nodes, edges) {
  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ rankdir: 'TB', nodesep: 50, ranksep: 70 })
  nodes.forEach(n => g.setNode(n.id, { width: NODE_W, height: NODE_H }))
  edges.forEach(e => g.setEdge(e.source, e.target))
  dagre.layout(g)
  return nodes.map(n => {
    const pos = g.node(n.id)
    return { ...n, position: { x: pos.x - NODE_W / 2, y: pos.y - NODE_H / 2 } }
  })
}

function flattenTree(node, result = []) {
  if (!node) return result
  result.push({ id: node.id, name: node.name, type: node.type, relationship_type: node.relationship_type })
  ;(node.children || []).forEach(c => flattenTree(c, result))
  return result
}

function buildGraphFromTree(rootApp, tree) {
  const nodesMap = {}
  const edgesList = []

  function addNode(id, label, status, app_type) {
    if (!nodesMap[id]) {
      nodesMap[id] = {
        id,
        type: 'appNode',
        position: { x: 0, y: 0 },
        data: { id, label, status, app_type },
      }
    }
  }

  function walk(node, parentId) {
    addNode(node.id, node.name, node.status, node.type)
    if (parentId) {
      edgesList.push({
        id: `${parentId}-${node.id}`,
        source: parentId,
        target: node.id,
        label: (node.relationship_type || '').replace(/_/g, ' '),
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: '#64748b', strokeWidth: 1.5 },
        labelStyle: { fontSize: 10, fill: '#94a3b8' },
        labelBgStyle: { fill: 'var(--bg-secondary)', fillOpacity: 0.9 },
        labelBgPadding: [4, 2],
        type: 'smoothstep',
      })
    }
    ;(node.children || []).forEach(c => walk(c, node.id))
  }

  // Root node
  addNode(rootApp.id, rootApp.name, rootApp.status, rootApp.app_type)
  ;(tree.children || []).forEach(c => walk(c, rootApp.id))

  return { nodes: Object.values(nodesMap), edges: edgesList }
}

function DependencyGraph({ app, depTree }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  useEffect(() => {
    if (!depTree) return
    const { nodes: rawNodes, edges: rawEdges } = buildGraphFromTree(app, depTree)
    if (rawNodes.length <= 1 && rawEdges.length === 0) {
      setNodes([])
      setEdges([])
      return
    }
    const laid = layoutNodes(rawNodes, rawEdges)
    setNodes(laid)
    setEdges(rawEdges)
  }, [depTree, app])

  if (!nodes.length) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No dependencies mapped yet — add relationships to see the dependency graph.
      </div>
    )
  }

  return (
    <div style={{ height: 360, border: '1px solid var(--border)', borderRadius: '8px', overflow: 'hidden' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.25 }}
        minZoom={0.2}
      >
        <Background color="var(--border)" gap={20} />
        <Controls />
      </ReactFlow>
    </div>
  )
}

export default function AppDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [app, setApp] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('overview')
  const [showEdit, setShowEdit] = useState(false)
  const [depTree, setDepTree] = useState(null)
  const [impact, setImpact] = useState(null)
  const [showRelModal, setShowRelModal] = useState(false)

  async function load() {
    setLoading(true)
    try {
      const res = await applications.getById(id)
      setApp(res.data)
    } catch {
      setApp(null)
    } finally {
      setLoading(false)
    }
  }

  async function loadRelData() {
    try {
      const [treeRes, impactRes] = await Promise.all([
        relationships.getDependencyTree(id),
        relationships.getImpact(id),
      ])
      setDepTree(treeRes.data)
      setImpact(impactRes.data)
    } catch {
      setDepTree(null)
      setImpact([])
    }
  }

  useEffect(() => { load() }, [id])

  useEffect(() => {
    if (tab === 'dependencies' || tab === 'impact') {
      loadRelData()
    }
  }, [tab, id])

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}><div className="spinner" style={{ margin: 'auto' }} /></div>
  if (!app) return <div className="card"><p style={{ color: 'var(--danger)' }}>Application not found.</p></div>

  const tabs = ['Overview', 'Deployments', 'Endpoints', 'Ownership', 'Dependencies', 'Impact']

  // Downstream: what this app depends on (flat from dep tree)
  const downstream = depTree ? flattenTree(depTree).filter(n => n.id !== app.id) : []

  // Upstream: what depends on this app (from impact endpoint)
  const upstream = impact || []

  // Group upstream by ci_type
  const upstreamByType = {}
  upstream.forEach(item => {
    upstreamByType[item.ci_type] = upstreamByType[item.ci_type] || []
    upstreamByType[item.ci_type].push(item)
  })

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/applications')}>← Back</button>
            <h2 style={{ fontSize: '20px', fontWeight: 700 }}>{app.name}</h2>
            <span className={`badge ${STATUS_BADGE[app.status] || 'badge-gray'}`}>{app.status}</span>
            <span className="badge badge-gray">{app.app_type}</span>
            {app.tier && <span className="badge badge-gray">Tier {app.tier}</span>}
          </div>
          {app.description && <p style={{ color: 'var(--text-secondary)', maxWidth: 600 }}>{app.description}</p>}
        </div>
        <button className="btn btn-secondary" onClick={() => setShowEdit(true)}>Edit</button>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0', borderBottom: '1px solid var(--border)', marginBottom: '1.25rem' }}>
        {tabs.map(t => (
          <button
            key={t}
            onClick={() => setTab(t.toLowerCase())}
            style={{
              padding: '0.625rem 1.25rem',
              background: 'none',
              border: 'none',
              borderBottom: tab === t.toLowerCase() ? '2px solid var(--accent)' : '2px solid transparent',
              color: tab === t.toLowerCase() ? 'var(--text-primary)' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: tab === t.toLowerCase() ? '600' : '400',
              marginBottom: '-1px',
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'overview' && (
        <div className="card">
          <InfoRow label="Name" value={app.name} />
          <InfoRow label="Type" value={app.app_type} />
          <InfoRow label="Status" value={<span className={`badge ${STATUS_BADGE[app.status] || 'badge-gray'}`}>{app.status}</span>} />
          <InfoRow label="Tier" value={app.tier ? `Tier ${app.tier}` : null} />
          <InfoRow label="Description" value={app.description} />
          <InfoRow label="Repository" value={app.repo_url ? <a href={app.repo_url} target="_blank" rel="noopener noreferrer">{app.repo_url}</a> : null} />
          <InfoRow label="Documentation" value={app.docs_url ? <a href={app.docs_url} target="_blank" rel="noopener noreferrer">{app.docs_url}</a> : null} />
          <InfoRow label="Created" value={fmtDate(app.created_at)} />
          <InfoRow label="Updated" value={fmtDate(app.updated_at)} />
        </div>
      )}

      {tab === 'deployments' && (
        <div className="card" style={{ padding: 0 }}>
          {!app.deployments?.length ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No deployments.</div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Environment</th>
                  <th>Version</th>
                  <th>Deployed By</th>
                  <th>Deployed At</th>
                  <th>Current</th>
                </tr>
              </thead>
              <tbody>
                {app.deployments.map(d => (
                  <tr key={d.id}>
                    <td>{d.environment?.name || d.environment_id}</td>
                    <td style={{ fontFamily: 'monospace' }}>{d.version}</td>
                    <td>{d.deployed_by || '—'}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{fmtDate(d.deployed_at)}</td>
                    <td>{d.is_current ? <span className="badge badge-success">Current</span> : <span style={{ color: 'var(--text-muted)' }}>—</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'endpoints' && (
        <div className="card" style={{ padding: 0 }}>
          {!app.endpoints?.length ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No endpoints.</div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>URL</th>
                  <th>Protocol</th>
                  <th>Environment</th>
                  <th>Public</th>
                </tr>
              </thead>
              <tbody>
                {app.endpoints.map(ep => (
                  <tr key={ep.id}>
                    <td><a href={ep.url} target="_blank" rel="noopener noreferrer">{ep.url}</a></td>
                    <td><span className="badge badge-info">{ep.protocol}</span></td>
                    <td>{ep.environment?.name || ep.environment_id || '—'}</td>
                    <td>{ep.is_public ? <span className="badge badge-success">Yes</span> : <span className="badge badge-gray">No</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'ownership' && (
        <div>
          {!app.ownerships?.length ? (
            <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No ownership records.</div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem' }}>
              {app.ownerships.map((o, i) => (
                <div key={i} className="card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <strong>{o.team?.name || 'Unknown Team'}</strong>
                    <span className={`badge ${o.ownership_type === 'primary' ? 'badge-info' : 'badge-gray'}`}>
                      {o.ownership_type}
                    </span>
                  </div>
                  {o.team?.email && <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{o.team.email}</div>}
                  {o.team?.slack_channel && <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{o.team.slack_channel}</div>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === 'dependencies' && (
        <div>
          <div style={{ marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '0.75rem' }}>Dependency Graph</h3>
            {depTree === null ? (
              <div style={{ padding: '2rem', textAlign: 'center' }}><div className="spinner" style={{ margin: 'auto' }} /></div>
            ) : (
              <DependencyGraph app={app} depTree={depTree} />
            )}
          </div>
        </div>
      )}

      {tab === 'impact' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 600 }}>Impact Analysis</h3>
            <button className="btn btn-primary btn-sm" onClick={() => setShowRelModal(true)}>
              + Add Relationship
            </button>
          </div>

          {upstream.length === 0 && downstream.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
              No dependencies mapped yet — add relationships to see impact analysis.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
              {/* Upstream: what depends ON this app */}
              <div className="card">
                <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
                  Depends on this ({upstream.length})
                </h4>
                {upstream.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Nothing depends on this application.</p>
                ) : (
                  Object.entries(upstreamByType).map(([ciType, items]) => (
                    <div key={ciType} style={{ marginBottom: '0.75rem' }}>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.4rem' }}>{ciType}</div>
                      {items.map(item => (
                        <div key={item.ci_id} style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '0.4rem 0.5rem',
                          borderRadius: '4px',
                          background: 'var(--bg-hover)',
                          marginBottom: '0.25rem',
                        }}>
                          <span style={{ fontSize: '13px' }}>{item.name}</span>
                          <span style={{
                            fontSize: '10px',
                            padding: '1px 6px',
                            borderRadius: '4px',
                            background: (REL_TYPE_COLORS[item.relationship_type] || '#64748b') + '33',
                            color: REL_TYPE_COLORS[item.relationship_type] || '#94a3b8',
                            border: `1px solid ${(REL_TYPE_COLORS[item.relationship_type] || '#64748b')}66`,
                          }}>
                            {(item.relationship_type || '').replace(/_/g, ' ')}
                          </span>
                        </div>
                      ))}
                    </div>
                  ))
                )}
              </div>

              {/* Downstream: what this app depends on */}
              <div className="card">
                <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
                  This depends on ({downstream.length})
                </h4>
                {downstream.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>This application has no mapped dependencies.</p>
                ) : (
                  downstream.map(item => (
                    <div key={item.id} style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0.4rem 0.5rem',
                      borderRadius: '4px',
                      background: 'var(--bg-hover)',
                      marginBottom: '0.25rem',
                    }}>
                      <div>
                        <span style={{ fontSize: '13px' }}>{item.name}</span>
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>{item.type}</span>
                      </div>
                      {item.relationship_type && (
                        <span style={{
                          fontSize: '10px',
                          padding: '1px 6px',
                          borderRadius: '4px',
                          background: (REL_TYPE_COLORS[item.relationship_type] || '#64748b') + '33',
                          color: REL_TYPE_COLORS[item.relationship_type] || '#94a3b8',
                          border: `1px solid ${(REL_TYPE_COLORS[item.relationship_type] || '#64748b')}66`,
                        }}>
                          {item.relationship_type.replace(/_/g, ' ')}
                        </span>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {showEdit && (
        <AppModal
          app={app}
          onClose={() => setShowEdit(false)}
          onSaved={() => { setShowEdit(false); load() }}
        />
      )}

      {showRelModal && (
        <RelationshipModal
          sourceApp={app}
          onClose={() => setShowRelModal(false)}
          onSaved={() => { setShowRelModal(false); loadRelData() }}
        />
      )}
    </div>
  )
}

