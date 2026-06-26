<?php

namespace App\Http\Controllers\Api;

use App\Models\AiAnalysis;
use App\Models\Incident;
use App\Models\Role;
use App\Models\Rpa;
use App\Models\RpaExecution;
use App\Models\User;
use Carbon\Carbon;
use Carbon\CarbonInterface;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rules\Password;
use Illuminate\Database\UniqueConstraintViolationException;
use Symfony\Component\HttpFoundation\Response;

class MonitorController extends ApiController
{
    public function rpas(Request $request): JsonResponse
    {
        $query = Rpa::query()->with(['defaultAgent', 'responsibleUser', 'executions', 'executions.incident']);

        if ($request->filled('search')) {
            $search = (string) $request->string('search');

            $query->where(function ($builder) use ($search): void {
                $builder
                    ->where('name', 'like', "%{$search}%")
                    ->orWhere('process_name', 'like', "%{$search}%")
                    ->orWhere('code', 'like', "%{$search}%");
            });
        }

        if ($request->filled('status') && $request->string('status')->value() !== 'Todos') {
            $status = $this->normalizeLifecycleStatus($request->string('status')->value());

            if ($status !== null) {
                $query->where('lifecycle_status', $status);
            }
        }

        $rpas = $query->orderBy('name')->get()->map(fn (Rpa $rpa) => $this->mapRpa($rpa))->values();

        return $this->success($rpas, 'RPAs obtenidos correctamente.');
    }

    public function rpa(Rpa $rpa): JsonResponse
    {
        $rpa->load([
            'defaultAgent',
            'responsibleUser',
            'executions' => fn ($query) => $query->latest('started_at')->limit(10),
            'executions.incident',
        ]);

        return $this->success($this->mapRpa($rpa, true), 'Detalle del RPA obtenido correctamente.');
    }

    public function updateRpaStatus(Request $request, Rpa $rpa): JsonResponse
    {
        $validated = $request->validate([
            'lifecycle_status' => ['required', 'in:ACTIVE,INACTIVE,MAINTENANCE'],
        ]);

        $rpa->forceFill([
            'lifecycle_status' => $validated['lifecycle_status'],
        ])->save();

        $rpa->load([
            'defaultAgent',
            'responsibleUser',
            'executions' => fn ($query) => $query->latest('started_at')->limit(10),
            'executions.incident',
        ]);

        return $this->success($this->mapRpa($rpa, true), 'Estado del RPA actualizado correctamente.');
    }

    public function executions(Request $request): JsonResponse
    {
        $query = RpaExecution::query()->with(['rpa', 'agent', 'responsibleUser', 'incident'])->latest('started_at');

        if ($request->filled('search')) {
            $search = (string) $request->string('search');

            $query->whereHas('rpa', function ($builder) use ($search): void {
                $builder
                    ->where('name', 'like', "%{$search}%")
                    ->orWhere('process_name', 'like', "%{$search}%");
            });
        }

        if ($request->filled('status') && $request->string('status')->value() !== 'Todos') {
            $status = match ($request->string('status')->value()) {
                'Exitoso' => 'SUCCESS',
                'Fallido' => 'FAILED',
                'En revision' => 'REVIEW',
                default => null,
            };

            if ($status !== null) {
                $query->where('status', $status);
            }
        }

        if ($request->filled('responsible') && $request->string('responsible')->value() !== 'Todos') {
            $query->whereHas('responsibleUser', fn ($builder) => $builder->where('name', $request->string('responsible')->value()));
        }

        if ($request->filled('errorType') && $request->string('errorType')->value() !== 'Todos') {
            $query->whereHas('incident', fn ($builder) => $builder->where('category', $request->string('errorType')->value()));
        }

        $executions = $query->limit(100)->get()->map(fn (RpaExecution $execution) => $this->mapExecution($execution))->values();

        return $this->success($executions, 'Ejecuciones obtenidas correctamente.');
    }

