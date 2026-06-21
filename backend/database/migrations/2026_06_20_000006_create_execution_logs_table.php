<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('execution_logs', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('execution_id')->constrained('rpa_executions')->cascadeOnDelete();
            $table->integer('sequence_number');
            $table->string('level', 20);
            $table->string('step', 100)->nullable();
            $table->text('message');
            $table->string('error_code', 100)->nullable();
            $table->jsonb('context')->nullable();
            $table->timestampTz('occurred_at')->nullable();
            $table->timestampTz('created_at')->nullable();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('execution_logs');
    }
};
