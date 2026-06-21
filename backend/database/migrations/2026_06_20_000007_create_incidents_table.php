<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('incidents', function (Blueprint $table): void {
            $table->id();
            $table->string('code', 30)->unique();
            $table->foreignId('execution_id')->nullable()->constrained('rpa_executions')->nullOnDelete();
            $table->foreignId('rpa_id')->nullable()->constrained('rpas')->nullOnDelete();
            $table->foreignId('assigned_to')->nullable()->constrained('users')->nullOnDelete();
            $table->string('title', 180);
            $table->string('category', 30)->nullable();
            $table->string('severity', 20);
            $table->string('status', 20);
            $table->text('description')->nullable();
            $table->text('probable_cause')->nullable();
            $table->timestampTz('detected_at')->nullable();
            $table->timestampTz('resolved_at')->nullable();
            $table->text('resolution_notes')->nullable();
            $table->timestampTz('created_at')->nullable();
            $table->timestampTz('updated_at')->nullable();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('incidents');
    }
};
