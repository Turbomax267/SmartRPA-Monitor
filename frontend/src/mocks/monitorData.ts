export type RoleKey = 'ADMIN' | 'TECH' | 'MANAGER'
export type UserStatus = 'ACTIVE' | 'INACTIVE'
export type RpaStatus = 'ACTIVE' | 'UNDER_REVIEW' | 'INACTIVE' | 'ERROR'
export type ExecutionStatus = 'SUCCESS' | 'FAILED' | 'REVIEW'
export type IncidentStatus = 'PENDING' | 'IN_REVIEW' | 'RESOLVED' | 'OBSERVED'
export type Severity = 'HIGH' | 'MEDIUM' | 'LOW'

export interface RoleCard {
  id: RoleKey
  title: string
  short: string
  description: string
  accent: 'navy' | 'blue' | 'green'
  permissions: string[]
}

export interface MonitorUserRecord {
  id: string
  firstName: string
  lastName: string
  name: string
  username: string
  email: string
  area: string
  position: string
  phone?: string
  initials: string
  role: RoleKey
  status: UserStatus
  lastAccess: string
  notifyByEmail: boolean
}

export interface TimelineEvent {
  at: string
  user: string
  action: string
  comment: string
}

export interface ExecutionLogLine {
  time: string
  level: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  step: string
  message: string
}

export interface ExecutionRecord {
  id: string
  publicCode: string
  rpaId: string
  rpaName: string
  process: string
  status: ExecutionStatus
  result: string
  responsible: string
  dateLabel: string
  timeLabel: string
  durationLabel: string
  durationMs: number
  triggerType: string
  scenario: string
  totalItems: number
  successItems: number
  failedItems: number
  errorType: string
  errorCode?: string
  errorMessage?: string
  summary: string
  agent: string
  incidentId?: string
  analysisId?: string
  logs: ExecutionLogLine[]
}

export interface IncidentRecord {
  id: string
  code: string
  title: string
  rpaId: string
  rpaName: string
  executionId: string
  executionCode: string
  category: string
  severity: Severity
  status: IncidentStatus
  responsible: string
  detectedAt: string
  updatedAt: string
  description: string
  probableCause: string
  resolution?: string
  analysisId?: string
  timeline: TimelineEvent[]
}

export interface SimilarAnalysis {
  date: string
  errorType: string
  match: number
}

export interface AnalysisRecord {
  id: string
  executionId: string
  executionCode: string
  incidentId?: string
  rpaName: string
  process: string
  agent: string
  executionStatus: string
  preliminaryError: string
  classification: string
  confidence: number
  probableCause: string
  recommendation: string[]
  provider: string
  model: string
  analyzedAt: string
  reviewedPatterns: number
  durationSeconds: number
  relatedIncidentStatus?: string
  relatedIncidentSeverity?: string
  responsible?: string
  sanitizedLog: ExecutionLogLine[]
  similarCases: SimilarAnalysis[]
}

export interface RpaRecord {
  id: string
  code: string
  name: string
  processName: string
  responsible: string
  scriptName: string
  lifecycleStatus: RpaStatus
  lastExecutionLabel: string
  executionMode: string
  environment: string
  assignedAgent: string
  uptime: number
  nextExecution: string
  frequency: string
  sinceLastRun: string
  stats: {
    successfulExecutions: number
    incidents: number
    averageMinutes: number
    successRate: number
  }
  incidentBreakdown: { label: string; total: number; percent: number; tone: 'red' | 'amber' | 'yellow' | 'slate' }[]
  recentHistory: { label: string; status: ExecutionStatus; duration: string; result: string }[]
  technicalInfo: Array<{ label: string; value: string }>
  configurationInfo: Array<{ label: string; value: string }>
}

export const roleCards: RoleCard[] = [
  {
    id: 'ADMIN',
    title: 'Administrador',
    short: 'AD',
    description: 'Permisos asignados:',
    accent: 'navy',
    permissions: [
      'Gestionar usuarios y bots',
      'Configuracion del sistema',
      'Acceso total a metricas',
      'Ver todos los logs',
      'Gestionar alertas',
    ],
  },
  {
    id: 'TECH',
    title: 'Equipo Tecnico',
    short: 'EQ',
    description: 'Permisos asignados:',
    accent: 'blue',
    permissions: [
      'Revisar logs tecnicos',
      'Gestionar alertas',
      'Analisis con IA',
      'Metricas y reportes',
      'Ver ejecuciones',
    ],
  },
  {
    id: 'MANAGER',
    title: 'Resp. de Proceso',
    short: 'RE',
    description: 'Permisos asignados:',
    accent: 'green',
    permissions: [
      'Consultar bots de su area',
      'Ver estado y alertas propias',
      'Seguimiento de ejecuciones',
      'Reportes basicos',
      'Dashboard general',
    ],
  },
]

