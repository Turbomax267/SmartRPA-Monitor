<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class DashboardSummaryTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        $this->seed();
    }

    public function test_dashboard_summary_requires_authentication(): void
    {
        $this->getJson('/api/dashboard/summary')
            ->assertUnauthorized();
    }

    public function test_dashboard_summary_returns_expected_structure(): void
    {
        $user = User::query()->where('email', env('ADMIN_EMAIL', 'admin@smartrpa.local'))->firstOrFail();

        $response = $this->actingAs($user, 'sanctum')->getJson('/api/dashboard/summary');

        $response->assertOk()
            ->assertJsonPath('success', true)
            ->assertJsonStructure([
                'success',
                'message',
                'data' => [
                    'total_rpas',
                    'active_rpas',
                    'inactive_rpas',
                    'under_review_rpas',
                    'total_executions',
                    'success_rate',
                    'detected_errors',
                    'average_duration_ms',
                    'executions_by_day',
                    'errors_by_category',
                    'latest_executions',
                ],
            ]);
    }
}
