import { useState, useEffect } from 'react'
import { applications, servers as serversApi, relationships } from '../api/index'

const REL_TYPES = [
  'depends_on', 'hosted_on', 'connects_to', 'owned_by', 'deployed_on', 'uses_database', 'exposes_endpoint',
]
const CI_TYPES = ['application', 'server', 'database']

export default function RelationshipModal({ sourceApp, onClose, onSaved }) {
  const [relType, setRelType] = useState('depends_on')
  const [targetType, setTargetType] = useState('application')
  const [targetId, setTargetId] = useState('')
  const [description, setDescription] = useState('')
  const [options, setOptions] = useState([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadOptions() {
      try {
        if (targetType === 'application') {
          const res = await applications.getAll()
          setOptions((res.data || []).filter(a => a.id !== sourceApp.id).map(a => ({ id: a.id, label: a.name })))
        } else if (targetType === 'server') {
          const res = await serversApi.getAll()
          setOptions((res.data || []).map(s => ({ id: s.id, label: s.hostname })))
        } else if (targetType === 'database') {
          const res = await fetch('/api/databases').then(r => r.json()).catch(() => [])
          setOptions((res || []).map(d => ({ id: d.id, label: d.name })))
        }
      } catch {
        setOptions([])
      }
    }
    setTargetId('')
    loadOptions()
  }, [targetType, sourceApp.id])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!targetId) { setError('Please select a target CI.'); return }
    setSaving(true)
    setError(null)
    try {
      await relationships.create({
        source_ci_type: 'application',
        source_ci_id: sourceApp.id,
        target_ci_type: targetType,
        target_ci_id: targetId,
        relationship_type: relType,
        description: description || null,
      })
      onSaved()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create relationship.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
      }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div style={{
        background: 'var(--bg-secondary)', border: '1px solid var(--border)',
        borderRadius: '10px', padding: '1.5rem', width: 440, maxWidth: '95vw',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Add Relationship</h3>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Source
            </label>
            <div style={{ padding: '0.5rem 0.75rem', background: 'var(--bg-hover)', borderRadius: '6px', fontSize: '13px', color: 'var(--text-muted)' }}>
              {sourceApp.name} (application)
            </div>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Relationship Type
            </label>
            <select
              value={relType}
              onChange={e => setRelType(e.target.value)}
              style={{ width: '100%', background: 'var(--bg-primary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', padding: '0.5rem 0.75rem', fontSize: '13px' }}
            >
              {REL_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Target CI Type
            </label>
            <select
              value={targetType}
              onChange={e => setTargetType(e.target.value)}
              style={{ width: '100%', background: 'var(--bg-primary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', padding: '0.5rem 0.75rem', fontSize: '13px' }}
            >
              {CI_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Target CI
            </label>
            <select
              value={targetId}
              onChange={e => setTargetId(e.target.value)}
              style={{ width: '100%', background: 'var(--bg-primary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', padding: '0.5rem 0.75rem', fontSize: '13px' }}
            >
              <option value="">Select {targetType}…</option>
              {options.map(o => <option key={o.id} value={o.id}>{o.label}</option>)}
            </select>
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Description (optional)
            </label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              rows={2}
              style={{ width: '100%', background: 'var(--bg-primary)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', padding: '0.5rem 0.75rem', fontSize: '13px', resize: 'vertical', boxSizing: 'border-box' }}
            />
          </div>

          {error && <div style={{ color: 'var(--danger)', fontSize: '13px', marginBottom: '0.75rem' }}>{error}</div>}

          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : 'Create Relationship'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
