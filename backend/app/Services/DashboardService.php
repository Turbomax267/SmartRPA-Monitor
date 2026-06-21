<?php

namespace App\Services;

use App\Repositories\Contracts\DashboardRepositoryInterface;

class DashboardService
{
    public function __construct(private readonly DashboardRepositoryInterface $dashboardRepository)
    {
    }

    public function getSummary(): array
    {
        return $this->dashboardRepository->getSummary();
    }
}
