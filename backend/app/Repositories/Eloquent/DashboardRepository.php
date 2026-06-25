<?php

namespace App\Repositories\Eloquent;

use App\Models\Incident;
use App\Models\Rpa;
use App\Models\RpaExecution;
use App\Repositories\Contracts\DashboardRepositoryInterface;
use Illuminate\Support\Facades\DB;

class DashboardRepository implements DashboardRepositoryInterface
{
    public function getSummary(): array
    {
        $totalRpas = Rpa::query()->count();
        $activeRpas = Rpa::query()->where('lifecycle_status', 'ACTIVE')->count();
        $inactiveRpas = Rpa::query()->where('lifecycle_status', 'INACTIVE')->count();
        $underReviewRpas = Rpa::query()->whereIn('lifecycle_status', ['UNDER_REVIEW', 'MAINTENANCE'])->count();

        $totalExecutions = RpaExecution::query()->count();
        $successfulExecutions = RpaExecution::query()->where('status', 'SUCCESS')->count();
        $detectedErrors = RpaExecution::query()->where('status', 'FAILED')->count() + Incident::query()->count();
        $averageDurationMs = (int) round((float) RpaExecution::query()->avg('duration_ms'));
        $successRate = $totalExecutions > 0 ? round(($successfulExecutions / $totalExecutions) * 100, 1) : 0.0;

        $executionsByDay = RpaExecution::query()
            ->selectRaw('DATE(started_at) as day')
            ->selectRaw('COUNT(*) as total')
            ->whereNotNull('started_at')
            ->groupBy('day')
            ->orderBy('day')
            ->limit(14)
            ->get()
            ->map(fn (RpaExecution $execution) => [
                'day' => $execution->day,
                'total' => (int) $execution->total,
            ])
            ->values()
            ->all();

        $errorsByCategory = Incident::query()
            ->select('category')
            ->selectRaw('COUNT(*) as total')
            ->groupBy('category')
            ->orderByDesc('total')
            ->get()
            ->map(fn (Incident $incident) => [
                'category' => $incident->category ?? 'Sin categoria',
                'total' => (int) $incident->total,
            ])
            ->values()
            ->all();

        $latestExecutions = RpaExecution::query()
            ->with(['rpa:id,name,process_name', 'responsibleUser:id,name'])
            ->latest('started_at')
            ->limit(5)
            ->get()
            ->map(fn (RpaExecution $execution) => [
                'id' => $execution->id,
                'rpa' => $execution->rpa?->name,
                'process' => $execution->rpa?->process_name,
                'status' => $execution->status,
                'duration_ms' => $execution->duration_ms,
                'responsible' => $execution->responsibleUser?->name,
                'started_at' => optional($execution->started_at)?->toIso8601String(),
            ])
            ->values()
            ->all();

        return [
            'total_rpas' => $totalRpas,
            'active_rpas' => $activeRpas,
            'inactive_rpas' => $inactiveRpas,
            'under_review_rpas' => $underReviewRpas,
            'total_executions' => $totalExecutions,
            'success_rate' => $successRate,
            'detected_errors' => $detectedErrors,
            'average_duration_ms' => $averageDurationMs,
            'executions_by_day' => $executionsByDay,
            'errors_by_category' => $errorsByCategory,
            'latest_executions' => $latestExecutions,
        ];
    }
}