export const monitorUsers: MonitorUserRecord[] = [
  {
    id: 'usr-admin',
    firstName: 'Carlos',
    lastName: 'Mendoza',
    name: 'Carlos Mendoza',
    username: 'admin',
    email: 'admin@empresa.com',
    area: 'TI',
    position: 'Administrador de Plataforma',
    phone: '+51 998 110 320',
    initials: 'AD',
    role: 'ADMIN',
    status: 'ACTIVE',
    lastAccess: 'Hoy 09:30',
    notifyByEmail: true,
  },
  {
    id: 'usr-tech-1',
    firstName: 'Juan',
    lastName: 'Rodriguez',
    name: 'Juan Rodriguez',
    username: 'tecnico',
    email: 'tecnico@empresa.com',
    area: 'RPA',
    position: 'Analista RPA',
    phone: '+51 977 120 450',
    initials: 'JR',
    role: 'TECH',
    status: 'ACTIVE',
    lastAccess: 'Hoy 08:15',
    notifyByEmail: true,
  },
  {
    id: 'usr-manager-1',
    firstName: 'Maria',
    lastName: 'Torres',
    name: 'Maria Torres',
    username: 'responsable',
    email: 'responsable@empresa.com',
    area: 'Academico',
    position: 'Responsable de Proceso',
    initials: 'MT',
    role: 'MANAGER',
    status: 'ACTIVE',
    lastAccess: 'Ayer 17:30',
    notifyByEmail: true,
  },
  {
    id: 'usr-tech-2',
    firstName: 'Ana',
    lastName: 'Garcia',
    name: 'Ana Garcia',
    username: 'tecnico2',
    email: 'tecnico2@empresa.com',
    area: 'RPA',
    position: 'Soporte RPA',
    initials: 'AG',
    role: 'TECH',
    status: 'ACTIVE',
    lastAccess: 'Ayer 16:00',
    notifyByEmail: true,
  },
  {
    id: 'usr-manager-2',
    firstName: 'Carlos',
    lastName: 'Lopez',
    name: 'Carlos Lopez',
    username: 'resp2',
    email: 'resp2@empresa.com',
    area: 'Logistica',
    position: 'Lider de Logistica',
    initials: 'CL',
    role: 'MANAGER',
    status: 'ACTIVE',
    lastAccess: 'Ayer 14:00',
    notifyByEmail: false,
  },
  {
    id: 'usr-tech-3',
    firstName: 'Roberto',
    lastName: 'Silva',
    name: 'Roberto Silva',
    username: 'tecnico3',
    email: 'tecnico3@empresa.com',
    area: 'RPA',
    position: 'Monitor RPA',
    initials: 'RS',
    role: 'TECH',
    status: 'INACTIVE',
    lastAccess: 'Hace 2d',
    notifyByEmail: false,
  },
  {
    id: 'usr-manager-3',
    firstName: 'Patricia',
    lastName: 'Mendez',
    name: 'Patricia Mendez',
    username: 'resp3',
    email: 'resp3@empresa.com',
    area: 'Finanzas',
    position: 'Lider de Finanzas',
    initials: 'PM',
    role: 'MANAGER',
    status: 'ACTIVE',
    lastAccess: 'Hace 2d',
    notifyByEmail: true,
  },
  {
    id: 'usr-admin-2',
    firstName: 'Luis',
    lastName: 'Vargas',
    name: 'Luis Vargas',
    username: 'admin2',
    email: 'admin2@empresa.com',
    area: 'TI',
    position: 'Coordinador TI',
    initials: 'LV',
    role: 'ADMIN',
    status: 'ACTIVE',
    lastAccess: 'Hace 3d',
    notifyByEmail: true,
  },
]

