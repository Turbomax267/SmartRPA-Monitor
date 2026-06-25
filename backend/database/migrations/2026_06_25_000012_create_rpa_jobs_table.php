<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('rpa_jobs', function (Blueprint $table): void {
            $table->id();
            $table->uuid('public_id')->unique();
            $table->foreignId('agent_id')->constrained('rpa_agents')->cascadeOnDelete();
            $table->foreignId('rpa_id')->nullable()->constrained('rpas')->nullOnDelete();
            $table->foreignId('requested_by')->nullable()->constrained('users')->nullOnDelete();
            $table->foreignId('execution_id')->nullable()->constrained('rpa_executions')->nullOnDelete();
            $table->string('command', 20);
            $table->string('status', 20)->default('PENDING');
            $table->json('payload')->nullable();
            $table->text('result_message')->nullable();
            $table->text('error_message')->nullable();
            $table->timestampTz('requested_at')->nullable();
            $table->timestampTz('started_at')->nullable();
            $table->timestampTz('finished_at')->nullable();
            $table->timestampTz('cancelled_at')->nullable();
            $table->timestampTz('created_at')->nullable();
            $table->timestampTz('updated_at')->nullable();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('rpa_jobs');
    }
};
