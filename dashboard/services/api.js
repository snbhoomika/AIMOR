import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const getImageUrl = (imagePath) => {
  if (!imagePath) return null;
  if (imagePath.startsWith('data:')) return imagePath;
  if (imagePath.startsWith('http')) return imagePath;
  return `${BASE_URL}${imagePath}`;
};

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  register: (data) => api.post('/auth/register', data),
  login: (email, password) => api.post('/auth/login', { email, password }),
  getMe: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/me', data),
  changePassword: (data) => api.post('/auth/change-password', data),
};

export const lostItemsService = {
  getAll: (params) => api.get('/lost-items/', { params }),
  getMy: (params) => api.get('/lost-items/my', { params }),
  getById: (id) => api.get(`/lost-items/${id}`),
  create: (formData) => api.post('/lost-items/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  update: (id, formData) => api.put(`/lost-items/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (id) => api.delete(`/lost-items/${id}`),
  markReturned: (id) => api.post(`/lost-items/${id}/mark-returned`),
};

export const foundItemsService = {
  getAll: (params) => api.get('/found-items/', { params }),
  getMy: (params) => api.get('/found-items/my', { params }),
  getById: (id) => api.get(`/found-items/${id}`),
  create: (formData) => api.post('/found-items/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  update: (id, formData) => api.put(`/found-items/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (id) => api.delete(`/found-items/${id}`),
  verify: (id) => api.post(`/found-items/${id}/verify`),
};

export const searchService = {
  byImage: (formData) => api.post('/search/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  byText: (params) => api.get('/search/text', { params }),
  nearby: (params) => api.get('/search/nearby', { params }),
  getMatches: (itemId, params) => api.get(`/search/matches/${itemId}`, { params }),
  getCategories: () => api.get('/search/categories'),
};

export const claimsService = {
  create: (data) => api.post('/claims/', data),
  getMyClaims: (params) => api.get('/claims/my-claims', { params }),
  getIncoming: (params) => api.get('/claims/incoming', { params }),
  getById: (id) => api.get(`/claims/${id}`),
  accept: (id, data) => api.put(`/claims/${id}/accept`, data),
  reject: (id, data) => api.put(`/claims/${id}/reject`, data),
  complete: (id) => api.put(`/claims/${id}/complete`),
};

export const notificationsService = {
  getAll: (params) => api.get('/notifications/', { params }),
  getUnreadCount: () => api.get('/notifications/unread-count'),
  markAsRead: (id) => api.put(`/notifications/${id}/read`),
  markAllAsRead: () => api.put('/notifications/read-all'),
  delete: (id) => api.delete(`/notifications/${id}`),
  clearAll: () => api.delete('/notifications/clear-all'),
};

export default api;
