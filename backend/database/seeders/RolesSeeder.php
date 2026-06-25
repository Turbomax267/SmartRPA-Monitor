<?php

namespace Database\Seeders;

use App\Models\Role;
use Illuminate\Database\Seeder;

class RolesSeeder extends Seeder
{
    public function run(): void
    {
        $roles = [
            [
                'name' => 'ADMINISTRATOR',
                'display_name' => 'Administrador',
                'description' => 'Acceso total a la plataforma.',
            ],
            [
                'name' => 'RPA_TECHNICIAN',
                'display_name' => 'Tecnico RPA',
                'description' => 'Supervisa bots y ejecuciones.',
            ],
            [
                'name' => 'PROCESS_MANAGER',
                'display_name' => 'Gestor de Procesos',
                'description' => 'Gestiona procesos y seguimiento.',
            ],
        ];

        foreach ($roles as $role) {
            Role::query()->updateOrCreate(
                ['name' => $role['name']],
                $role + ['is_active' => true]
            );
        }
    }
}
