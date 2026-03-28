import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { applications } from '../api/index'
import AppModal from '../components/AppModal'
import ConfirmDialog from '../components/ConfirmDialog'

const STATUS_BADGE = {
  active: 'badge-success',
  deprecated: 'badge-warning',
  decommissioned: 'badge-gray',
  planned: 'badge-info',
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString()
}

export default function Applications() {
  const navigate = useNavigate()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [filterType, setFilterType] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editApp, setEditApp] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterStatus) params.status = filterStatus
      if (filterType) params.app_type = filterType
      const res = await applications.getAll(params)
      setData(res.data)
    } catch {
      setData([])
    } finally {
      setLoading(false)
    }
  }, [filterStatus, filterType])

  useEffect(() => { load() }, [load])

  const filtered = data.filter(a =>
    a.name.toLowerCase().includes(search.toLowerCase())
  )

  async function handleDelete() {
    await applications.remove(deleteTarget.id)
    setDeleteTarget(null)
    load()
  }

  const allTypes = [...new Set(data.map(a => a.app_type).filter(Boolean))]

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Applications</h2>
        <button className="btn btn-primary" onClick={() => { setEditApp(null); setShowModal(true) }}>
          + New Application
        </button>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
        <input
          className="input"
          style={{ maxWidth: 260 }}
          placeholder="Search by name…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select className="select" style={{ maxWidth: 160 }} value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="deprecated">Deprecated</option>
          <option value="decommissioned">Decommissioned</option>
          <option value="planned">Planned</option>
        </select>
        <select className="select" style={{ maxWidth: 160 }} value={filterType} onChange={e => setFilterType(e.target.value)}>
          <option value="">All Types</option>
          {allTypes.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}><div className="spinner" style={{ margin: 'auto' }} /></div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No applications found.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Tier</th>
                <th>Repo</th>
                <th>Updated</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(app => (
                <tr key={app.id} onClick={() => navigate(`/applications/${app.id}`)}>
                  <td style={{ fontWeight: 500 }}>{app.name}</td>
                  <td><span className="badge badge-gray">{app.app_type}</span></td>
                  <td>
                    <span className={`badge ${STATUS_BADGE[app.status] || 'badge-gray'}`}>
                      {app.status}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>Tier {app.tier}</td>
                  <td>
                    {app.repo_url
                      ? <a href={app.repo_url} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()} style={{ color: 'var(--accent)' }}>↗</a>
                      : <span style={{ color: 'var(--text-muted)' }}>—</span>}
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{fmtDate(app.updated_at)}</td>
                  <td onClick={e => e.stopPropagation()}>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button className="btn btn-secondary btn-sm" onClick={() => { setEditApp(app); setShowModal(true) }}>Edit</button>
                      <button className="btn btn-danger btn-sm" onClick={() => setDeleteTarget(app)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <AppModal
          app={editApp}
          onClose={() => setShowModal(false)}
          onSaved={() => { setShowModal(false); load() }}
        />
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete Application"
          message={`Delete "${deleteTarget.name}"? This cannot be undone.`}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  )
}
