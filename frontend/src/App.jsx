import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Applications from './pages/Applications'
import AppDetail from './pages/AppDetail'
import Servers from './pages/Servers'
import Environments from './pages/Environments'
import Teams from './pages/Teams'
import AuditLog from './pages/AuditLog'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="applications" element={<Applications />} />
          <Route path="applications/:id" element={<AppDetail />} />
          <Route path="servers" element={<Servers />} />
          <Route path="environments" element={<Environments />} />
          <Route path="teams" element={<Teams />} />
          <Route path="audit" element={<AuditLog />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
