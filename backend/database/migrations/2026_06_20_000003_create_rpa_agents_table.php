<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('rpa_agents', function (Blueprint $table): void {
            $table->id();
            $table->string('code', 50)->unique();
            $table->string('name', 120);
            $table->string('hostname', 120);
            $table->ipAddress('ip_address')->nullable();
            $table->string('environment', 30);
            $table->string('version', 30);
            $table->string('connection_status', 20)->default('OFFLINE');
            $table->string('api_key_hash', 255)->nullable();
            $table->timestampTz('last_seen_at')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestampTz('created_at')->nullable();
            $table->timestampTz('updated_at')->nullable();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('rpa_agents');
    }
};
