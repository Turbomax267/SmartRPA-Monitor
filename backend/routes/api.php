<?php

use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\AgentController;
use App\Http\Controllers\Api\DashboardController;
use App\Http\Controllers\Api\MonitorController;
use App\Http\Controllers\Api\RpaJobController;
use Illuminate\Support\Facades\Route;

Route::prefix('auth')->group(function (): void {
    Route::post('/login', [AuthController::class, 'login']);

    Route::middleware('auth:sanctum')->group(function (): void {
        Route::post('/logout', [AuthController::class, 'logout']);
        Route::get('/me', [AuthController::class, 'me']);
    });
});

Route::middleware('auth:sanctum')->group(function (): void {
    Route::get('/dashboard/summary', [DashboardController::class, 'summary']);
    Route::get('/rpas', [MonitorController::class, 'rpas']);
    Route::get('/rpas/{rpa}', [MonitorController::class, 'rpa']);
    Route::patch('/rpas/{rpa}/status', [MonitorController::class, 'updateRpaStatus']);
    Route::get('/executions', [MonitorController::class, 'executions']);
    Route::get('/executions/{execution}', [MonitorController::class, 'execution']);
    Route::get('/incidents', [MonitorController::class, 'incidents']);
    Route::get('/incidents/{incident}', [MonitorController::class, 'incident']);
    Route::get('/ai-analyses/{analysis}', [MonitorController::class, 'analysis']);
    Route::get('/metrics/summary', [MonitorController::class, 'metrics']);
    Route::get('/settings', [MonitorController::class, 'settings']);
    Route::get('/users', [MonitorController::class, 'users']);
    Route::post('/users', [MonitorController::class, 'storeUser']);
    Route::get('/roles', [MonitorController::class, 'roles']);
    Route::get('/jobs', [RpaJobController::class, 'index']);
    Route::post('/jobs', [RpaJobController::class, 'store']);
    Route::post('/jobs/{job}/cancel', [RpaJobController::class, 'cancel']);
});

Route::prefix('agent')->group(function (): void {
    Route::post('/heartbeat', [AgentController::class, 'heartbeat']);
    Route::post('/executions/start', [AgentController::class, 'start']);
    Route::post('/executions/{execution}/logs', [AgentController::class, 'log']);
    Route::post('/executions/{execution}/complete', [AgentController::class, 'complete']);
    Route::post('/executions/{execution}/fail', [AgentController::class, 'fail']);
    Route::get('/jobs/next', [RpaJobController::class, 'next']);
    Route::post('/jobs/{job}/take', [RpaJobController::class, 'take']);
    Route::post('/jobs/{job}/running', [RpaJobController::class, 'running']);
    Route::post('/jobs/{job}/success', [RpaJobController::class, 'complete']);
    Route::post('/jobs/{job}/fail', [RpaJobController::class, 'fail']);
});