export const rpaCatalog: RpaRecord[] = [
  {
    id: 'rpa-registro',
    code: 'RPA-RR-001',
    name: 'RPA Registro Resultados',
    processName: 'Registro de Resultados Academicos',
    responsible: 'Maria Rodriguez',
    scriptName: 'RPA_Registro_Resultados.py',
    lifecycleStatus: 'ACTIVE',
    lastExecutionLabel: 'Hoy, 09:42 AM',
    executionMode: 'Programado',
    environment: 'Produccion',
    assignedAgent: 'AGT-PROD-02',
    uptime: 96.8,
    nextExecution: 'Hoy, 18:00',
    frequency: 'Diaria - 09:00 y 18:00',
    sinceLastRun: '1h 42m',
    stats: {
      successfulExecutions: 1192,
      incidents: 56,
      averageMinutes: 4.2,
      successRate: 95.3,
    },
    incidentBreakdown: [
      { label: 'Timeout en SAP', total: 38, percent: 40, tone: 'red' },
      { label: 'Error de validacion de datos', total: 12, percent: 22, tone: 'amber' },
      { label: 'Elemento no hallado', total: 6, percent: 13, tone: 'yellow' },
      { label: 'Fallo conexion BD', total: 4, percent: 9, tone: 'red' },
      { label: 'Otros', total: 9, percent: 16, tone: 'slate' },
    ],
    recentHistory: [
      { label: 'Hoy, 09:42 AM', status: 'SUCCESS', duration: '4m 12s', result: 'OK' },
      { label: 'Hoy, 06:00 AM', status: 'SUCCESS', duration: '3m 58s', result: 'OK' },
      { label: 'Ayer, 18:00 PM', status: 'FAILED', duration: '1m 03s', result: 'Timeout SAP' },
      { label: 'Ayer, 09:00 AM', status: 'SUCCESS', duration: '4m 22s', result: 'OK' },
      { label: 'Hace 2d, 18:00 PM', status: 'SUCCESS', duration: '4m 05s', result: 'OK' },
    ],
    technicalInfo: [
      { label: 'Script', value: 'RPA_Registro_Resultados.py' },
      { label: 'Version del script', value: '1.5.3' },
      { label: 'Agente', value: 'AGT-PROD-02 (Windows 10, v2.4.1)' },
      { label: 'Ultima sincronizacion', value: 'Hoy, 09:41 AM' },
      { label: 'Entorno', value: 'Produccion' },
    ],
    configurationInfo: [
      { label: 'Modo de ejecucion', value: 'Programado' },
      { label: 'Frecuencia', value: 'Diaria (09:00 y 18:00)' },
      { label: 'Reintentos', value: '2 reintentos' },
      { label: 'Notificaciones', value: 'En caso de fallo' },
      { label: 'Propietario', value: 'Maria Rodriguez' },
    ],
  },
  {
    id: 'rpa-certificados',
    code: 'RPA-GC-002',
    name: 'RPA Gen. Certificados',
    processName: 'Certificaciones',
    responsible: 'Equipo Tecnico',
    scriptName: 'gen_certificados_v2.py',
    lifecycleStatus: 'ACTIVE',
    lastExecutionLabel: '03/06/2026 10:30',
    executionMode: 'Programado',
    environment: 'Produccion',
    assignedAgent: 'AGT-PROD-01',
    uptime: 99.1,
    nextExecution: 'Hoy, 17:00',
    frequency: 'Lunes a viernes',
    sinceLastRun: '4h 10m',
    stats: { successfulExecutions: 984, incidents: 12, averageMinutes: 2.8, successRate: 97.8 },
    incidentBreakdown: [
      { label: 'Timeout', total: 5, percent: 32, tone: 'red' },
      { label: 'Conexion', total: 4, percent: 24, tone: 'amber' },
      { label: 'Datos', total: 3, percent: 18, tone: 'yellow' },
    ],
    recentHistory: [
      { label: 'Hoy, 10:10 AM', status: 'SUCCESS', duration: '2m 10s', result: 'OK' },
      { label: 'Ayer, 17:00 PM', status: 'SUCCESS', duration: '2m 22s', result: 'OK' },
    ],
    technicalInfo: [],
    configurationInfo: [],
  },
  {
    id: 'rpa-publicacion',
    code: 'RPA-PC-003',
    name: 'RPA Pub. Certificados',
    processName: 'Certificaciones',
    responsible: 'Equipo Tecnico',
    scriptName: 'pub_certificados_v1.py',
    lifecycleStatus: 'ACTIVE',
    lastExecutionLabel: '03/06/2026 09:15',
    executionMode: 'Programado',
    environment: 'Produccion',
    assignedAgent: 'AGT-PROD-03',
    uptime: 97.2,
    nextExecution: 'Hoy, 15:00',
    frequency: 'Cada 4 horas',
    sinceLastRun: '2h 14m',
    stats: { successfulExecutions: 754, incidents: 9, averageMinutes: 3.1, successRate: 96.4 },
    incidentBreakdown: [],
    recentHistory: [],
    technicalInfo: [],
    configurationInfo: [],
  },
  {
    id: 'rpa-fechas',
    code: 'RPA-CF-004',
    name: 'RPA Cambio de Fechas',
    processName: 'Configuracion',
    responsible: 'J. Rodriguez',
    scriptName: 'cambio_fechas_v1.py',
    lifecycleStatus: 'INACTIVE',
    lastExecutionLabel: '01/06/2026 11:00',
    executionMode: 'Manual',
    environment: 'QA',
    assignedAgent: 'AGT-QA-02',
    uptime: 0,
    nextExecution: 'Sin programar',
    frequency: 'Bajo demanda',
    sinceLastRun: '5 dias',
    stats: { successfulExecutions: 132, incidents: 4, averageMinutes: 1.8, successRate: 91.2 },
    incidentBreakdown: [],
    recentHistory: [],
    technicalInfo: [],
    configurationInfo: [],
  },
  {
    id: 'rpa-evaluaciones',
    code: 'RPA-CE-005',
    name: 'RPA Creacion Evaluaciones',
    processName: 'Evaluaciones',
    responsible: 'M. Torres',
    scriptName: 'crear_evaluaciones_v2.py',
    lifecycleStatus: 'ACTIVE',
    lastExecutionLabel: '03/06/2026 08:30',
    executionMode: 'Programado',
    environment: 'Produccion',
    assignedAgent: 'AGT-PROD-03',
    uptime: 98.1,
    nextExecution: 'Hoy, 22:00',
    frequency: 'Diaria',
    sinceLastRun: '3h 02m',
    stats: { successfulExecutions: 612, incidents: 15, averageMinutes: 5.1, successRate: 92.6 },
    incidentBreakdown: [],
    recentHistory: [],
    technicalInfo: [],
    configurationInfo: [],
  },
  {
    id: 'rpa-sync-erp',
    code: 'RPA-SE-006',
    name: 'Bot_Sync_ERP',
    processName: 'TI',
    responsible: 'R. Silva',
    scriptName: 'sync_erp_v4.py',
    lifecycleStatus: 'ERROR',
    lastExecutionLabel: 'Hace 3 dias',
    executionMode: 'Programado',
    environment: 'Produccion',
    assignedAgent: 'AGT-PROD-04',
    uptime: 72.4,
    nextExecution: 'Suspendido',
    frequency: 'Cada 3 horas',
    sinceLastRun: '3 dias',
    stats: { successfulExecutions: 420, incidents: 22, averageMinutes: 4.9, successRate: 84.5 },
    incidentBreakdown: [],
    recentHistory: [],
    technicalInfo: [],
    configurationInfo: [],
  },
  {
    id: 'rpa-alertas',
    code: 'RPA-AF-007',
    name: 'Bot_Alertas_Fraude',
    processName: 'Seguridad',
    responsible: 'P. Mendez',
    scriptName: 'alertas_fraude_v2.py',
    lifecycleStatus: 'ACTIVE',
    lastExecutionLabel: 'Hace 4 dias',
    executionMode: 'Programado',
    environment: 'Produccion',
    assignedAgent: 'AGT-PROD-05',
    uptime: 98.7,
    nextExecution: 'Hoy, 16:00',
    frequency: 'Cada 2 horas',
    sinceLastRun: '1h 11m',
    stats: { successfulExecutions: 845, incidents: 17, averageMinutes: 2.4, successRate: 96.8 },
    incidentBreakdown: [],
    recentHistory: [],
    technicalInfo: [],
    configurationInfo: [],
  },
  {
    id: 'rpa-reportes',
    code: 'RPA-RH-008',
    name: 'Bot_Reportes_RRHH',
    processName: 'RRHH',
    responsible: 'A. Garcia',
    scriptName: 'reportes_rrhh_v1.py',
    lifecycleStatus: 'ACTIVE',
    lastExecutionLabel: 'Hoy 09:15',
    executionMode: 'Programado',
    environment: 'Produccion',
    assignedAgent: 'AGT-PROD-06',
    uptime: 97.9,
    nextExecution: 'Hoy, 18:30',
    frequency: 'Diaria',
    sinceLastRun: '42m',
    stats: { successfulExecutions: 703, incidents: 8, averageMinutes: 2.6, successRate: 97.1 },
    incidentBreakdown: [],
    recentHistory: [],
    technicalInfo: [],
    configurationInfo: [],
  },
]

