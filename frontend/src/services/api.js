import axios from 'axios'

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
export const API_BASE_URL = rawBaseUrl.replace(/\/$/, '')
const API_V1_BASE_URL = `${API_BASE_URL}/api/v1`

const api = axios.create({
  baseURL: API_V1_BASE_URL,
  timeout: 60000,
})

const getErrorMessage = (error, fallback = 'Something went wrong while contacting the backend.') => {
  if (axios.isAxiosError(error)) {
    return (
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      fallback
    )
  }
  return fallback
}

api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(new Error(getErrorMessage(error)))
)

export const systemApi = {
  async getHealth() {
    const response = await axios.get(`${API_BASE_URL}/health`, { timeout: 10000 })
    return response.data
  },
  async getDatabaseHealth() {
    const response = await axios.get(`${API_BASE_URL}/health/db`, { timeout: 10000 })
    return response.data
  },
}

export const documentsApi = {
  async list() {
    const response = await api.get('/documents')
    return response.data
  },
  async get(documentId) {
    const response = await api.get(`/documents/${documentId}`)
    return response.data
  },
  async upload(formData, onUploadProgress) {
    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress,
    })
    return response.data
  },
  async process(documentId) {
    const response = await api.post(`/documents/${documentId}/process`)
    return response.data
  },
  async getSummary(documentId) {
    const response = await api.get(`/documents/${documentId}/summary`)
    return response.data
  },
  async getMetadata(documentId) {
    const response = await api.get(`/documents/${documentId}/metadata`)
    return response.data
  },
  async getChunks(documentId) {
    const response = await api.get(`/documents/${documentId}/chunks`)
    return response.data
  },
  async getLogs(documentId) {
    const response = await api.get(`/documents/${documentId}/logs`)
    return response.data
  },
}

export const dashboardApi = {
  async getMetrics() {
    const response = await api.get('/dashboard/metrics')
    return response.data
  },
  async getRecentActivity() {
    const response = await api.get('/dashboard/recent-activity')
    return response.data
  },
}

export const searchApi = {
  async semanticSearch(payload) {
    const response = await api.post('/search', payload)
    return response.data
  },
}

export const qaApi = {
  async askQuestion(payload) {
    const response = await api.post('/qa', payload)
    return response.data
  },
}

export { getErrorMessage }
export default api
