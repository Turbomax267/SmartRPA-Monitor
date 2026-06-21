<?php

namespace App\Http\Controllers\Api;

use App\Services\DashboardService;
use Illuminate\Http\JsonResponse;

class DashboardController extends ApiController
{
    public function __construct(private readonly DashboardService $dashboardService)
    {
    }

    public function summary(): JsonResponse
    {
        return $this->success(
            $this->dashboardService->getSummary(),
            'Resumen del dashboard obtenido correctamente.'
        );
    }
}