export const executionCatalog: ExecutionRecord[] = [
  {
    id: 'ex-247',
    publicCode: 'EX-247',
    rpaId: 'rpa-registro',
    rpaName: 'RPA Registro Resultados',
    process: 'Resultados Academicos',
    status: 'FAILED',
    result: 'Error SAP',
    responsible: 'J. Rodriguez',
    dateLabel: 'Hoy',
    timeLabel: '09:42',
    durationLabel: '1m 08s',
    durationMs: 68000,
    triggerType: 'Manual',
    scenario: 'Campo requerido vacio',
    totalItems: 18,
    successItems: 12,
    failedItems: 6,
    errorType: 'Datos',
    errorCode: 'DATA_VALIDATION',
    errorMessage: 'Campo requerido vacio en formulario de registro',
    summary:
      'El bot RPA Registro Resultados proceso 18 registros. La ejecucion se detuvo al detectar valores invalidos o incompletos antes del envio final.',
    agent: 'AGENT-LOCAL-01',
    incidentId: 'inc-024',
    analysisId: 'ai-024',
    logs: [
      { time: '14:30:01', level: 'INFO', step: 'INIT', message: 'Inicio de ejecucion EX-247' },
      { time: '14:30:05', level: 'INFO', step: 'CARGA_DATOS', message: 'Se obtuvieron 18 registros pendientes' },
      { time: '14:30:12', level: 'INFO', step: 'VALIDACION', message: 'Validando estructura de datos de entrada' },
      { time: '14:30:16', level: 'WARNING', step: 'VALIDACION', message: 'Se detectaron 2 registros con campos incompletos' },
      { time: '14:30:22', level: 'INFO', step: 'REGISTRO', message: 'Iniciando envio de resultados al sistema destino' },
      { time: '14:30:30', level: 'ERROR', step: 'REGISTRO', message: 'Campo requerido vacio en formulario de registro' },
      { time: '14:30:31', level: 'CRITICAL', step: 'FIN', message: 'Ejecucion detenida por error de validacion' },
    ],
  },
  {
    id: 'ex-246',
    publicCode: 'EX-246',
    rpaId: 'rpa-certificados',
    rpaName: 'Bot_Facturacion',
    process: 'Contabilidad',
    status: 'SUCCESS',
    result: 'Completado',
    responsible: 'J. Rodriguez',
    dateLabel: 'Hoy',
    timeLabel: '09:42',
    durationLabel: '4m 12s',
    durationMs: 252000,
    triggerType: 'Programado',
    scenario: 'Horario regular',
    totalItems: 48,
    successItems: 48,
    failedItems: 0,
    errorType: '-',
    summary: 'Ejecucion completada sin observaciones.',
    agent: 'AGT-PROD-01',
    logs: [],
  },
  {
    id: 'ex-245',
    publicCode: 'EX-245',
    rpaId: 'rpa-publicacion',
    rpaName: 'Bot_Conciliacion',
    process: 'Finanzas',
    status: 'FAILED',
    result: 'Error login',
    responsible: 'M. Torres',
    dateLabel: 'Hoy',
    timeLabel: '09:30',
    durationLabel: '1m 08s',
    durationMs: 68000,
    triggerType: 'API',
    scenario: 'Login vencido',
    totalItems: 14,
    successItems: 2,
    failedItems: 12,
    errorType: 'Timeout',
    summary: 'No se logro autenticar en el sistema remoto.',
    agent: 'AGT-PROD-03',
    logs: [],
  },
  {
    id: 'ex-244',
    publicCode: 'EX-244',
    rpaId: 'rpa-reportes',
    rpaName: 'Bot_Reportes',
    process: 'RRHH',
    status: 'SUCCESS',
    result: 'Completado',
    responsible: 'A. Garcia',
    dateLabel: 'Hoy',
    timeLabel: '09:15',
    durationLabel: '2m 55s',
    durationMs: 175000,
    triggerType: 'Programado',
    scenario: 'Corte diario',
    totalItems: 12,
    successItems: 12,
    failedItems: 0,
    errorType: '-',
    summary: 'Ejecucion correcta.',
    agent: 'AGT-PROD-06',
    logs: [],
  },
  {
    id: 'ex-243',
    publicCode: 'EX-243',
    rpaId: 'rpa-alertas',
    rpaName: 'Bot_Inventario',
    process: 'Logistica',
    status: 'SUCCESS',
    result: 'Completado',
    responsible: 'C. Lopez',
    dateLabel: 'Hoy',
    timeLabel: '08:00',
    durationLabel: '5m 30s',
    durationMs: 330000,
    triggerType: 'Programado',
    scenario: 'Stock matinal',
    totalItems: 85,
    successItems: 85,
    failedItems: 0,
    errorType: '-',
    summary: 'Inventario conciliado.',
    agent: 'AGT-PROD-05',
    logs: [],
  },
  {
    id: 'ex-242',
    publicCode: 'EX-242',
    rpaId: 'rpa-registro',
    rpaName: 'Bot_Cobranza',
    process: 'Ventas',
    status: 'FAILED',
    result: 'Error BD',
    responsible: 'R. Silva',
    dateLabel: 'Ayer',
    timeLabel: '18:00',
    durationLabel: '0m 45s',
    durationMs: 45000,
    triggerType: 'Programado',
    scenario: 'Conexion a base',
    totalItems: 10,
    successItems: 0,
    failedItems: 10,
    errorType: 'Credenciales',
    summary: 'Credenciales no validas al abrir el origen.',
    agent: 'AGT-PROD-04',
    logs: [],
  },
  {
    id: 'ex-241',
    publicCode: 'EX-241',
    rpaId: 'rpa-reportes',
    rpaName: 'Bot_Nomina',
    process: 'RRHH',
    status: 'SUCCESS',
    result: 'Completado',
    responsible: 'J. Rodriguez',
    dateLabel: 'Ayer',
    timeLabel: '09:00',
    durationLabel: '6m 10s',
    durationMs: 370000,
    triggerType: 'Programado',
    scenario: 'Cierre mensual',
    totalItems: 56,
    successItems: 56,
    failedItems: 0,
    errorType: '-',
    summary: 'Planilla enviada correctamente.',
    agent: 'AGT-PROD-06',
    logs: [],
  },
  {
    id: 'ex-240',
    publicCode: 'EX-240',
    rpaId: 'rpa-certificados',
    rpaName: 'Bot_Sync_ERP',
    process: 'TI',
    status: 'FAILED',
    result: 'Error conexion',
    responsible: 'R. Silva',
    dateLabel: 'Hace 2d',
    timeLabel: '10:30',
    durationLabel: '2m 20s',
    durationMs: 140000,
    triggerType: 'Programado',
    scenario: 'ERP no responde',
    totalItems: 40,
    successItems: 11,
    failedItems: 29,
    errorType: 'Conexion',
    summary: 'El ERP rechazo la conexion remota.',
    agent: 'AGT-PROD-04',
    logs: [],
  },
  {
    id: 'ex-239',
    publicCode: 'EX-239',
    rpaId: 'rpa-evaluaciones',
    rpaName: 'Bot_Auditoria',
    process: 'Legal',
    status: 'SUCCESS',
    result: 'Completado',
    responsible: 'M. Torres',
    dateLabel: 'Hace 2d',
    timeLabel: '08:10',
    durationLabel: '8m 15s',
    durationMs: 495000,
    triggerType: 'Programado',
    scenario: 'Corte semanal',
    totalItems: 16,
    successItems: 16,
    failedItems: 0,
    errorType: '-',
    summary: 'Sin observaciones.',
    agent: 'AGT-PROD-03',
    logs: [],
  },
  {
    id: 'ex-238',
    publicCode: 'EX-238',
    rpaId: 'rpa-alertas',
    rpaName: 'Bot_Alertas',
    process: 'Seguridad',
    status: 'SUCCESS',
    result: 'Completado',
    responsible: 'P. Mendez',
    dateLabel: 'Hace 2d',
    timeLabel: '07:30',
    durationLabel: '1m 50s',
    durationMs: 110000,
    triggerType: 'Programado',
    scenario: 'Barrido normal',
    totalItems: 5,
    successItems: 5,
    failedItems: 0,
    errorType: '-',
    summary: 'Todo conforme.',
    agent: 'AGT-PROD-05',
    logs: [],
  },
  {
    id: 'ex-237',
    publicCode: 'EX-237',
    rpaId: 'rpa-fechas',
    rpaName: 'Bot_Compras',
    process: 'Compras',
    status: 'REVIEW',
    result: 'Revisando',
    responsible: 'P. Mendez',
    dateLabel: 'Hace 3d',
    timeLabel: '12:30',
    durationLabel: '3m 00s',
    durationMs: 180000,
    triggerType: 'Manual',
    scenario: 'Ajuste manual',
    totalItems: 25,
    successItems: 21,
    failedItems: 4,
    errorType: 'Datos',
    summary: 'Pendiente de revision humana.',
    agent: 'AGT-QA-02',
    logs: [],
  },
  {
    id: 'ex-236',
    publicCode: 'EX-236',
    rpaId: 'rpa-reportes',
    rpaName: 'Bot_Cierre',
    process: 'Contabilidad',
    status: 'SUCCESS',
    result: 'Completado',
    responsible: 'A. Garcia',
    dateLabel: 'Hace 3d',
    timeLabel: '08:00',
    durationLabel: '7m 30s',
    durationMs: 450000,
    triggerType: 'Programado',
    scenario: 'Cierre semanal',
    totalItems: 30,
    successItems: 30,
    failedItems: 0,
    errorType: '-',
    summary: 'Listo.',
    agent: 'AGT-PROD-06',
    logs: [],
  },
]

