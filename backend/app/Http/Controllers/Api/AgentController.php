<?php

namespace App\Http\Controllers\Api;

use App\Models\Alert;
use App\Models\ExecutionLog;
use App\Models\Incident;
use App\Models\Rpa;
use App\Models\RpaAgent;
use App\Models\RpaExecution;
use App\Models\User;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;
use Throwable;

class AgentController extends ApiController
{
    public function heartbeat(Request $request): JsonResponse
    {
        $agent = $this->resolveAgent($request);

        $validated = $request->validate([
            'agent_code' => ['required', 'string'],
            'status' => ['required', 'string'],
            'current_rpa' => ['nullable', 'string'],
            'sent_at' => ['nullable', 'date'],
        ]);

        if ($validated['agent_code'] !== $agent->code) {
            return $this->error('El codigo del agente no coincide con el token.', status: Response::HTTP_FORBIDDEN);
        }

        $agent->forceFill([
            'connection_status' => strtoupper($validated['status']),
            'last_seen_at' => now('UTC'),
            'is_active' => true,
        ])->save();

        return $this->success([
            'agent_id' => $agent->id,
            'status' => $agent->connection_status,
        ], 'Heartbeat recibido correctamente.');
    }

    public function start(Request $request): JsonResponse
    {
        $agent = $this->resolveAgent($request);

        $validated = $request->validate([
            'rpa_code' => ['required', 'string'],
            'trigger_type' => ['nullable', 'string'],
            'scenario' => ['nullable', 'string'],
            'triggered_by_email' => ['nullable', 'email'],
            'metadata' => ['nullable', 'array'],
        ]);

        $rpa = Rpa::query()->where('code', $validated['rpa_code'])->firstOrFail();
        $user = User::query()->where('email', $validated['triggered_by_email'] ?? 'admin@smartrpa.local')->first();

        $execution = RpaExecution::query()->create([
            'public_id' => (string) Str::uuid(),
            'rpa_id' => $rpa->id,
            'agent_id' => $agent->id,
            'triggered_by' => $user?->id,
            'trigger_type' => strtoupper($validated['trigger_type'] ?? 'API'),
            'scenario' => $validated['scenario'] ?? 'General',
            'status' => 'RUNNING',
            'started_at' => now(),
            'metadata' => $validated['metadata'] ?? [],
        ]);

        $rpa->forceFill(['last_execution_at' => now()])->save();
        $agent->forceFill(['connection_status' => 'ONLINE', 'last_seen_at' => now()])->save();

        return $this->success([
            'id' => $execution->id,
            'public_id' => $execution->public_id,
        ], 'Ejecucion iniciada correctamente.', Response::HTTP_CREATED);
    }

    public function log(Request $request, RpaExecution $execution): JsonResponse
    {
        $agent = $this->resolveAgent($request);
        $this->guardExecutionOwnership($execution, $agent);

        $validated = $request->validate([
            'level' => ['required', 'string'],
            'step' => ['required', 'string'],
            'message' => ['required', 'string'],
            'error_code' => ['nullable', 'string'],
            'context' => ['nullable', 'array'],
            'occurred_at' => ['nullable', 'date'],
        ]);

        $log = ExecutionLog::query()->create([
            'execution_id' => $execution->id,
            'sequence_number' => ((int) $execution->logs()->max('sequence_number')) + 1,
            'level' => strtoupper($validated['level']),
            'step' => $validated['step'],
            'message' => $validated['message'],
            'error_code' => $validated['error_code'] ?? null,
            'context' => $validated['context'] ?? [],
            'occurred_at' => $validated['occurred_at'] ?? now(),
            'created_at' => now(),
        ]);

        return $this->success($log, 'Log registrado correctamente.', Response::HTTP_CREATED);
    }

    public function complete(Request $request, RpaExecution $execution): JsonResponse
    {
        $agent = $this->resolveAgent($request);
        $this->guardExecutionOwnership($execution, $agent);

        $validated = $request->validate([
            'total_items' => ['nullable', 'integer'],
            'successful_items' => ['nullable', 'integer'],
            'failed_items' => ['nullable', 'integer'],
            'result_summary' => ['nullable', 'string'],
            'metadata' => ['nullable', 'array'],
            'finished_at' => ['nullable', 'date'],
        ]);

        $finishedAt = $validated['finished_at'] ?? now();
        $durationMs = max(0, Carbon::parse($finishedAt)->diffInMilliseconds($execution->started_at ?? now()));

        $execution->forceFill([
            'status' => 'SUCCESS',
            'finished_at' => $finishedAt,
            'duration_ms' => $durationMs,
            'total_items' => $validated['total_items'] ?? $execution->total_items,
            'successful_items' => $validated['successful_items'] ?? $execution->successful_items,
            'failed_items' => $validated['failed_items'] ?? $execution->failed_items,
            'result_summary' => $validated['result_summary'] ?? 'Ejecucion completada correctamente.',
            'metadata' => array_merge($execution->metadata ?? [], $validated['metadata'] ?? []),
        ])->save();

        $execution->rpa?->forceFill(['last_execution_at' => $finishedAt])->save();

        return $this->success($execution->fresh(), 'Ejecucion completada correctamente.');
    }

