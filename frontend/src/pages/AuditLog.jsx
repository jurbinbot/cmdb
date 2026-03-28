import { useState, useEffect, useCallback } from 'react'
import { audit } from '../api/index'

const ACTION_BADGE = {
  create: 'badge-success',
  update: 'badge-info',
  delete: 'badge-danger',
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString()
}

function JsonDiff({ before, after }) {
  function fmt(obj) {
    if (!obj) return 'null'
    try {
      return JSON.stringify(typeof obj === 'string' ? JSON.parse(obj) : obj, null, 2)
    } catch {
      return String(obj)
    }
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '0.75rem' }}>
      <div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Before</div>
        <pre style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.75rem',
          fontSize: '11px',
          color: 'var(--danger)',
          overflow: 'auto',
          maxHeight: 200,
          whiteSpace: 'pre-wrap',
        }}>{fmt(before)}</pre>
      </div>
      <div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>After</div>
        <pre style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.75rem',
          fontSize: '11px',
          color: 'var(--success)',
          overflow: 'auto',
          maxHeight: 200,
          whiteSpace: 'pre-wrap',
        }}>{fmt(after)}</pre>
      </div>
    </div>
  )
}

export default function AuditLog() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const PAGE_SIZE = 25

  const [filterType, setFilterType] = useState('')
  const [filterAction, setFilterAction] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = { skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE }
      if (filterType) params.ci_type = filterType
      if (filterAction) params.action = filterAction
      if (dateFrom) params.date_from = dateFrom
      if (dateTo) params.date_to = dateTo
      const res = await audit.getAll(params)
      const items = Array.isArray(res.data) ? res.data : (res.data.items || [])
      setData(items)
      setTotal(res.data.total || items.length)
    } catch { setData([]) }
    finally { setLoading(false) }
  }, [page, filterType, filterAction, dateFrom, dateTo])

  useEffect(() => { setPage(1) }, [filterType, filterAction, dateFrom, dateTo])
  useEffect(() => { load() }, [load])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  const ciTypes = ['application', 'server', 'environment', 'team', 'contact', 'deployment', 'endpoint', 'database']

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Audit Log</h2>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <select className="select" style={{ maxWidth: 180 }} value={filterType} onChange={e => setFilterType(e.target.value)}>
          <option value="">All CI Types</option>
          {ciTypes.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <select className="select" style={{ maxWidth: 160 }} value={filterAction} onChange={e => setFilterAction(e.target.value)}>
          <option value="">All Actions</option>
          <option value="create">Create</option>
          <option value="update">Update</option>
          <option value="delete">Delete</option>
        </select>
        <input type="date" className="input" style={{ maxWidth: 180 }} value={dateFrom} onChange={e => setDateFrom(e.target.value)} title="From date" />
        <input type="date" className="input" style={{ maxWidth: 180 }} value={dateTo} onChange={e => setDateTo(e.target.value)} title="To date" />
        {(filterType || filterAction || dateFrom || dateTo) && (
          <button className="btn btn-secondary" onClick={() => { setFilterType(''); setFilterAction(''); setDateFrom(''); setDateTo('') }}>Clear</button>
        )}
      </div>

      <div className="card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}><div className="spinner" style={{ margin: 'auto' }} /></div>
        ) : data.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No audit events found.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>CI Type</th>
                <th>CI ID</th>
                <th>Action</th>
                <th>Changed By</th>
                <th>Timestamp</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.map(e => (
                <>
                  <tr key={e.id} onClick={() => setExpanded(expanded === e.id ? null : e.id)} style={{ cursor: 'pointer' }}>
                    <td><span className="badge badge-gray">{e.ci_type}</span></td>
                    <td style={{ fontFamily: 'monospace', fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {String(e.ci_id).slice(0, 8)}…
                    </td>
                    <td>
                      <span className={`badge ${ACTION_BADGE[e.action] || 'badge-gray'}`}>{e.action}</span>
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>{e.changed_by || '—'}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{fmtDate(e.changed_at)}</td>
                    <td style={{ color: 'var(--text-muted)' }}>{expanded === e.id ? '▲' : '▼'}</td>
                  </tr>
                  {expanded === e.id && (
                    <tr key={`${e.id}-detail`}>
                      <td colSpan={6} style={{ background: 'var(--bg-secondary)', padding: '0.75rem 1rem' }}>
                        <JsonDiff before={e.before_json} after={e.after_json} />
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1rem' }}>
          <button className="btn btn-secondary btn-sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
          <span style={{ padding: '0.3rem 0.75rem', color: 'var(--text-secondary)', fontSize: '13px' }}>
            Page {page} of {totalPages}
          </span>
          <button className="btn btn-secondary btn-sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Next →</button>
        </div>
      )}
    </div>
  )
}