export const incidentCatalog: IncidentRecord[] = [
  {
    id: 'inc-024',
    code: 'INC-024',
    title: 'Error en validacion de datos',
    rpaId: 'rpa-registro',
    rpaName: 'RPA Registro Resultados',
    executionId: 'ex-247',
    executionCode: 'EX-247',
    category: 'Datos',
    severity: 'HIGH',
    status: 'IN_REVIEW',
    responsible: 'Juan Rodriguez',
    detectedAt: '05/06/2026 14:30',
    updatedAt: '05/06/2026 15:10',
    description:
      'El bot no pudo registrar resultados en el sistema destino porque los datos enviados desde el formulario contenian valores invalidos o campos incompletos.',
    probableCause:
      'Fallo en la validacion de datos de entrada. El origen envio registros con campos obligatorios vacios o en formato incorrecto.',
    resolution: '',
    analysisId: 'ai-024',
    timeline: [
      {
        at: '05/06/2026 14:32',
        user: 'Juan Rodriguez',
        action: 'ASSIGNMENT',
        comment: 'Incidente asignado para revision.',
      },
      {
        at: '05/06/2026 14:40',
        user: 'Juan Rodriguez',
        action: 'COMMENT',
        comment: 'Se reviso el log y se detecto campo obligatorio vacio.',
      },
      {
        at: '05/06/2026 14:48',
        user: 'Juan Rodriguez',
        action: 'TECHNICAL_ACTION',
        comment: 'Se valido el origen de datos del proceso.',
      },
      {
        at: '05/06/2026 15:05',
        user: 'Juan Rodriguez',
        action: 'STATUS_CHANGE',
        comment: 'Estado actualizado a En revision.',
      },
    ],
  },
  {
    id: 'inc-023',
    code: 'ALT-001',
    title: 'Interfaz no disponible',
    rpaId: 'rpa-certificados',
    rpaName: 'RPA Gen. Certificados',
    executionId: 'ex-246',
    executionCode: 'EX-246',
    category: 'Interfaz',
    severity: 'HIGH',
    status: 'PENDING',
    responsible: 'Equipo Tecnico',
    detectedAt: '03/06/2026 10:30',
    updatedAt: '03/06/2026 10:45',
    description: 'La pantalla de certificados no cargaba el componente principal.',
    probableCause: 'Recurso estatico no respondio a tiempo.',
    timeline: [],
  },
  {
    id: 'inc-022',
    code: 'ALT-002',
    title: 'Campos incompletos detectados',
    rpaId: 'rpa-registro',
    rpaName: 'RPA Reg. Resultados',
    executionId: 'ex-247',
    executionCode: 'EX-247',
    category: 'Datos',
    severity: 'HIGH',
    status: 'IN_REVIEW',
    responsible: 'Equipo Tecnico',
    detectedAt: '05/06/2026 14:30',
    updatedAt: '05/06/2026 14:50',
    description: 'Los datos de origen no cumplieron el validador previo.',
    probableCause: 'Origen academico con campos obligatorios en blanco.',
    timeline: [],
  },
  {
    id: 'inc-021',
    code: 'ALT-003',
    title: 'Timeout de autenticacion',
    rpaId: 'rpa-publicacion',
    rpaName: 'Bot_Conciliacion',
    executionId: 'ex-245',
    executionCode: 'EX-245',
    category: 'Timeout',
    severity: 'HIGH',
    status: 'PENDING',
    responsible: 'M. Torres',
    detectedAt: 'Hoy 09:30',
    updatedAt: 'Hoy 09:30',
    description: 'No se obtuvo token del sistema remoto.',
    probableCause: 'Latencia alta en autenticacion.',
    timeline: [],
  },
  {
    id: 'inc-020',
    code: 'ALT-004',
    title: 'Credenciales no validas',
    rpaId: 'rpa-registro',
    rpaName: 'Bot_Cobranza',
    executionId: 'ex-242',
    executionCode: 'EX-242',
    category: 'Credenciales',
    severity: 'MEDIUM',
    status: 'IN_REVIEW',
    responsible: 'R. Silva',
    detectedAt: 'Hoy 08:15',
    updatedAt: 'Hoy 08:50',
    description: 'Usuario o password invalido para el origen.',
    probableCause: 'Cambio de clave no sincronizado.',
    timeline: [],
  },
  {
    id: 'inc-019',
    code: 'ALT-005',
    title: 'Conexion intermitente',
    rpaId: 'rpa-sync-erp',
    rpaName: 'Bot_Sync_ERP',
    executionId: 'ex-240',
    executionCode: 'EX-240',
    category: 'Conexion',
    severity: 'MEDIUM',
    status: 'PENDING',
    responsible: 'R. Silva',
    detectedAt: 'Hoy 07:00',
    updatedAt: 'Hoy 07:20',
    description: 'Caidas intermitentes del ERP.',
    probableCause: 'Servicio remoto degradado.',
    timeline: [],
  },
  {
    id: 'inc-018',
    code: 'ALT-006',
    title: 'Interfaz estabilizada',
    rpaId: 'rpa-fechas',
    rpaName: 'RPA Cambio Fechas',
    executionId: 'ex-237',
    executionCode: 'EX-237',
    category: 'Interfaz',
    severity: 'LOW',
    status: 'RESOLVED',
    responsible: 'J. Rodriguez',
    detectedAt: 'Ayer 15:00',
    updatedAt: 'Ayer 15:30',
    description: 'Incidente resuelto.',
    probableCause: 'Cambio menor de selector.',
    timeline: [],
  },
  {
    id: 'inc-017',
    code: 'ALT-007',
    title: 'Dato inconsistente',
    rpaId: 'rpa-alertas',
    rpaName: 'Bot_Inventario',
    executionId: 'ex-243',
    executionCode: 'EX-243',
    category: 'Datos',
    severity: 'MEDIUM',
    status: 'RESOLVED',
    responsible: 'C. Lopez',
    detectedAt: 'Ayer 12:20',
    updatedAt: 'Ayer 13:10',
    description: 'Catalogo corregido manualmente.',
    probableCause: 'Archivo de entrada con formato mixto.',
    timeline: [],
  },
  {
    id: 'inc-016',
    code: 'ALT-008',
    title: 'Conexion observada',
    rpaId: 'rpa-publicacion',
    rpaName: 'RPA Pub. Certificados',
    executionId: 'ex-245',
    executionCode: 'EX-245',
    category: 'Conexion',
    severity: 'LOW',
    status: 'OBSERVED',
    responsible: 'Equipo Tecnico',
    detectedAt: 'Ayer 09:45',
    updatedAt: 'Ayer 10:05',
    description: 'Se mantiene en observacion.',
    probableCause: 'Pico de consumo remoto.',
    timeline: [],
  },
  {
    id: 'inc-015',
    code: 'ALT-009',
    title: 'Error de datos repetidos',
    rpaId: 'rpa-fechas',
    rpaName: 'Bot_Compras',
    executionId: 'ex-237',
    executionCode: 'EX-237',
    category: 'Datos',
    severity: 'HIGH',
    status: 'IN_REVIEW',
    responsible: 'P. Mendez',
    detectedAt: 'Ayer 09:45',
    updatedAt: 'Ayer 10:10',
    description: 'El lote incluia filas duplicadas.',
    probableCause: 'Generacion duplicada de origen.',
    timeline: [],
  },
  {
    id: 'inc-014',
    code: 'ALT-010',
    title: 'Fallo de interfaz menor',
    rpaId: 'rpa-reportes',
    rpaName: 'Bot_Nomina',
    executionId: 'ex-241',
    executionCode: 'EX-241',
    category: 'Interfaz',
    severity: 'LOW',
    status: 'RESOLVED',
    responsible: 'J. Rodriguez',
    detectedAt: 'Hace 2d',
    updatedAt: 'Hace 2d',
    description: 'Resuelto sin impacto.',
    probableCause: 'Cambio visual de formulario.',
    timeline: [],
  },
]

