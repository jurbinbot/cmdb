import { useState, useEffect, useCallback } from 'react'
import { environments } from '../api/index'
import ConfirmDialog from '../components/ConfirmDialog'

const TYPE_BADGE = {
  dev: 'badge-info',
  staging: 'badge-warning',
  prod: 'badge-danger',
}

function EnvModal({ env, onClose, onSaved }) {
  const isEdit = !!env
  const [form, setForm] = useState({ name: '', type: 'dev', description: '', ...env })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  function set(f, v) { setForm(x => ({ ...x, [f]: v })) }

  async function submit(e) {
    e.preventDefault()
    if (!form.name.trim()) { setError('Name is required'); return }
    setSaving(true)
    try {
      if (isEdit) await environments.update(env.id, form)
      else await environments.create(form)
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 440 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{isEdit ? 'Edit Environment' : 'New Environment'}</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Name *</label>
            <input className="input" value={form.name} onChange={e => set('name', e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Type</label>
            <select className="select" value={form.type} onChange={e => set('type', e.target.value)}>
              <option value="dev">dev</option>
              <option value="staging">staging</option>
              <option value="prod">prod</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="textarea" value={form.description} onChange={e => set('description', e.target.value)} />
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

export default function Environments() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editEnv, setEditEnv] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await environments.getAll()
      setData(res.data)
    } catch { setData([]) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  async function handleDelete() {
    await environments.remove(deleteTarget.id)
    setDeleteTarget(null)
    load()
  }

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Environments</h2>
        <button className="btn btn-primary" onClick={() => { setEditEnv(null); setShowModal(true) }}>+ New Environment</button>
      </div>

      <div className="card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}><div className="spinner" style={{ margin: 'auto' }} /></div>
        ) : data.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No environments found.</div>
        ) : (
          <table className="table">
            <thead>
              <tr><th>Name</th><th>Type</th><th>Description</th><th></th></tr>
            </thead>
            <tbody>
              {data.map(env => (
                <tr key={env.id}>
                  <td style={{ fontWeight: 500 }}>{env.name}</td>
                  <td><span className={`badge ${TYPE_BADGE[env.type] || 'badge-gray'}`}>{env.type}</span></td>
                  <td style={{ color: 'var(--text-secondary)' }}>{env.description || '—'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button className="btn btn-secondary btn-sm" onClick={() => { setEditEnv(env); setShowModal(true) }}>Edit</button>
                      <button className="btn btn-danger btn-sm" onClick={() => setDeleteTarget(env)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && <EnvModal env={editEnv} onClose={() => setShowModal(false)} onSaved={() => { setShowModal(false); load() }} />}
      {deleteTarget && (
        <ConfirmDialog
          title="Delete Environment"
          message={`Delete "${deleteTarget.name}"?`}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  )
}
