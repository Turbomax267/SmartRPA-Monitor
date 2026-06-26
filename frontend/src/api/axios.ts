import axios from 'axios'
import { getStoredToken } from '../utils/storage'

function resolveApiBaseUrl() {
  const configuredUrl = import.meta.env.VITE_API_URL

  if (configuredUrl) {
    return configuredUrl
  }

  if (typeof window !== 'undefined') {
    const { hostname, origin } = window.location

    if (hostname.includes('onrender.com')) {
      if (hostname.includes('frontend')) {
        return `${origin.replace('frontend', 'backend')}/api`
      }

      if (hostname.includes('front')) {
        return `${origin.replace('front', 'back')}/api`
      }
    }
  }

  return 'http://localhost:8000/api'
}

export const api = axios.create({
  baseURL: resolveApiBaseUrl(),
  timeout: 15000,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = getStoredToken()

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }

    return Promise.reject(error)
  },
)
