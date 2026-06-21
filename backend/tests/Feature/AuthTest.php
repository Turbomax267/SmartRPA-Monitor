<?php

namespace Tests\Feature;

use App\Models\Role;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Tests\TestCase;

class AuthTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        $this->seed();
    }

    public function test_user_can_login_successfully(): void
    {
        $response = $this->postJson('/api/auth/login', [
            'email' => env('ADMIN_EMAIL', 'admin@smartrpa.local'),
            'password' => env('ADMIN_PASSWORD', 'SmartRPA123*'),
        ]);

        $response->assertOk()
            ->assertJsonPath('success', true)
            ->assertJsonStructure([
                'success',
                'message',
                'data' => [
                    'token',
                    'token_type',
                    'user' => ['id', 'name', 'email', 'status', 'role'],
                ],
            ]);
    }

    public function test_login_fails_with_wrong_password(): void
    {
        $response = $this->postJson('/api/auth/login', [
            'email' => env('ADMIN_EMAIL', 'admin@smartrpa.local'),
            'password' => 'incorrecta',
        ]);

        $response->assertStatus(422)
            ->assertJsonPath('success', false);
    }

    public function test_inactive_user_cannot_login(): void
    {
        $role = Role::query()->firstWhere('name', 'PROCESS_MANAGER');

        User::query()->create([
            'role_id' => $role->id,
            'name' => 'Usuario Inactivo',
            'email' => 'inactive@smartrpa.local',
            'password' => Hash::make('SmartRPA123*'),
            'status' => 'INACTIVE',
        ]);

        $response = $this->postJson('/api/auth/login', [
            'email' => 'inactive@smartrpa.local',
            'password' => 'SmartRPA123*',
        ]);

        $response->assertStatus(403)
            ->assertJsonPath('success', false);
    }

    public function test_protected_route_requires_token(): void
    {
        $this->getJson('/api/auth/me')
            ->assertUnauthorized();
    }

    public function test_authenticated_user_can_be_retrieved(): void
    {
        $user = User::query()->where('email', env('ADMIN_EMAIL', 'admin@smartrpa.local'))->firstOrFail();

        $response = $this->actingAs($user, 'sanctum')->getJson('/api/auth/me');

        $response->assertOk()
            ->assertJsonPath('success', true)
            ->assertJsonPath('data.email', $user->email);
    }

    public function test_user_can_logout(): void
    {
        $user = User::query()->where('email', env('ADMIN_EMAIL', 'admin@smartrpa.local'))->firstOrFail();
        $token = $user->createToken('test_token');

        $response = $this->withToken($token->plainTextToken)->postJson('/api/auth/logout');

        $response->assertOk()
            ->assertJsonPath('success', true);
    }
}
