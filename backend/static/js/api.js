// PostMate API Client
const API = (() => {
  const BASE = '';

  function getToken() {
    return localStorage.getItem('token');
  }

  function headers() {
    const h = { 'Content-Type': 'application/json' };
    const token = getToken();
    if (token) h['Authorization'] = `Bearer ${token}`;
    return h;
  }

  async function request(method, path, body) {
    const res = await fetch(`${BASE}${path}`, {
      method,
      headers: headers(),
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Request failed');
    return data;
  }

  return {
    // Auth
    register: (email, password, inviteCode) =>
      request('POST', '/api/auth/register', { email, password, invite_code: inviteCode }),
    login: (email, password) =>
      request('POST', '/api/auth/login', { email, password }),
    me: () => request('GET', '/api/auth/me'),

    // Brand
    createBrand: (data) => request('POST', '/api/brands', data),
    getBrand: () => request('GET', '/api/brands/me'),

    // Posts
    getPosts: (week) => request('GET', `/api/posts${week ? `?week=${week}` : ''}`),
    approvePost: (id) => request('PUT', `/api/posts/${id}/approve`),
    regeneratePost: (id) => request('PUT', `/api/posts/${id}/regenerate`),

    // Generate
    generate: () => request('POST', '/api/generate'),
    generationStatus: () => request('GET', '/api/generate/status'),

    // Invites (admin)
    createInvite: (email) => request('POST', '/api/invites', { email, count: 1 }),
    listInvites: () => request('GET', '/api/invites'),
    validateInvite: (code) => request('GET', `/api/invites/validate/${encodeURIComponent(code)}`),
  };
})();
