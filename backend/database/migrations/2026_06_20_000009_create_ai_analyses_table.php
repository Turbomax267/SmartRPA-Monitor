<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('ai_analyses', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('incident_id')->constrained('incidents')->cascadeOnDelete();
            $table->string('provider', 50);
            $table->string('model_name', 100)->nullable();
            $table->string('classification', 100)->nullable();
            $table->decimal('confidence', 5, 2)->nullable();
            $table->text('probable_cause')->nullable();
            $table->text('recommendation')->nullable();
            $table->text('sanitized_log')->nullable();
            $table->jsonb('raw_response')->nullable();
            $table->timestampTz('created_at')->nullable();
            $table->timestampTz('updated_at')->nullable();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('ai_analyses');
    }
};