export const analysisCatalog: AnalysisRecord[] = [
  {
    id: 'ai-024',
    executionId: 'ex-247',
    executionCode: 'EX-247',
    incidentId: 'inc-024',
    rpaName: 'RPA Registro Resultados',
    process: 'Resultados Academicos',
    agent: 'AGENT-LOCAL-01',
    executionStatus: 'Fallido',
    preliminaryError: 'Datos',
    classification: 'Error de datos',
    confidence: 85,
    probableCause:
      'La IA detecta que la ejecucion intento registrar resultados con campos obligatorios vacios o incompletos. El error se origina en la validacion previa al envio.',
    recommendation: [
      'Validar que los registros origen incluyan todos los campos obligatorios.',
      'Revisar la regla de validacion previa antes del paso REGISTRO.',
      'Incorporar control preventivo para campos nulos o vacios.',
      'Reintentar la ejecucion luego de corregir los datos.',
    ],
    provider: 'Gemini API',
    model: 'SmartRPA-IA v2.1',
    analyzedAt: '05/06/2026 14:31',
    reviewedPatterns: 847,
    durationSeconds: 1.2,
    relatedIncidentStatus: 'En revision',
    relatedIncidentSeverity: 'Alta',
    responsible: 'Juan Rodriguez',
    sanitizedLog: [
      { time: '14:30:22', level: 'INFO', step: 'REGISTRO', message: 'Iniciando envio de resultados al sistema destino' },
      { time: '14:30:30', level: 'ERROR', step: 'REGISTRO', message: 'Campo requerido vacio en formulario de registro' },
      { time: '14:30:31', level: 'CRITICAL', step: 'FIN', message: 'Ejecucion detenida por error de validacion' },
    ],
    similarCases: [
      { date: '02/06/2026', errorType: 'Error de datos', match: 85 },
      { date: '26/05/2026', errorType: 'Error de datos', match: 82 },
      { date: '19/05/2026', errorType: 'Interfaz', match: 71 },
    ],
  },
]

