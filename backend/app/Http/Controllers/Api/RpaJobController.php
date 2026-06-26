<?php

namespace App\Http\Controllers\Api;

use App\Models\Rpa;
use App\Models\RpaAgent;
use App\Models\RpaJob;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;
use Throwable;

class RpaJobController extends ApiController
{
    public function index(Request $request): JsonResponse
    {
        $jobs = RpaJob::query()
            ->with(['agent:id,code,name', 'rpa:id,code,name', 'requester:id,name', 'execution:id,public_id,status'])
            ->when($request->filled('status'), fn ($query) => $query->where('status', $request->string('status')->value()))
            ->latest('requested_at')
            ->limit(100)
            ->get()
            ->map(fn (RpaJob $job) => $this->mapJob($job))
            ->values();

        return $this->success($jobs, 'Jobs obtenidos correctamente.');
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'agent_id' => ['nullable', 'exists:rpa_agents,id'],
            'rpa_id' => ['required', 'exists:rpas,id'],
            'command' => ['required', 'in:run,activate,deactivate'],
            'payload' => ['nullable', 'array'],
        ]);

        $rpa = Rpa::query()->with('defaultAgent')->findOrFail($validated['rpa_id']);
        $agentId = $validated['agent_id'] ?? $rpa->default_agent_id;

        abort_unless($agentId, Response::HTTP_UNPROCESSABLE_ENTITY, 'El RPA no tiene agente asignado.');

        $job = RpaJob::query()->create([
            'public_id' => (string) Str::uuid(),
            'agent_id' => $agentId,
            'rpa_id' => $rpa->id,
            'requested_by' => $request->user()?->id,
            'command' => $validated['command'],
            'status' => 'PENDING',
            'payload' => array_merge($validated['payload'] ?? [], [
                'rpa_code' => $rpa->code,
                'script_name' => $rpa->script_name,
            ]),
            'requested_at' => now(),
        ]);

        $job->load(['agent:id,code,name', 'rpa:id,code,name', 'requester:id,name']);

        return $this->success($this->mapJob($job), 'Job creado correctamente.', Response::HTTP_CREATED);
    }

    public function cancel(Request $request, RpaJob $job): JsonResponse
    {
        abort_if(in_array($job->status, ['SUCCESS', 'FAILED', 'CANCELLED'], true), Response::HTTP_UNPROCESSABLE_ENTITY, 'El job ya no se puede cancelar.');

        $job->forceFill([
            'status' => 'CANCELLED',
            'cancelled_at' => now(),
        ])->save();

        return $this->success($this->mapJob($job->fresh(['agent', 'rpa', 'requester', 'execution'])), 'Job cancelado correctamente.');
    }

    public function next(Request $request): JsonResponse
    {
        $agent = $this->resolveAgent($request);

        $job = RpaJob::query()
            ->with(['rpa:id,code,name,script_name,lifecycle_status', 'agent:id,code,name'])
            ->where('agent_id', $agent->id)
            ->where('status', 'PENDING')
            ->orderBy('requested_at')
            ->orderBy('id')
            ->first();

        return $this->success($job ? $this->mapJob($job) : null, 'Consulta de job realizada correctamente.');
    }

    public function take(Request $request, RpaJob $job): JsonResponse
    {
        $agent = $this->resolveAgent($request);
        $this->guardAgentJob($job, $agent);

        abort_if($job->status !== 'PENDING', Response::HTTP_UNPROCESSABLE_ENTITY, 'El job ya fue tomado.');

        $job->forceFill([
            'status' => 'TAKEN',
            'started_at' => now(),
        ])->save();

        return $this->success($this->mapJob($job->fresh(['agent', 'rpa', 'requester', 'execution'])), 'Job tomado correctamente.');
    }

    public function running(Request $request, RpaJob $job): JsonResponse
    {
        $agent = $this->resolveAgent($request);
        $this->guardAgentJob($job, $agent);

        abort_if(! in_array($job->status, ['TAKEN', 'RUNNING'], true), Response::HTTP_UNPROCESSABLE_ENTITY, 'El job no puede pasar a running.');

        $job->forceFill([
            'status' => 'RUNNING',
            'started_at' => $job->started_at ?? now(),
        ])->save();

        return $this->success($this->mapJob($job->fresh(['agent', 'rpa', 'requester', 'execution'])), 'Job marcado como running.');
    }

    public function success(Request $request, RpaJob $job): JsonResponse
    {
        $agent = $this->resolveAgent($request);
        $this->guardAgentJob($job, $agent);

        $validated = $request->validate([
            'execution_id' => ['nullable', 'exists:rpa_executions,id'],
            'result_message' => ['nullable', 'string'],
            'payload' => ['nullable', 'array'],
        ]);

        DB::transaction(function () use ($job, $validated): void {
            $job->forceFill([
                'status' => 'SUCCESS',
                'execution_id' => $validated['execution_id'] ?? $job->execution_id,
                'result_message' => $validated['result_message'] ?? $job->result_message,
                'payload' => array_merge($job->payload ?? [], $validated['payload'] ?? []),
                'finished_at' => now(),
            ])->save();

            $this->applyCommandSideEffects($job);
        });

        return $this->success($this->mapJob($job->fresh(['agent', 'rpa', 'requester', 'execution'])), 'Job completado correctamente.');
    }

    public function fail(Request $request, RpaJob $job): JsonResponse
    {
        $agent = $this->resolveAgent($request);
        $this->guardAgentJob($job, $agent);

        $validated = $request->validate([
            'execution_id' => ['nullable', 'exists:rpa_executions,id'],
            'error_message' => ['required', 'string'],
            'payload' => ['nullable', 'array'],
        ]);

        $job->forceFill([
            'status' => 'FAILED',
            'execution_id' => $validated['execution_id'] ?? $job->execution_id,
            'error_message' => $validated['error_message'],
            'payload' => array_merge($job->payload ?? [], $validated['payload'] ?? []),
            'finished_at' => now(),
        ])->save();

        return $this->success($this->mapJob($job->fresh(['agent', 'rpa', 'requester', 'execution'])), 'Job marcado como fallido.');
    }

    private function applyCommandSideEffects(RpaJob $job): void
    {
        if (! $job->rpa) {
            return;
        }

        if ($job->command === 'activate') {
            $job->rpa->forceFill(['lifecycle_status' => 'ACTIVE'])->save();

            return;
        }

        if ($job->command === 'deactivate') {
            $job->rpa->forceFill(['lifecycle_status' => 'INACTIVE'])->save();
        }
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

    private function guardAgentJob(RpaJob $job, RpaAgent $agent): void
    {
        abort_unless($job->agent_id === $agent->id, Response::HTTP_FORBIDDEN, 'El job no pertenece al agente autenticado.');
    }

    private function mapJob(RpaJob $job): array
    {
        return [
            'id' => $job->id,
            'publicId' => $job->public_id,
            'agentId' => $job->agent_id,
            'agentCode' => $job->agent?->code,
            'agentName' => $job->agent?->name,
            'rpaId' => $job->rpa_id,
            'rpaCode' => $job->payload['rpa_code'] ?? $job->rpa?->code,
            'rpaName' => $job->rpa?->name,
            'command' => $job->command,
            'status' => $job->status,
            'payload' => $job->payload ?? [],
            'executionId' => $job->execution_id,
            'executionPublicId' => $job->execution?->public_id,
            'resultMessage' => $job->result_message,
            'errorMessage' => $job->error_message,
            'requestedBy' => $job->requester?->name,
            'requestedAt' => optional($job->requested_at)->toIso8601String(),
            'startedAt' => optional($job->started_at)->toIso8601String(),
            'finishedAt' => optional($job->finished_at)->toIso8601String(),
        ];
    }
}