    public function fail(Request $request, RpaExecution $execution): JsonResponse
    {
        $agent = $this->resolveAgent($request);
        $this->guardExecutionOwnership($execution, $agent);

        $validated = $request->validate([
            'error_code' => ['required', 'string'],
            'error_message' => ['required', 'string'],
            'category' => ['nullable', 'string'],
            'severity' => ['nullable', 'string'],
            'total_items' => ['nullable', 'integer'],
            'successful_items' => ['nullable', 'integer'],
            'failed_items' => ['nullable', 'integer'],
            'result_summary' => ['nullable', 'string'],
            'metadata' => ['nullable', 'array'],
            'finished_at' => ['nullable', 'date'],
        ]);

        $finishedAt = $validated['finished_at'] ?? now();
        $durationMs = max(0, Carbon::parse($finishedAt)->diffInMilliseconds($execution->started_at ?? now()));

        $execution->forceFill([
            'status' => 'FAILED',
            'finished_at' => $finishedAt,
            'duration_ms' => $durationMs,
            'total_items' => $validated['total_items'] ?? $execution->total_items,
            'successful_items' => $validated['successful_items'] ?? 0,
            'failed_items' => $validated['failed_items'] ?? $validated['total_items'] ?? 0,
            'result_summary' => $validated['result_summary'] ?? 'La ejecucion termino con errores.',
            'error_code' => $validated['error_code'],
            'error_message' => $validated['error_message'],
            'metadata' => array_merge($execution->metadata ?? [], $validated['metadata'] ?? []),
        ])->save();

        $incidentCategory = $this->normalizeIncidentCategory($validated['category'] ?? null);
        $incidentStatus = 'OPEN';

        $incident = $execution->incident()->firstOrCreate(
            ['execution_id' => $execution->id],
            [
                'code' => 'INC-'.str_pad((string) $execution->id, 4, '0', STR_PAD_LEFT),
                'rpa_id' => $execution->rpa_id,
                'assigned_to' => $execution->rpa?->responsible_user_id,
                'title' => 'Fallo en '.$execution->rpa?->name,
                'category' => $incidentCategory,
                'severity' => strtoupper($validated['severity'] ?? 'HIGH'),
                'status' => $incidentStatus,
                'description' => $validated['error_message'],
                'probable_cause' => 'Pendiente de revision tecnica.',
                'detected_at' => $finishedAt,
            ]
        );

        if ($incident->assigned_to) {
            Alert::query()->create([
                'incident_id' => $incident->id,
                'recipient_user_id' => $incident->assigned_to,
                'channel' => 'EMAIL',
                'priority' => strtoupper($validated['severity'] ?? 'HIGH'),
                'status' => 'SENT',
                'message' => 'Incidente detectado: '.$incident->title,
                'sent_at' => now(),
            ]);
        }

        $execution->rpa?->forceFill(['last_execution_at' => $finishedAt])->save();

        return $this->success([
            'execution' => $execution->fresh(),
            'incident_id' => $incident->id,
        ], 'Fallo registrado correctamente.');
    }

    private function normalizeIncidentCategory(?string $category): string
    {
        return match (strtoupper(trim((string) $category))) {
            'CONNECTION', 'CONEXION' => 'CONNECTION',
            'CREDENTIALS', 'CREDENCIALES' => 'CREDENTIALS',
            'DATA', 'DATOS' => 'DATA',
            'INTERFACE', 'INTERFAZ' => 'INTERFACE',
            'TIMEOUT' => 'TIMEOUT',
            'DATABASE', 'BASE_DE_DATOS' => 'DATABASE',
            'BUSINESS_RULE', 'REGLA_NEGOCIO', 'SIMULADO', 'SIMULATION', 'GENERAL' => 'BUSINESS_RULE',
            default => 'UNKNOWN',
        };
    }

    private function resolveAgent(Request $request): RpaAgent
    {
        $token = $request->bearerToken();

        abort_unless($token, Response::HTTP_UNAUTHORIZED, 'Token de agente no enviado.');

        $agent = RpaAgent::query()
            ->where('is_active', true)
            ->get()
            ->first(fn (RpaAgent $item) => $this->agentTokenMatches($token, $item->api_key_hash));

        abort_unless($agent, Response::HTTP_UNAUTHORIZED, 'Token de agente invalido.');

        return $agent;
    }

    private function agentTokenMatches(string $token, ?string $storedHash): bool
    {
        if (! $storedHash) {
            return false;
        }

        try {
            if (Hash::check($token, $storedHash)) {
                return true;
            }
        } catch (Throwable) {
        }

        if (hash_equals($storedHash, $token)) {
            return true;
        }

        if (preg_match('/^[a-f0-9]{32}$/i', $storedHash) === 1) {
            return hash_equals(strtolower($storedHash), md5($token));
        }

        if (preg_match('/^[a-f0-9]{40}$/i', $storedHash) === 1) {
            return hash_equals(strtolower($storedHash), sha1($token));
        }

        return false;
    }

    private function guardExecutionOwnership(RpaExecution $execution, RpaAgent $agent): void
    {
        abort_unless($execution->agent_id === $agent->id, Response::HTTP_FORBIDDEN, 'La ejecucion no pertenece al agente autenticado.');
    }
}
