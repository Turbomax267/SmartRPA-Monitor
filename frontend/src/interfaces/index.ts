export interface ApiResponse<T> {
  success: boolean
  message: string
  data: T
  errors?: Record<string, string[]>
}

export interface Role {
  id: number
  name: string
  display_name: string
}

export interface User {
  id: number
  name: string
  email: string
  status: string
  role?: Role
}

export interface AuthPayload {
  token: string
  token_type: string
  user: User
}

export interface LoginFormValues {
  email: string
  password: string
}

export interface DashboardChartPoint {
  day?: string
  total: number
  category?: string
}

export interface LatestExecution {
  id: number
  rpa: string | null
  process: string | null
  status: string
  duration_ms: number | null
  responsible: string | null
  started_at: string | null
}

export interface DashboardSummary {
  total_rpas: number
  active_rpas: number
  inactive_rpas: number
  under_review_rpas: number
  total_executions: number
  success_rate: number
  detected_errors: number
  average_duration_ms: number
  executions_by_day: DashboardChartPoint[]
  errors_by_category: DashboardChartPoint[]
  latest_executions: LatestExecution[]
}