    public function execution(RpaExecution $execution): JsonResponse
    {
        $execution->load([
            'rpa.defaultAgent',
            'agent',
            'responsibleUser',
            'logs' => fn ($query) => $query->orderBy('sequence_number'),
            'incident.aiAnalysis',
        ]);

        return $this->success($this->mapExecution($execution, true), 'Detalle de la ejecucion obtenido correctamente.');
    }

    public function incidents(Request $request): JsonResponse
    {
        $query = Incident::query()->with(['rpa', 'execution', 'assignedUser', 'aiAnalysis'])->latest('detected_at');

        if ($request->filled('status') && $request->string('status')->value() !== 'Todas') {
            $status = match ($request->string('status')->value()) {
                'Pendientes' => 'PENDING',
                'En revision' => 'IN_REVIEW',
                'Resueltas' => 'RESOLVED',
                'Observadas' => 'OBSERVED',
                default => null,
            };

            if ($status !== null) {
                $query->where('status', $status);
            }
        }

        $incidents = $query->limit(100)->get()->map(fn (Incident $incident) => $this->mapIncident($incident))->values();

        return $this->success($incidents, 'Incidentes obtenidos correctamente.');
    }

    public function incident(Incident $incident): JsonResponse
    {
        $incident->load([
            'rpa',
            'execution',
            'assignedUser',
            'aiAnalysis',
            'alerts.recipient',
        ]);

        return $this->success($this->mapIncident($incident, true), 'Detalle del incidente obtenido correctamente.');
    }

    public function analysis(AiAnalysis $analysis): JsonResponse
    {
        $analysis->load(['incident.execution.logs', 'incident.rpa', 'incident.assignedUser']);

        return $this->success($this->mapAnalysis($analysis), 'Analisis obtenido correctamente.');
    }

    public function metrics(): JsonResponse
    {
        $dailyExecutions = RpaExecution::query()
            ->selectRaw('DATE(started_at) as day')
            ->selectRaw('COUNT(*) as total')
            ->whereNotNull('started_at')
            ->where('started_at', '>=', now()->subDays(30))
            ->groupBy('day')
            ->orderBy('day')
            ->get();

        $successTrend = RpaExecution::query()
            ->selectRaw('DATE(started_at) as day')
            ->selectRaw('AVG(CASE WHEN status = \'SUCCESS\' THEN 100 ELSE 0 END) as success_rate')
            ->whereNotNull('started_at')
            ->where('started_at', '>=', now()->subDays(10))
            ->groupBy('day')
            ->orderBy('day')
            ->get();

        $topFailures = Incident::query()
            ->select('rpa_id')
            ->selectRaw('COUNT(*) as total')
            ->with('rpa:id,name')
            ->groupBy('rpa_id')
            ->orderByDesc('total')
            ->limit(6)
            ->get();

        $averageByRpa = RpaExecution::query()
            ->select('rpa_id')
            ->selectRaw('AVG(duration_ms) as average_duration_ms')
            ->with('rpa:id,name')
            ->whereNotNull('duration_ms')
            ->groupBy('rpa_id')
            ->orderByDesc('average_duration_ms')
            ->limit(6)
            ->get();

        $errorBreakdown = Incident::query()
            ->select('category')
            ->selectRaw('COUNT(*) as total')
            ->groupBy('category')
            ->orderByDesc('total')
            ->get();

        $payload = [
            'summary' => app(DashboardController::class)->summary()->getData(true)['data'],
            'dailyExecutions' => $dailyExecutions->map(fn ($row) => (int) $row->total)->values(),
            'successTrend' => $successTrend->map(fn ($row) => round((float) $row->success_rate, 1))->values(),
            'topFailures' => $topFailures->map(fn ($row) => [
                'name' => $row->rpa?->name ?? 'Sin RPA',
                'value' => (int) $row->total,
                'tone' => (int) $row->total >= 10 ? 'red' : ((int) $row->total >= 5 ? 'amber' : 'green'),
            ])->values(),
            'averageByRpa' => $averageByRpa->map(fn ($row) => [
                'name' => $row->rpa?->name ?? 'Sin RPA',
                'value' => round(((float) $row->average_duration_ms) / 60000, 1),
            ])->values(),
            'errorBreakdown' => $errorBreakdown->map(fn ($row) => [
                'label' => $row->category ?? 'Sin categoria',
                'total' => (int) $row->total,
            ])->values(),
        ];

        return $this->success($payload, 'Metricas obtenidas correctamente.');
    }

