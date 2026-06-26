import { api } from './axios'
import type { ApiResponse } from '../interfaces'

export interface MonitorListItem {
  [key: string]: unknown
}

export interface AnalysisLogLine {
  time: string
  level: 'INFO' | 'WARNING' | 'ERROR' | string
  step: string
  message: string
}

export interface SimilarCase {
  date: string
  errorType: string
  match: number
}

export interface AnalysisDetail {
  executionId: string | number
  executionCode: string
  rpaName: string
  process: string
  analyzedAt: string
  agent: string
  incidentId?: string | null
  executionStatus: string
  preliminaryError: string
  sanitizedLog: AnalysisLogLine[]
  classification: string
  probableCause: string
  recommendation: string[]
  confidence: number
  model: string
  durationSeconds: number
  reviewedPatterns: number
  responsible: string
  similarCases: SimilarCase[]
}

export interface ExecutionIncident {
  id: string | number
  code: string
  severity: string
  status: string
  category?: string
  probableCause?: string
}

export interface ExecutionLogItem {
  time: string
  level: 'INFO' | 'WARNING' | 'ERROR' | string
  step: string
  message: string
}

export interface ExecutionDetail {
  id: string | number
  publicCode: string
  rpaName: string
  process: string
  agent: string
  responsible: string
  triggerType: string
  scenario: string
  durationLabel: string
  totalItems: number
  successItems: number
  failedItems: number
  errorType: string
  errorCode?: string | null
  errorMessage?: string | null
  summary: string
  incidentId?: string | number
  incident?: ExecutionIncident | null
  analysisId?: string | number
  logs: ExecutionLogItem[]
}

export interface IncidentTimelineStep {
  at: string
  user: string
  action: 'ASSIGNMENT' | 'COMMENT' | 'TECHNICAL_ACTION' | 'RESOLUTION' | string
  comment: string
}

export interface IncidentDetail {
  id: string | number
  code: string
  title: string
  category: string
  rpaName: string
  executionCode: string
  executionId: string | number
  responsible: string
  detectedAt: string
  updatedAt: string
  description: string
  probableCause: string
  resolution?: string | null
  analysisId?: string | number
  timeline: IncidentTimelineStep[]
}

export interface RpaExecutionSummary {
  id: string | number
  publicCode: string
  status: 'SUCCESS' | 'FAILED' | 'REVIEW' | string
  durationLabel: string
  responsible: string
  dateLabel: string
}

export interface RpaIncidentBreakdownItem {
  label: string
  total: number
  percent: number
  tone: 'red' | 'amber' | 'yellow' | 'slate' | string
}

export interface RpaRecentHistoryItem {
  label: string
  status: 'SUCCESS' | 'FAILED' | string
  duration: string
  result: string
}

export interface RpaInfoItem {
  label: string
  value: string
}

export interface RpaStats {
  successfulExecutions: number
  incidents: number
  averageMinutes: number
  successRate: number
}

export interface RpaDetail {
  id: string | number
  code: string
  name: string
  processName: string
  responsible: string
  scriptName: string
  executionMode: string
  assignedAgent: string
  lastExecutionLabel: string
  uptime: number
  environment: string
  nextExecution: string
  frequency: string
  sinceLastRun: string
  stats: RpaStats
  incidentBreakdown: RpaIncidentBreakdownItem[]
  recentHistory: RpaRecentHistoryItem[]
  technicalInfo: RpaInfoItem[]
  configurationInfo: RpaInfoItem[]
  executions?: RpaExecutionSummary[]
}

export async function listRpasRequest() {
  const { data } = await api.get<ApiResponse<MonitorListItem[]>>('/rpas')
  return data
}

export async function getRpaRequest(rpaId: string) {
  const { data } = await api.get<ApiResponse<RpaDetail>>(`/rpas/${rpaId}`)
  return data
}

export async function listExecutionsRequest() {
  const { data } = await api.get<ApiResponse<MonitorListItem[]>>('/executions')
  return data
}

export async function getExecutionRequest(executionId: string) {
  const { data } = await api.get<ApiResponse<ExecutionDetail>>(`/executions/${executionId}`)
  return data
}

export async function listIncidentsRequest() {
  const { data } = await api.get<ApiResponse<MonitorListItem[]>>('/incidents')
  return data
}

export async function getIncidentRequest(incidentId: string) {
  const { data } = await api.get<ApiResponse<IncidentDetail>>(`/incidents/${incidentId}`)
  return data
}

export async function getAnalysisRequest(analysisId: string) {
  const { data } = await api.get<ApiResponse<AnalysisDetail>>(`/ai-analyses/${analysisId}`)
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
