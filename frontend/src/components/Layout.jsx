import { NavLink, Outlet, useLocation } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Dashboard', icon: '⊞' },
  { to: '/applications', label: 'Applications', icon: '◈' },
  { to: '/topology', label: 'Topology', icon: '⬡' },
  { to: '/servers', label: 'Servers', icon: '▣' },
  { to: '/environments', label: 'Environments', icon: '◎' },
  { to: '/teams', label: 'Teams', icon: '◉' },
  { to: '/audit', label: 'Audit Log', icon: '≡' },
]

const pageTitles = {
  '/': 'Dashboard',
  '/applications': 'Applications',
  '/topology': 'Topology',
  '/servers': 'Servers',
  '/environments': 'Environments',
  '/teams': 'Teams',
  '/audit': 'Audit Log',
}

export default function Layout() {
  const location = useLocation()
  const title = pageTitles[location.pathname] || 'CMDB'

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      <aside style={{
        width: 'var(--sidebar-width)',
        minWidth: 'var(--sidebar-width)',
        background: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}>
        {/* Logo */}
        <div style={{
          padding: '1.25rem 1.25rem 1rem',
          borderBottom: '1px solid var(--border)',
        }}>
          <span style={{
            fontSize: '18px',
            fontWeight: '700',
            color: 'var(--accent)',
            letterSpacing: '-0.02em',
          }}>CMDB</span>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
            Configuration Management
          </div>
        </div>

        {/* Nav */}
        <nav style={{ padding: '0.75rem 0', flex: 1 }}>
          {navItems.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '0.625rem',
                padding: '0.6rem 1.25rem',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                background: isActive ? 'var(--bg-hover)' : 'transparent',
                borderLeft: isActive ? '2px solid var(--accent)' : '2px solid transparent',
                textDecoration: 'none',
                fontSize: '13px',
                fontWeight: isActive ? '600' : '400',
                transition: 'all 0.15s',
              })}
            >
              <span style={{ fontSize: '14px', opacity: 0.8 }}>{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Top bar */}
        <header style={{
          height: '52px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 1.5rem',
          background: 'var(--bg-secondary)',
          flexShrink: 0,
        }}>
          <h1 style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-primary)' }}>{title}</h1>
        </header>

        {/* Page content */}
        <main style={{
          flex: 1,
          overflow: 'auto',
          padding: '1.5rem',
          background: 'var(--bg-primary)',
        }}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
