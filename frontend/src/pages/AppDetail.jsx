import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { applications } from '../api/index'
import AppModal from '../components/AppModal'

const STATUS_BADGE = {
  active: 'badge-success',
  deprecated: 'badge-warning',
  decommissioned: 'badge-gray',
  planned: 'badge-info',
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

export default function AppDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [app, setApp] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('overview')
  const [showEdit, setShowEdit] = useState(false)

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

  useEffect(() => { load() }, [id])

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}><div className="spinner" style={{ margin: 'auto' }} /></div>
  if (!app) return <div className="card"><p style={{ color: 'var(--danger)' }}>Application not found.</p></div>

  const tabs = ['Overview', 'Deployments', 'Endpoints', 'Ownership']

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

      {showEdit && (
        <AppModal
          app={app}
          onClose={() => setShowEdit(false)}
          onSaved={() => { setShowEdit(false); load() }}
        />
      )}
    </div>
  )
}
