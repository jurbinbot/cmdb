import { useState, useEffect, useCallback } from 'react'
import { servers, environments } from '../api/index'
import ConfirmDialog from '../components/ConfirmDialog'

const STATUS_BADGE = {
  active: 'badge-success',
  inactive: 'badge-gray',
  maintenance: 'badge-warning',
  decommissioned: 'badge-danger',
}

function ServerModal({ server, envList, onClose, onSaved }) {
  const isEdit = !!server
  const [form, setForm] = useState({
    hostname: '', ip_address: '', os: '', server_type: 'physical',
    environment_id: envList[0]?.id || '', role: '', status: 'active',
    ...server,
  })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  function set(f, v) { setForm(x => ({ ...x, [f]: v })) }

  async function submit(e) {
    e.preventDefault()
    if (!form.hostname.trim()) { setError('Hostname is required'); return }
    setSaving(true)
    try {
      if (isEdit) await servers.update(server.id, form)
      else await servers.create(form)
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save')
    } finally { setSaving(false) }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{isEdit ? 'Edit Server' : 'New Server'}</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div className="form-group">
              <label className="form-label">Hostname *</label>
              <input className="input" value={form.hostname} onChange={e => set('hostname', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">IP Address</label>
              <input className="input" value={form.ip_address} onChange={e => set('ip_address', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">OS</label>
              <input className="input" value={form.os} onChange={e => set('os', e.target.value)} placeholder="Ubuntu 22.04" />
            </div>
            <div className="form-group">
              <label className="form-label">Type</label>
              <select className="select" value={form.server_type} onChange={e => set('server_type', e.target.value)}>
                <option value="physical">Physical</option>
                <option value="virtual">Virtual</option>
                <option value="container">Container</option>
                <option value="cloud">Cloud</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Environment</label>
              <select className="select" value={form.environment_id} onChange={e => set('environment_id', e.target.value)}>
                <option value="">None</option>
                {envList.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Status</label>
              <select className="select" value={form.status} onChange={e => set('status', e.target.value)}>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="maintenance">Maintenance</option>
                <option value="decommissioned">Decommissioned</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Role</label>
            <input className="input" value={form.role} onChange={e => set('role', e.target.value)} placeholder="web, db, worker…" />
          </div>
          {error && <p style={{ color: 'var(--danger)', fontSize: '13px' }}>{error}</p>}
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : isEdit ? 'Update' : 'Create'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function Servers() {
  const [data, setData] = useState([])
  const [envList, setEnvList] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editServer, setEditServer] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [sRes, eRes] = await Promise.all([servers.getAll(), environments.getAll()])
      setData(sRes.data)
      setEnvList(eRes.data)
    } catch { setData([]) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  async function handleDelete() {
    await servers.remove(deleteTarget.id)
    setDeleteTarget(null)
    load()
  }

  const envMap = Object.fromEntries(envList.map(e => [e.id, e.name]))

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Servers</h2>
        <button className="btn btn-primary" onClick={() => { setEditServer(null); setShowModal(true) }}>+ New Server</button>
      </div>

      <div className="card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}><div className="spinner" style={{ margin: 'auto' }} /></div>
        ) : data.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No servers found.</div>
        ) : (
          <table className="table">
            <thead>
              <tr><th>Hostname</th><th>IP</th><th>OS</th><th>Type</th><th>Environment</th><th>Status</th><th>Role</th><th></th></tr>
            </thead>
            <tbody>
              {data.map(s => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 500, fontFamily: 'monospace' }}>{s.hostname}</td>
                  <td style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{s.ip_address || '—'}</td>
                  <td style={{ color: 'var(--text-secondary)' }}>{s.os || '—'}</td>
                  <td><span className="badge badge-gray">{s.server_type || s.type || '—'}</span></td>
                  <td style={{ color: 'var(--text-secondary)' }}>{envMap[s.environment_id] || '—'}</td>
                  <td><span className={`badge ${STATUS_BADGE[s.status] || 'badge-gray'}`}>{s.status}</span></td>
                  <td style={{ color: 'var(--text-secondary)' }}>{s.role || '—'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button className="btn btn-secondary btn-sm" onClick={() => { setEditServer(s); setShowModal(true) }}>Edit</button>
                      <button className="btn btn-danger btn-sm" onClick={() => setDeleteTarget(s)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && <ServerModal server={editServer} envList={envList} onClose={() => setShowModal(false)} onSaved={() => { setShowModal(false); load() }} />}
      {deleteTarget && (
        <ConfirmDialog
          title="Delete Server"
          message={`Delete "${deleteTarget.hostname}"?`}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  )
}
