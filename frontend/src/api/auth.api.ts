import { api } from './axios'
import type { ApiResponse, AuthPayload, LoginFormValues, User } from '../interfaces'

export async function loginRequest(payload: LoginFormValues) {
  const { data } = await api.post<ApiResponse<AuthPayload>>('/auth/login', payload)
  return data
}

export async function meRequest() {
  const { data } = await api.get<ApiResponse<User>>('/auth/me')
  return data
}

export async function logoutRequest() {
  const { data } = await api.post<ApiResponse<null>>('/auth/logout')
  return data
}
