<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Rpa extends Model
{
    use HasFactory;

    protected $fillable = [
        'default_agent_id',
        'responsible_user_id',
        'code',
        'name',
        'process_name',
        'description',
        'script_name',
        'execution_mode',
        'schedule_expression',
        'lifecycle_status',
        'last_execution_at',
    ];

    protected $casts = [
        'last_execution_at' => 'datetime',
    ];

    public function defaultAgent(): BelongsTo
    {
        return $this->belongsTo(RpaAgent::class, 'default_agent_id');
    }

    public function responsibleUser(): BelongsTo
    {
        return $this->belongsTo(User::class, 'responsible_user_id');
    }

    public function executions(): HasMany
    {
        return $this->hasMany(RpaExecution::class);
    }

    public function jobs(): HasMany
    {
        return $this->hasMany(RpaJob::class);
    }
}
