<?php

namespace App\Http\Controllers\Api;

use App\Http\Requests\Auth\LoginRequest;
use App\Http\Resources\UserResource;
use App\Services\AuthService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class AuthController extends ApiController
{
    public function __construct(private readonly AuthService $authService)
    {
    }

    public function login(LoginRequest $request): JsonResponse
    {
        $payload = $this->authService->login($request->validated());

        return $this->success([
            'token' => $payload['token'],
            'token_type' => 'Bearer',
            'user' => new UserResource($payload['user']),
        ], 'Inicio de sesión exitoso.');
    }

    public function me(Request $request): JsonResponse
    {
        $user = $request->user()->load('role');

        return $this->success(new UserResource($user));
    }

    public function logout(Request $request): JsonResponse
    {
        $this->authService->logout($request);

        return $this->success(null, 'Cierre de sesión exitoso.', Response::HTTP_OK);
    }
}
