import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { applications, audit } from '../api/index'
import api from '../api/client'

function StatCard({ label, value, accent }) {
  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <div style={{ fontSize: '32px', fontWeight: 700, color: accent || 'var(--text-primary)', marginBottom: '0.25rem' }}>{value}</div>
      <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{label}</div>
    </div>
  )
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString()
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [apps, setApps] = useState([])
  const [deployments, setDeployments] = useState([])
  const [auditEvents, setAuditEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const timerRef = useRef(null)

  async function load() {
    try {
      const [appsRes, depRes, auditRes] = await Promise.all([
        applications.getAll(),
        api.get('/api/deployments', { params: { limit: 5 } }),
        audit.getAll({ limit: 5 }),
      ])
      setApps(appsRes.data || [])
      setDeployments(depRes.data || [])
      setAuditEvents(auditRes.data || [])
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    timerRef.current = setInterval(load, 30000)
    return () => clearInterval(timerRef.current)
  }, [])

  const counts = {
    total: apps.length,
    active: apps.filter(a => a.status === 'active').length,
    deprecated: apps.filter(a => a.status === 'deprecated').length,
    decommissioned: apps.filter(a => a.status === 'decommissioned').length,
  }

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Dashboard</h2>
        <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Auto-refreshes every 30s</span>
      </div>

      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        <StatCard label="Total Apps" value={counts.total} />
        <StatCard label="Active" value={counts.active} accent="var(--success)" />
        <StatCard label="Deprecated" value={counts.deprecated} accent="var(--warning)" />
        <StatCard label="Decommissioned" value={counts.decommissioned} accent="var(--text-muted)" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        {/* Recent deployments */}
        <div>
          <h3 style={{ marginBottom: '0.75rem', fontSize: '14px', fontWeight: 600, color: 'var(--text-secondary)' }}>Recent Deployments</h3>
          <div className="card" style={{ padding: 0 }}>
            {deployments.length === 0 ? (
              <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>No deployments yet.</div>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>App</th>
                    <th>Version</th>
                    <th>By</th>
                    <th>When</th>
                  </tr>
                </thead>
                <tbody>
                  {deployments.slice(0, 5).map(d => (
                    <tr key={d.id} onClick={() => navigate(`/applications/${d.application_id}`)}>
                      <td style={{ fontWeight: 500 }}>{d.application?.name || d.application_id}</td>
                      <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{d.version}</td>
                      <td style={{ color: 'var(--text-secondary)' }}>{d.deployed_by || '—'}</td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{fmtDate(d.deployed_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Recent audit events */}
        <div>
          <h3 style={{ marginBottom: '0.75rem', fontSize: '14px', fontWeight: 600, color: 'var(--text-secondary)' }}>Recent Audit Events</h3>
          <div className="card" style={{ padding: 0 }}>
            {auditEvents.length === 0 ? (
              <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>No audit events yet.</div>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Action</th>
                    <th>By</th>
                    <th>When</th>
                  </tr>
                </thead>
                <tbody>
                  {auditEvents.slice(0, 5).map(e => (
                    <tr key={e.id}>
                      <td><span className="badge badge-gray">{e.ci_type}</span></td>
                      <td>
                        <span className={`badge ${e.action === 'delete' ? 'badge-danger' : e.action === 'create' ? 'badge-success' : 'badge-info'}`}>
                          {e.action}
                        </span>
                      </td>
                      <td style={{ color: 'var(--text-secondary)' }}>{e.changed_by || '—'}</td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{fmtDate(e.changed_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
