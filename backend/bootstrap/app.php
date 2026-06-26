<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Auth\AuthenticationException;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpFoundation\Response;
use Throwable;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        api: __DIR__.'/../routes/api.php',
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->append(\Illuminate\Http\Middleware\HandleCors::class);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->shouldRenderJsonWhen(
            fn (Request $request) => $request->is('api/*'),
        );

        $exceptions->render(function (ValidationException $exception, Request $request) {
            if (! $request->is('api/*')) {
                return null;
            }

            return response()->json([
                'success' => false,
                'message' => $exception->status === Response::HTTP_FORBIDDEN
                    ? 'No tienes acceso para realizar esta acción.'
                    : 'No se pudo completar la operación.',
                'errors' => $exception->errors(),
            ], $exception->status);
        });

        $exceptions->render(function (AuthenticationException $exception, Request $request) {
            if (! $request->is('api/*')) {
                return null;
            }

            return response()->json([
                'success' => false,
                'message' => 'No autenticado.',
                'errors' => [],
            ], Response::HTTP_UNAUTHORIZED);
        });

        $exceptions->report(function (Throwable $exception) {
            Log::error('Excepcion no controlada en API.', [
                'type' => $exception::class,
                'message' => $exception->getMessage(),
                'file' => $exception->getFile(),
                'line' => $exception->getLine(),
                'trace' => $exception->getTraceAsString(),
            ]);
        });

        $exceptions->render(function (Throwable $exception, Request $request) {
            if (! $request->is('api/*')) {
                return null;
            }

            $payload = [
                'success' => false,
                'message' => 'Ocurrio un error interno en la API.',
                'errors' => [],
            ];

            if ($request->is('api/agent/*')) {
                $payload['debug'] = [
                    'type' => $exception::class,
                    'message' => $exception->getMessage(),
                ];
            }

            return response()->json($payload, Response::HTTP_INTERNAL_SERVER_ERROR);
        });
    })->create();