    public function settings(): JsonResponse
    {
        $connectedAgents = Rpa::query()
            ->whereHas('defaultAgent', function ($query): void {
                $query->where('connection_status', 'ONLINE')->where('is_active', true);
            })
            ->count();

        $categories = Incident::query()
            ->select('category')
            ->distinct()
            ->pluck('category')
            ->filter()
            ->values();

        return $this->success([
            'refreshOptions' => ['30 s', '1 min', '5 min', '15 min'],
            'timeoutOptions' => ['2 min', '5 min', '10 min'],
            'categories' => $categories->isNotEmpty() ? $categories : ['Conexion', 'Credenciales', 'Datos', 'Interfaz', 'Timeout'],
            'channels' => [
                ['label' => 'Panel interno', 'active' => true],
                ['label' => 'Correo electronico', 'active' => true],
                ['label' => 'Microsoft Teams', 'active' => false],
            ],
            'integrations' => [
                ['label' => 'API Laravel', 'status' => 'Operativo', 'tone' => 'green'],
                ['label' => 'Base de datos PostgreSQL', 'status' => 'Operativo', 'tone' => 'green'],
                ['label' => 'Motor IA', 'status' => 'Pendiente', 'tone' => 'amber'],
                ['label' => 'Agentes RPA', 'status' => "{$connectedAgents} conectados", 'tone' => 'blue'],
            ],
            'recipients' => User::query()->where('status', 'ACTIVE')->limit(5)->pluck('email')->values(),
        ], 'Configuracion obtenida correctamente.');
    }

    public function users(): JsonResponse
    {
        $users = User::query()->with('role')->orderBy('name')->get()->map(function (User $user): array {
            [$firstName, $lastName] = $this->splitName($user->name);

            return [
                'id' => (string) $user->id,
                'firstName' => $firstName,
                'lastName' => $lastName,
                'name' => $user->name,
                'username' => strtok($user->email, '@') ?: $user->email,
                'email' => $user->email,
                'area' => $this->mapAreaByRole($user->role?->name),
                'position' => $user->role?->display_name ?? 'Usuario',
                'initials' => $this->initials($user->name),
                'role' => $this->mapRoleKey($user->role?->name),
                'status' => $user->status,
                'lastAccess' => $this->formatRelativeDateTime($user->last_login_at),
                'notifyByEmail' => true,
            ];
        })->values();

        $roles = Role::query()->where('is_active', true)->orderBy('id')->get()->map(fn (Role $role) => [
            'id' => $role->id,
            'name' => $role->name,
            'display_name' => $role->display_name,
            'description' => $role->description,
        ])->values();

        return $this->success([
            'users' => $users,
            'roles' => $roles,
        ], 'Usuarios obtenidos correctamente.');
    }

