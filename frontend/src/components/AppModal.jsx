import { useState, useEffect } from 'react'
import { applications } from '../api/index'

const APP_TYPES = ['web', 'api', 'worker', 'cli', 'mobile', 'library', 'database', 'other']
const APP_STATUSES = ['active', 'deprecated', 'decommissioned', 'planned']
const APP_TIERS = ['1', '2', '3', '4']

export default function AppModal({ app, onClose, onSaved }) {
  const isEdit = !!app
  const [form, setForm] = useState({
    name: '',
    description: '',
    app_type: 'web',
    status: 'active',
    tier: '2',
    repo_url: '',
    docs_url: '',
    ...app,
  })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  function set(field, value) {
    setForm(f => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.name.trim()) {
      setError('Name is required')
      return
    }
    setSaving(true)
    setError('')
    try {
      if (isEdit) {
        await applications.update(app.id, form)
      } else {
        await applications.create(form)
      }
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{isEdit ? 'Edit Application' : 'New Application'}</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Name *</label>
            <input className="input" value={form.name} onChange={e => set('name', e.target.value)} placeholder="my-app" />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="textarea" value={form.description} onChange={e => set('description', e.target.value)} placeholder="What does this application do?" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
            <div className="form-group">
              <label className="form-label">Type</label>
              <select className="select" value={form.app_type} onChange={e => set('app_type', e.target.value)}>
                {APP_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Status</label>
              <select className="select" value={form.status} onChange={e => set('status', e.target.value)}>
                {APP_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Tier</label>
              <select className="select" value={form.tier} onChange={e => set('tier', e.target.value)}>
                {APP_TIERS.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Repo URL</label>
            <input className="input" value={form.repo_url} onChange={e => set('repo_url', e.target.value)} placeholder="https://github.com/org/repo" />
          </div>

          <div className="form-group">
            <label className="form-label">Docs URL</label>
            <input className="input" value={form.docs_url} onChange={e => set('docs_url', e.target.value)} placeholder="https://docs.example.com" />
          </div>

          {error && <p style={{ color: 'var(--danger)', fontSize: '13px' }}>{error}</p>}

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : isEdit ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