export const dashboardSnapshot = {
  cards: [
    { title: 'Total RPA', value: '48', subtitle: 'Bots monitoreados', tone: 'navy' as const },
    { title: 'RPA Activos', value: '36', subtitle: 'En ejecucion normal', tone: 'green' as const },
    { title: 'RPA Inactivos', value: '8', subtitle: 'Sin ejecuciones', tone: 'slate' as const },
    { title: 'En Revision', value: '4', subtitle: 'Requieren atencion', tone: 'amber' as const },
    { title: 'Total Ejecuciones', value: '1,248', subtitle: 'Este mes', tone: 'blue' as const },
    { title: 'Tasa de Exito', value: '94.2%', subtitle: '+2.1% vs mes anterior', tone: 'green' as const },
    { title: 'Errores Detectados', value: '72', subtitle: 'Ultimas 24 horas', tone: 'red' as const },
    { title: 'Tiempo Promedio', value: '3.4 min', subtitle: 'Por ejecucion', tone: 'amber' as const },
  ],
  executionsByDay: [38, 52, 46, 66, 79, 58, 72, 61, 83, 77, 64, 91, 54, 78],
  errorsByType: [
    { label: 'Timeout', percent: 35, tone: 'red' as const },
    { label: 'Conexion', percent: 28, tone: 'amber' as const },
    { label: 'Datos', percent: 20, tone: 'blue' as const },
  ],
}

