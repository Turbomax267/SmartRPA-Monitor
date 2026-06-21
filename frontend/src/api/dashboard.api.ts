import { api } from './axios'
import type { ApiResponse, DashboardSummary } from '../interfaces'

export async function dashboardSummaryRequest() {
  const { data } = await api.get<ApiResponse<DashboardSummary>>('/dashboard/summary')
  return data
}
