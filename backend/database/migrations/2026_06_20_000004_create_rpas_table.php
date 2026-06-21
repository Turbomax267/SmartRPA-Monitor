<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('rpas', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('default_agent_id')->nullable()->constrained('rpa_agents')->nullOnDelete();
            $table->foreignId('responsible_user_id')->nullable()->constrained('users')->nullOnDelete();
            $table->string('code', 60)->unique();
            $table->string('name', 150);
            $table->string('process_name', 150);
            $table->text('description')->nullable();
            $table->string('script_name', 150);
            $table->string('execution_mode', 20);
            $table->string('schedule_expression', 100)->nullable();
            $table->string('lifecycle_status', 20)->default('ACTIVE');
            $table->timestampTz('last_execution_at')->nullable();
            $table->timestampTz('created_at')->nullable();
            $table->timestampTz('updated_at')->nullable();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('rpas');
    }
};