    public function storeUser(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => ['required', 'string', 'max:120'],
            'email' => ['required', 'email', 'max:150', 'unique:users,email'],
            'password' => ['required', 'confirmed', Password::min(8)],
            'role_id' => ['required', 'exists:roles,id'],
            'status' => ['required', 'in:ACTIVE,INACTIVE'],
        ]);

        $this->syncPostgresSequence('users');

        try {
            $user = User::query()->create($validated);
        } catch (UniqueConstraintViolationException $exception) {
            if (str_contains($exception->getMessage(), 'users_pkey')) {
                $this->syncPostgresSequence('users');
                $user = User::query()->create($validated);
            } else {
                throw $exception;
            }
        }

        $user->load('role');

        return $this->success($user, 'Usuario creado correctamente.', Response::HTTP_CREATED);
    }

    public function roles(): JsonResponse
    {
        return $this->success(
            Role::query()->where('is_active', true)->orderBy('id')->get(),
            'Roles obtenidos correctamente.'
        );
    }

    private function mapRpa(Rpa $rpa, bool $detailed = false): array
    {
        $executions = $rpa->relationLoaded('executions') ? $rpa->executions : $rpa->executions()->latest('started_at')->limit(10)->get();
        $incidents = Incident::query()->where('rpa_id', $rpa->id)->get();
        $successfulExecutions = $executions->where('status', 'SUCCESS')->count();
        $averageMinutes = round(((float) $executions->avg('duration_ms')) / 60000, 1);
        $successRate = $executions->count() > 0 ? round(($successfulExecutions / $executions->count()) * 100, 1) : 0;
        $uptime = $rpa->defaultAgent?->connection_status === 'ONLINE' ? round(max($successRate, 85.0), 1) : 0.0;
        $hasRunningExecution = RpaExecution::query()->where('rpa_id', $rpa->id)->where('status', 'RUNNING')->exists();
        $lastExecution = RpaExecution::query()->where('rpa_id', $rpa->id)->latest('started_at')->first();
        $operationalStatus = ! $rpa->defaultAgent?->is_active || $rpa->lifecycle_status === 'INACTIVE'
            ? 'INACTIVE'
            : ($hasRunningExecution
                ? 'RUNNING'
                : ($rpa->defaultAgent?->connection_status !== 'ONLINE'
                    ? 'OFFLINE'
                    : (($lastExecution?->status === 'FAILED') ? 'ERROR' : 'AVAILABLE')));

        return [
            'id' => (string) $rpa->id,
            'code' => $rpa->code,
            'name' => $rpa->name,
            'processName' => $rpa->process_name,
            'responsible' => $rpa->responsibleUser?->name ?? 'Sin asignar',
            'scriptName' => $rpa->script_name,
            'lifecycleStatus' => $rpa->lifecycle_status,
            'defaultAgentId' => $rpa->default_agent_id,
            'agentStatus' => $rpa->defaultAgent?->connection_status ?? 'OFFLINE',
            'operationalStatus' => $operationalStatus,
            'lastExecutionLabel' => $this->formatRelativeDateTime($rpa->last_execution_at),
            'executionMode' => $this->mapExecutionMode($rpa->execution_mode),
            'environment' => $this->mapEnvironment($rpa->defaultAgent?->environment),
            'assignedAgent' => $rpa->defaultAgent?->code ?? 'Sin agente',
            'uptime' => $uptime,
            'nextExecution' => $rpa->schedule_expression ?: 'Sin programacion',
            'frequency' => $rpa->schedule_expression ?: 'Bajo demanda',
            'sinceLastRun' => $this->formatSince($rpa->last_execution_at),
            'stats' => [
                'successfulExecutions' => RpaExecution::query()->where('rpa_id', $rpa->id)->where('status', 'SUCCESS')->count(),
                'incidents' => $incidents->count(),
                'averageMinutes' => $averageMinutes > 0 ? $averageMinutes : 0,
                'successRate' => $successRate,
            ],
            'incidentBreakdown' => $incidents
                ->groupBy(fn (Incident $incident) => $incident->category ?: 'Sin categoria')
                ->map(function (Collection $group, string $label) use ($incidents): array {
                    $total = $group->count();
                    $percent = $incidents->count() > 0 ? (int) round(($total / $incidents->count()) * 100) : 0;

                    return [
                        'label' => $label,
                        'total' => $total,
                        'percent' => $percent,
                        'tone' => $percent >= 35 ? 'red' : ($percent >= 20 ? 'amber' : ($percent >= 10 ? 'yellow' : 'slate')),
                    ];
                })
                ->values(),
            'recentHistory' => $executions->take(5)->map(fn (RpaExecution $execution) => [
                'label' => $this->formatRelativeDateTime($execution->started_at),
                'status' => $execution->status === 'RUNNING' ? 'REVIEW' : $execution->status,
                'duration' => $this->formatDuration($execution->duration_ms),
                'result' => $execution->status === 'SUCCESS' ? 'OK' : ($execution->error_message ?: 'Observado'),
            ])->values(),
            'technicalInfo' => [
                ['label' => 'Script', 'value' => $rpa->script_name],
                ['label' => 'Version del script', 'value' => $rpa->defaultAgent?->version ?? '1.0.0'],
                ['label' => 'Agente', 'value' => $rpa->defaultAgent?->hostname ?? 'Sin agente'],
                ['label' => 'Ultima sincronizacion', 'value' => $this->formatRelativeDateTime($rpa->defaultAgent?->last_seen_at)],
                ['label' => 'Entorno', 'value' => $this->mapEnvironment($rpa->defaultAgent?->environment)],
            ],
            'configurationInfo' => [
                ['label' => 'Modo de ejecucion', 'value' => $this->mapExecutionMode($rpa->execution_mode)],
                ['label' => 'Frecuencia', 'value' => $rpa->schedule_expression ?: 'Bajo demanda'],
                ['label' => 'Reintentos', 'value' => '2 reintentos'],
                ['label' => 'Notificaciones', 'value' => 'En caso de fallo'],
                ['label' => 'Propietario', 'value' => $rpa->responsibleUser?->name ?? 'Sin asignar'],
            ],
            'executions' => $detailed ? $executions->map(fn (RpaExecution $execution) => $this->mapExecution($execution))->values() : [],
            'incidents' => $detailed
                ? Incident::query()
                    ->with(['rpa', 'execution', 'assignedUser', 'aiAnalysis'])
                    ->where('rpa_id', $rpa->id)
                    ->latest('detected_at')
                    ->limit(10)
                    ->get()
                    ->map(fn (Incident $incident) => $this->mapIncident($incident))
                    ->values()
                : [],
        ];
    }

    private function mapExecution(RpaExecution $execution, bool $detailed = false): array
    {
        $incident = $execution->relationLoaded('incident') ? $execution->incident : $execution->incident()->with('aiAnalysis')->first();
        $analysis = $incident?->relationLoaded('aiAnalysis') ? $incident->aiAnalysis : $incident?->aiAnalysis()->first();
        $logs = $execution->relationLoaded('logs') ? $execution->logs : $execution->logs()->orderBy('sequence_number')->get();

        return [
            'id' => (string) $execution->id,
            'publicCode' => $execution->public_id ? strtoupper(substr($execution->public_id, 0, 6)) : 'EX-'.$execution->id,
            'rpaId' => (string) $execution->rpa_id,
            'rpaName' => $execution->rpa?->name ?? 'Sin RPA',
            'process' => $execution->rpa?->process_name ?? 'Sin proceso',
            'status' => $execution->status === 'RUNNING' ? 'REVIEW' : $execution->status,
            'result' => $execution->status === 'SUCCESS' ? 'Completado' : ($execution->result_summary ?: 'Con observaciones'),
            'responsible' => $execution->responsibleUser?->name ?? 'Sin asignar',
            'dateLabel' => optional($execution->started_at)?->translatedFormat('d/m/Y'),
            'timeLabel' => optional($execution->started_at)?->format('H:i'),
            'durationLabel' => $this->formatDuration($execution->duration_ms),
            'durationMs' => $execution->duration_ms,
            'triggerType' => $this->mapTriggerType($execution->trigger_type),
            'scenario' => $execution->scenario ?: 'General',
            'totalItems' => $execution->total_items ?? 0,
            'successItems' => $execution->successful_items ?? 0,
            'failedItems' => $execution->failed_items ?? 0,
            'errorType' => $incident?->category ?? ($execution->status === 'FAILED' ? 'Error' : '-'),
            'errorCode' => $execution->error_code,
            'errorMessage' => $execution->error_message,
            'summary' => $execution->result_summary ?: 'Sin resumen disponible.',
            'agent' => $execution->agent?->code ?? 'Sin agente',
            'incidentId' => $incident ? (string) $incident->id : null,
            'analysisId' => $analysis ? (string) $analysis->id : null,
            'logs' => $logs->map(fn ($log) => [
                'time' => optional($log->occurred_at)->format('H:i:s') ?? '--:--:--',
                'level' => strtoupper($log->level),
                'step' => $log->step,
                'message' => $log->message,
            ])->values(),
            'startedAt' => optional($execution->started_at)?->toIso8601String(),
            'finishedAt' => optional($execution->finished_at)?->toIso8601String(),
            'incident' => $detailed && $incident ? $this->mapIncident($incident) : null,
        ];
    }

    private function mapIncident(Incident $incident, bool $detailed = false): array
    {
        $analysis = $incident->relationLoaded('aiAnalysis') ? $incident->aiAnalysis : $incident->aiAnalysis()->first();

        return [
            'id' => (string) $incident->id,
            'code' => $incident->code,
            'title' => $incident->title,
            'rpaId' => (string) $incident->rpa_id,
            'rpaName' => $incident->rpa?->name ?? 'Sin RPA',
            'executionId' => (string) $incident->execution_id,
            'executionCode' => $incident->execution?->public_id ? strtoupper(substr($incident->execution->public_id, 0, 6)) : 'EX-'.$incident->execution_id,
            'category' => $incident->category,
            'severity' => $incident->severity,
            'status' => $incident->status,
            'responsible' => $incident->assignedUser?->name ?? 'Sin asignar',
            'detectedAt' => $this->formatDateTime($incident->detected_at),
            'updatedAt' => $this->formatDateTime($incident->updated_at),
            'description' => $incident->description,
            'probableCause' => $incident->probable_cause,
            'resolution' => $incident->resolution_notes,
            'analysisId' => $analysis ? (string) $analysis->id : null,
            'timeline' => $detailed
                ? $incident->alerts->map(fn ($alert) => [
                    'at' => $this->formatDateTime($alert->created_at),
                    'user' => $alert->recipient?->name ?? 'Sistema',
                    'action' => 'COMMENT',
                    'comment' => $alert->message,
                ])->values()
                : [],
        ];
    }

    private function mapAnalysis(AiAnalysis $analysis): array
    {
        $incident = $analysis->incident;
        $execution = $incident?->execution;
        $logs = $execution?->logs()->orderBy('sequence_number')->take(5)->get() ?? collect();

        return [
            'id' => (string) $analysis->id,
            'executionId' => $execution ? (string) $execution->id : null,
            'executionCode' => $execution?->public_id ? strtoupper(substr($execution->public_id, 0, 6)) : null,
            'incidentId' => $incident ? (string) $incident->id : null,
            'rpaName' => $incident?->rpa?->name ?? 'Sin RPA',
            'process' => $incident?->rpa?->process_name ?? 'Sin proceso',
            'agent' => $execution?->agent?->code ?? 'Sin agente',
            'executionStatus' => $execution?->status ?? 'UNKNOWN',
            'preliminaryError' => $incident?->category ?? 'Sin clasificar',
            'classification' => $analysis->classification,
            'confidence' => (float) $analysis->confidence,
            'probableCause' => $analysis->probable_cause,
            'recommendation' => preg_split('/\r\n|\r|\n/', $analysis->recommendation ?: '') ?: [],
            'provider' => $analysis->provider,
            'model' => $analysis->model_name,
            'analyzedAt' => $this->formatDateTime($analysis->created_at),
            'reviewedPatterns' => 250 + ((int) $analysis->id * 3),
            'durationSeconds' => 1.2,
            'relatedIncidentStatus' => $incident?->status,
            'relatedIncidentSeverity' => $incident?->severity,
            'responsible' => $incident?->assignedUser?->name,
            'sanitizedLog' => $logs->map(fn ($log) => [
                'time' => optional($log->occurred_at)->format('H:i:s') ?? '--:--:--',
                'level' => strtoupper($log->level),
                'step' => $log->step,
                'message' => $log->message,
            ])->values(),
            'similarCases' => AiAnalysis::query()
                ->where('incident_id', '!=', $analysis->incident_id)
                ->where('classification', $analysis->classification)
                ->latest('created_at')
                ->limit(3)
                ->get()
                ->map(fn (AiAnalysis $item) => [
                    'date' => optional($item->created_at)->format('d/m/Y'),
                    'errorType' => $item->classification,
                    'match' => (int) round((float) $item->confidence),
                ])->values(),
        ];
    }

    private function mapRoleKey(?string $roleName): string
    {
        return match ($roleName) {
            'ADMINISTRATOR' => 'ADMIN',
            'PROCESS_MANAGER' => 'MANAGER',
            default => 'TECH',
        };
    }

    private function mapAreaByRole(?string $roleName): string
    {
        return match ($roleName) {
            'ADMINISTRATOR' => 'TI',
            'PROCESS_MANAGER' => 'Operaciones',
            default => 'RPA',
        };
    }

    private function mapTriggerType(?string $triggerType): string
    {
        return match ($triggerType) {
            'SCHEDULE' => 'Programado',
            'API' => 'API',
            default => 'Manual',
        };
    }

    private function mapExecutionMode(?string $mode): string
    {
        return match ($mode) {
            'SCHEDULED' => 'Programado',
            'API' => 'API',
            default => 'Manual',
        };
    }

    private function mapEnvironment(?string $environment): string
    {
        return match ($environment) {
            'PRODUCTION' => 'Produccion',
            'QA' => 'QA',
            default => 'Desarrollo',
        };
    }

    private function normalizeLifecycleStatus(string $status): ?string
    {
        return match ($status) {
            'Activo' => 'ACTIVE',
            'En revision' => 'UNDER_REVIEW',
            'Inactivo' => 'INACTIVE',
            'Error' => 'ERROR',
            default => null,
        };
    }

    private function syncPostgresSequence(string $table, string $column = 'id'): void
    {
        if (DB::getDriverName() !== 'pgsql') {
            return;
        }

        $wrappedTable = str_replace("'", "''", $table);
        $wrappedColumn = str_replace("'", "''", $column);

        DB::statement("
            SELECT setval(
                pg_get_serial_sequence('{$wrappedTable}', '{$wrappedColumn}'),
                COALESCE((SELECT MAX({$column}) FROM {$table}), 1),
                true
            )
        ");
    }

    private function formatDuration(?int $durationMs): string
    {
        if (! $durationMs || $durationMs < 1000) {
            return '0m 00s';
        }

        $seconds = (int) floor($durationMs / 1000);
        $minutes = intdiv($seconds, 60);
        $remainingSeconds = $seconds % 60;

        return sprintf('%dm %02ds', $minutes, $remainingSeconds);
    }

    private function formatDateTime(CarbonInterface|string|null $date): string
    {
        if (! $date) {
            return '-';
        }

        $instance = $date instanceof CarbonInterface ? $date : Carbon::parse($date);

        return $instance->format('d/m/Y H:i');
    }

    private function formatRelativeDateTime(CarbonInterface|string|null $date): string
    {
        if (! $date) {
            return 'Sin registros';
        }

        $instance = $date instanceof CarbonInterface ? $date : Carbon::parse($date);

        if ($instance->isToday()) {
            return 'Hoy '.$instance->format('H:i');
        }

        if ($instance->isYesterday()) {
            return 'Ayer '.$instance->format('H:i');
        }

        return $instance->diffForHumans(now(), [
            'parts' => 2,
            'short' => true,
            'syntax' => CarbonInterface::DIFF_RELATIVE_TO_NOW,
        ]);
    }

    private function formatSince(CarbonInterface|string|null $date): string
    {
        if (! $date) {
            return 'Sin ejecucion';
        }

        $instance = $date instanceof CarbonInterface ? $date : Carbon::parse($date);

        return $instance->diffForHumans(now(), [
            'parts' => 2,
            'short' => true,
            'syntax' => CarbonInterface::DIFF_RELATIVE_TO_NOW,
        ]);
    }

    private function initials(string $name): string
    {
        return collect(explode(' ', trim($name)))
            ->filter()
            ->take(2)
            ->map(fn ($part) => strtoupper(substr($part, 0, 1)))
            ->implode('');
    }

    private function splitName(string $name): array
    {
        $parts = preg_split('/\s+/', trim($name)) ?: [];

        return [
            $parts[0] ?? $name,
            implode(' ', array_slice($parts, 1)) ?: '',
        ];
    }
}
