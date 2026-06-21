<?php

namespace Database\Seeders;

use App\Models\Role;
use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class AdminUserSeeder extends Seeder
{
    public function run(): void
    {
        $role = Role::query()->where('name', 'ADMINISTRATOR')->firstOrFail();

        User::query()->updateOrCreate(
            ['email' => env('ADMIN_EMAIL', 'admin@smartrpa.local')],
            [
                'role_id' => $role->id,
                'name' => env('ADMIN_NAME', 'Administrador SmartRPA'),
                'password' => Hash::make(env('ADMIN_PASSWORD', 'SmartRPA123*')),
                'status' => 'ACTIVE',
            ]
        );
    }
}
