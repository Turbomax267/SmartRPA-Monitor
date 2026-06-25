import { api } from './axios'
import type { ApiResponse } from '../interfaces'

export async function listRpasRequest() {
  const { data } = await api.get<ApiResponse<any[]>>('/rpas')
  return data
}

export async function getRpaRequest(rpaId: string) {
  const { data } = await api.get<ApiResponse<any>>(`/rpas/${rpaId}`)
  return data
}

export async function listExecutionsRequest() {
  const { data } = await api.get<ApiResponse<any[]>>('/executions')
  return data
}

export async function getExecutionRequest(executionId: string) {
  const { data } = await api.get<ApiResponse<any>>(`/executions/${executionId}`)
  return data
}

export async function listIncidentsRequest() {
  const { data } = await api.get<ApiResponse<any[]>>('/incidents')
  return data
}

export async function getIncidentRequest(incidentId: string) {
  const { data } = await api.get<ApiResponse<any>>(`/incidents/${incidentId}`)
  return data
}

export async function getAnalysisRequest(analysisId: string) {
  const { data } = await api.get<ApiResponse<any>>(`/ai-analyses/${analysisId}`)
  return data
}

export async function metricsSummaryRequest() {
  const { data } = await api.get<ApiResponse<any>>('/metrics/summary')
  return data
}

export async function usersRequest() {
  const { data } = await api.get<ApiResponse<any>>('/users')
  return data
}

export async function createJobRequest(payload: { rpa_id: string | number; agent_id?: string | number; command: 'run' | 'activate' | 'deactivate'; payload?: Record<string, unknown> }) {
  const { data } = await api.post<ApiResponse<any>>('/jobs', payload)
  return data
}

export async function listJobsRequest() {
  const { data } = await api.get<ApiResponse<any[]>>('/jobs')
  return data
}
