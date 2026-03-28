import { useState, useEffect, useCallback } from 'react'
import { teams } from '../api/index'
import api from '../api/client'
import ConfirmDialog from '../components/ConfirmDialog'

function TeamModal({ team, onClose, onSaved }) {
  const isEdit = !!team
  const [form, setForm] = useState({ name: '', email: '', slack_channel: '', ...team })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  function set(f, v) { setForm(x => ({ ...x, [f]: v })) }

  async function submit(e) {
    e.preventDefault()
    if (!form.name.trim()) { setError('Name is required'); return }
    setSaving(true)
    try {
      if (isEdit) await teams.update(team.id, form)
      else await teams.create(form)
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save')
    } finally { setSaving(false) }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 440 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{isEdit ? 'Edit Team' : 'New Team'}</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Name *</label>
            <input className="input" value={form.name} onChange={e => set('name', e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="input" type="email" value={form.email} onChange={e => set('email', e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Slack Channel</label>
            <input className="input" value={form.slack_channel} onChange={e => set('slack_channel', e.target.value)} placeholder="#team-channel" />
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

function ContactModal({ teamId, contact, onClose, onSaved }) {
  const isEdit = !!contact
  const [form, setForm] = useState({ name: '', email: '', phone: '', role: '', team_id: teamId, ...contact })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  function set(f, v) { setForm(x => ({ ...x, [f]: v })) }

  async function submit(e) {
    e.preventDefault()
    if (!form.name.trim()) { setError('Name is required'); return }
    setSaving(true)
    try {
      if (isEdit) await api.put(`/api/contacts/${contact.id}`, form)
      else await api.post('/api/contacts', form)
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save')
    } finally { setSaving(false) }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 440 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{isEdit ? 'Edit Contact' : 'New Contact'}</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Name *</label>
            <input className="input" value={form.name} onChange={e => set('name', e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="input" type="email" value={form.email} onChange={e => set('email', e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Phone</label>
            <input className="input" value={form.phone} onChange={e => set('phone', e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Role</label>
            <input className="input" value={form.role} onChange={e => set('role', e.target.value)} />
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

export default function Teams() {
  const [data, setData] = useState([])
  const [contacts, setContacts] = useState({})
  const [expanded, setExpanded] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showTeamModal, setShowTeamModal] = useState(false)
  const [editTeam, setEditTeam] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [showContactModal, setShowContactModal] = useState(false)
  const [editContact, setEditContact] = useState(null)
  const [contactTeamId, setContactTeamId] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await teams.getAll()
      setData(res.data)
    } catch { setData([]) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  async function loadContacts(teamId) {
    try {
      const res = await api.get(`/api/teams/${teamId}/contacts`)
      setContacts(c => ({ ...c, [teamId]: res.data }))
    } catch {
      setContacts(c => ({ ...c, [teamId]: [] }))
    }
  }

  function toggleExpand(teamId) {
    if (expanded === teamId) {
      setExpanded(null)
    } else {
      setExpanded(teamId)
      loadContacts(teamId)
    }
  }

  async function handleDeleteTeam() {
    await teams.remove(deleteTarget.id)
    setDeleteTarget(null)
    load()
  }

  async function handleDeleteContact(contact) {
    await api.delete(`/api/contacts/${contact.id}`)
    loadContacts(contact.team_id)
  }

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Teams</h2>
        <button className="btn btn-primary" onClick={() => { setEditTeam(null); setShowTeamModal(true) }}>+ New Team</button>
      </div>

      {loading ? (
        <div style={{ padding: '2rem', textAlign: 'center' }}><div className="spinner" style={{ margin: 'auto' }} /></div>
      ) : data.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No teams found.</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {data.map(team => (
            <div key={team.id} className="card" style={{ padding: 0 }}>
              {/* Team row */}
              <div
                style={{ display: 'flex', alignItems: 'center', padding: '0.875rem 1.25rem', cursor: 'pointer' }}
                onClick={() => toggleExpand(team.id)}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, marginBottom: '2px' }}>{team.name}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {team.email && <span style={{ marginRight: '1rem' }}>{team.email}</span>}
                    {team.slack_channel && <span>{team.slack_channel}</span>}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <button className="btn btn-secondary btn-sm" onClick={e => { e.stopPropagation(); setEditTeam(team); setShowTeamModal(true) }}>Edit</button>
                  <button className="btn btn-danger btn-sm" onClick={e => { e.stopPropagation(); setDeleteTarget(team) }}>Delete</button>
                  <span style={{ color: 'var(--text-muted)', fontSize: '12px', marginLeft: '0.5rem' }}>{expanded === team.id ? '▲' : '▼'}</span>
                </div>
              </div>

              {/* Contacts */}
              {expanded === team.id && (
                <div style={{ borderTop: '1px solid var(--border)', padding: '0.75rem 1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Contacts</span>
                    <button className="btn btn-secondary btn-sm" onClick={() => { setContactTeamId(team.id); setEditContact(null); setShowContactModal(true) }}>+ Contact</button>
                  </div>
                  {!contacts[team.id] ? (
                    <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Loading…</div>
                  ) : contacts[team.id].length === 0 ? (
                    <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No contacts.</div>
                  ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '0.5rem' }}>
                      {contacts[team.id].map(c => (
                        <div key={c.id} style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '0.625rem 0.75rem' }}>
                          <div style={{ fontWeight: 500, marginBottom: '2px' }}>{c.name}</div>
                          {c.role && <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{c.role}</div>}
                          {c.email && <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{c.email}</div>}
                          <div style={{ display: 'flex', gap: '0.375rem', marginTop: '0.5rem' }}>
                            <button className="btn btn-secondary btn-sm" style={{ fontSize: '11px', padding: '2px 8px' }}
                              onClick={() => { setEditContact(c); setContactTeamId(team.id); setShowContactModal(true) }}>Edit</button>
                            <button className="btn btn-danger btn-sm" style={{ fontSize: '11px', padding: '2px 8px' }}
                              onClick={() => handleDeleteContact(c).then(() => loadContacts(team.id))}>Del</button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showTeamModal && <TeamModal team={editTeam} onClose={() => setShowTeamModal(false)} onSaved={() => { setShowTeamModal(false); load() }} />}
      {showContactModal && <ContactModal teamId={contactTeamId} contact={editContact} onClose={() => setShowContactModal(false)} onSaved={() => { setShowContactModal(false); loadContacts(contactTeamId) }} />}
      {deleteTarget && (
        <ConfirmDialog
          title="Delete Team"
          message={`Delete "${deleteTarget.name}"?`}
          onConfirm={handleDeleteTeam}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  )
}
