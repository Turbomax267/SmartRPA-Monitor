<?php

namespace Database\Seeders;

use App\Models\Alert;
use App\Models\AiAnalysis;
use App\Models\ExecutionLog;
use App\Models\Incident;
use App\Models\IncidentFollowup;
use App\Models\Rpa;
use App\Models\RpaAgent;
use App\Models\RpaExecution;
use App\Models\Role;
use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class DemoDataSeeder extends Seeder
{
    public function run(): void
    {
        $technicianRole = Role::query()->firstWhere('name', 'RPA_TECHNICIAN');
        $managerRole = Role::query()->firstWhere('name', 'PROCESS_MANAGER');

        $technician = User::query()->firstOrCreate(
            ['email' => 'tecnico@smartrpa.local'],
            [
                'role_id' => $technicianRole?->id,
                'name' => 'Laura Rodriguez',
                'password' => bcrypt('SmartRPA123*'),
                'status' => 'ACTIVE',
            ]
        );

        $manager = User::query()->firstOrCreate(
            ['email' => 'manager@smartrpa.local'],
            [
                'role_id' => $managerRole?->id,
                'name' => 'Miguel Torres',
                'password' => bcrypt('SmartRPA123*'),
                'status' => 'ACTIVE',
            ]
        );

        $agentA = RpaAgent::query()->firstOrCreate(
            ['code' => 'AGENT-LIMA-01'],
            [
                'name' => 'Agente Lima',
                'hostname' => 'LIMA-RPA-01',
                'ip_address' => '192.168.1.10',
                'environment' => 'PRODUCTION',
                'version' => '1.0.0',
                'connection_status' => 'ONLINE',
                'api_key_hash' => Hash::make(env('AGENT_LIMA_01_TOKEN', 'agent-lima-01-token')),
                'is_active' => true,
                'last_seen_at' => now(),
            ]
        );

        $agentB = RpaAgent::query()->firstOrCreate(
            ['code' => 'AGENT-LIMA-02'],
            [
                'name' => 'Agente Soporte',
                'hostname' => 'LIMA-RPA-02',
                'ip_address' => '192.168.1.11',
                'environment' => 'PRODUCTION',
                'version' => '1.0.0',
                'connection_status' => 'OFFLINE',
                'api_key_hash' => Hash::make(env('AGENT_LIMA_02_TOKEN', 'agent-lima-02-token')),
                'is_active' => false,
            ]
        );

        $rpas = [
            ['code' => 'RPA-001', 'name' => 'Bot_Facturacion_Mensual', 'process_name' => 'Contabilidad', 'status' => 'ACTIVE', 'agent' => $agentA, 'user' => $technician],
            ['code' => 'RPA-002', 'name' => 'Bot_Conciliacion_Banco', 'process_name' => 'Finanzas', 'status' => 'ACTIVE', 'agent' => $agentA, 'user' => $manager],
            ['code' => 'RPA-003', 'name' => 'Bot_Reportes_RRHH', 'process_name' => 'RRHH', 'status' => 'ACTIVE', 'agent' => $agentA, 'user' => $technician],
            ['code' => 'RPA-004', 'name' => 'Bot_Registro_Proveedores', 'process_name' => 'Operaciones', 'status' => 'UNDER_REVIEW', 'agent' => $agentB, 'user' => $manager],
            ['code' => 'RPA-005', 'name' => 'Bot_Carga_Documental', 'process_name' => 'Archivo', 'status' => 'INACTIVE', 'agent' => $agentB, 'user' => $technician],
        ];

        foreach ($rpas as $index => $row) {
            $rpa = Rpa::query()->firstOrCreate(
                ['code' => $row['code']],
                [
                    'default_agent_id' => $row['agent']->id,
                    'responsible_user_id' => $row['user']->id,
                    'name' => $row['name'],
                    'process_name' => $row['process_name'],
                    'description' => 'Proceso automatizado del area '.$row['process_name'],
                    'script_name' => Str::slug($row['name'], '_').'.py',
                    'execution_mode' => 'SCHEDULED',
                    'schedule_expression' => '0 */2 * * *',
                    'lifecycle_status' => $row['status'],
                    'last_execution_at' => now()->subHours($index + 1),
                ]
            );

            for ($day = 13; $day >= 0; $day--) {
                $execution = RpaExecution::query()->create([
                    'public_id' => (string) Str::uuid(),
                    'rpa_id' => $rpa->id,
                    'agent_id' => $row['agent']->id,
                    'triggered_by' => $row['user']->id,
                    'trigger_type' => 'SCHEDULE',
                    'scenario' => 'Default',
                    'status' => $day % 5 === 0 && $index < 2 ? 'FAILED' : 'SUCCESS',
                    'started_at' => now()->subDays($day)->setHour(9 + $index)->setMinute(12),
                    'finished_at' => now()->subDays($day)->setHour(9 + $index)->setMinute(16),
                    'duration_ms' => 120000 + ($index * 10000) + ($day * 3000),
                    'total_items' => 100,
                    'successful_items' => $day % 5 === 0 && $index < 2 ? 82 : 100,
                    'failed_items' => $day % 5 === 0 && $index < 2 ? 18 : 0,
                    'result_summary' => 'Ejecucion registrada para dashboard.',
                    'error_code' => $day % 5 === 0 && $index < 2 ? 'TIMEOUT' : null,
                    'error_message' => $day % 5 === 0 && $index < 2 ? 'Se agoto el tiempo de espera.' : null,
                    'metadata' => ['source' => 'seeder'],
                ]);

                ExecutionLog::query()->create([
                    'execution_id' => $execution->id,
                    'sequence_number' => 1,
                    'level' => $execution->status === 'FAILED' ? 'ERROR' : 'INFO',
                    'step' => 'Inicio',
                    'message' => $execution->status === 'FAILED' ? 'Error de conectividad detectado.' : 'Ejecucion completada.',
                    'error_code' => $execution->error_code,
                    'context' => ['rpa' => $rpa->code],
                    'occurred_at' => $execution->finished_at,
                    'created_at' => $execution->finished_at,
                ]);

                if ($execution->status === 'FAILED' && ! Incident::query()->where('execution_id', $execution->id)->exists()) {
                    $incident = Incident::query()->create([
                        'code' => 'INC-'.Str::upper(Str::random(8)),
                        'execution_id' => $execution->id,
                        'rpa_id' => $rpa->id,
                        'assigned_to' => $technician->id,
                        'title' => 'Fallo en '.$rpa->name,
                        'category' => $index % 2 === 0 ? 'Timeout' : 'Conexion',
                        'severity' => 'HIGH',
                        'status' => 'OPEN',
                        'description' => 'Incidente detectado por el monitor.',
                        'probable_cause' => 'Intermitencia de red.',
                        'detected_at' => $execution->finished_at,
                    ]);

                    Alert::query()->create([
                        'incident_id' => $incident->id,
                        'recipient_user_id' => $manager->id,
                        'channel' => 'EMAIL',
                        'priority' => 'HIGH',
                        'status' => 'SENT',
                        'message' => 'Nuevo incidente detectado para '.$rpa->name,
                        'sent_at' => now()->subMinutes(15),
                    ]);

                    AiAnalysis::query()->create([
                        'incident_id' => $incident->id,
                        'provider' => 'INTERNAL',
                        'model_name' => 'rules-engine',
                        'classification' => 'Incidente de infraestructura',
                        'confidence' => 92.5,
                        'probable_cause' => 'Respuesta lenta del servicio dependiente.',
                        'recommendation' => 'Revisar latencia de red y reintentar.',
                        'sanitized_log' => 'Log saneado para revision.',
                        'raw_response' => ['label' => 'Timeout'],
                    ]);

                    IncidentFollowup::query()->create([
                        'incident_id' => $incident->id,
                        'user_id' => $technician->id,
                        'action_type' => 'CREATED',
                        'comment' => 'Incidente generado automaticamente.',
                        'status_before' => 'NEW',
                        'status_after' => 'OPEN',
                        'created_at' => now()->subMinutes(10),
                    ]);
                }
            }
        }
    }
}