export const metricsSnapshot = {
  successTrend: [89, 91, 90, 93, 94, 92, 95, 94, 96, 95],
  dailyExecutions: [52, 67, 61, 74, 85, 69, 80, 72, 88, 81, 75, 90, 66, 78, 84, 70, 76, 85, 64, 72, 89, 77, 65, 83, 79, 71, 82, 86, 63, 87],
  topFailures: [
    { name: 'RPA Reg. Resultados', value: 28, tone: 'red' as const },
    { name: 'Bot_Conciliacion', value: 19, tone: 'red' as const },
    { name: 'Bot_Cobranza', value: 14, tone: 'amber' as const },
    { name: 'Bot_Sync_ERP', value: 11, tone: 'amber' as const },
    { name: 'RPA Cambio Fechas', value: 8, tone: 'green' as const },
    { name: 'Bot_Inventario', value: 5, tone: 'green' as const },
  ],
  averageByRpa: [
    { name: 'Bot_Auditoria', value: 8.2 },
    { name: 'Bot_Nomina', value: 6.1 },
    { name: 'RPA Reg. Resultados', value: 5.4 },
    { name: 'Bot_Sync_ERP', value: 4.9 },
    { name: 'Bot_Facturacion', value: 4.2 },
    { name: 'RPA Gen. Cert.', value: 3.4 },
  ],
  exportButtons: ['Exportar PDF', 'Exportar Excel'],
}

export const settingsSnapshot = {
  refreshOptions: ['30 s', '1 min', '5 min', '15 min'],
  timeoutOptions: ['2 min', '5 min', '10 min'],
  categories: [
    { label: 'Conexion', tone: 'blue' as const },
    { label: 'Credenciales', tone: 'purple' as const },
    { label: 'Datos', tone: 'amber' as const },
    { label: 'Interfaz', tone: 'green' as const },
    { label: 'Timeout', tone: 'red' as const },
    { label: 'Base de datos', tone: 'blue' as const },
    { label: 'Regla de negocio', tone: 'purple' as const },
  ],
  recipients: ['admin@empresa.com', 'tecnico.rpa@empresa.com', 'soporte@empresa.com', 'procesos@empresa.com'],
  channels: [
    { label: 'Panel interno', active: true },
    { label: 'Correo electronico', active: true },
    { label: 'Microsoft Teams', active: false },
  ],
  integrations: [
    { label: 'API Laravel', status: 'Operativo', tone: 'green' as const },
    { label: 'Base de datos PostgreSQL', status: 'Operativo', tone: 'green' as const },
    { label: 'Motor IA', status: 'Operativo', tone: 'green' as const },
    { label: 'Servicio de alertas', status: 'Advertencia', tone: 'amber' as const },
    { label: 'Agentes RPA', status: '3 conectados', tone: 'blue' as const },
  ],
}

export function getRoleCard(roleId: RoleKey) {
  return roleCards.find((role) => role.id === roleId) ?? roleCards[0]
}

export function getRpaById(rpaId?: string) {
  return rpaCatalog.find((item) => item.id === rpaId) ?? rpaCatalog[0]
}

export function getExecutionById(executionId?: string) {
  return executionCatalog.find((item) => item.id === executionId) ?? executionCatalog[0]
}

export function getIncidentById(incidentId?: string) {
  return incidentCatalog.find((item) => item.id === incidentId) ?? incidentCatalog[0]
}

export function getAnalysisById(analysisId?: string) {
  return analysisCatalog.find((item) => item.id === analysisId) ?? analysisCatalog[0]
}
