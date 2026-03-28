import api from './client'

// Applications
export const applications = {
  getAll: (params) => api.get('/api/applications', { params }),
  getById: (id) => api.get(`/api/applications/${id}`),
  create: (data) => api.post('/api/applications', data),
  update: (id, data) => api.put(`/api/applications/${id}`, data),
  remove: (id) => api.delete(`/api/applications/${id}`),
}

// Environments
export const environments = {
  getAll: () => api.get('/api/environments'),
  getById: (id) => api.get(`/api/environments/${id}`),
  create: (data) => api.post('/api/environments', data),
  update: (id, data) => api.put(`/api/environments/${id}`, data),
  remove: (id) => api.delete(`/api/environments/${id}`),
}

// Servers
export const servers = {
  getAll: () => api.get('/api/servers'),
  create: (data) => api.post('/api/servers', data),
  update: (id, data) => api.put(`/api/servers/${id}`, data),
  remove: (id) => api.delete(`/api/servers/${id}`),
}

// Teams
export const teams = {
  getAll: () => api.get('/api/teams'),
  create: (data) => api.post('/api/teams', data),
  update: (id, data) => api.put(`/api/teams/${id}`, data),
  remove: (id) => api.delete(`/api/teams/${id}`),
}

// Relationships
export const relationships = {
  getAll: (params) => api.get('/api/relationships', { params }),
  getById: (id) => api.get(`/api/relationships/${id}`),
  create: (data) => api.post('/api/relationships', data),
  update: (id, data) => api.put(`/api/relationships/${id}`, data),
  remove: (id) => api.delete(`/api/relationships/${id}`),
  getCiRelationships: (ciType, ciId) => api.get(`/api/ci/${ciType}/${ciId}/relationships`),
  getDependencyTree: (appId) => api.get(`/api/applications/${appId}/dependency-tree`),
  getImpact: (appId) => api.get(`/api/applications/${appId}/impact`),
}

// Audit
export const audit = {
  getAll: (params) => api.get('/api/audit', { params }),
}
