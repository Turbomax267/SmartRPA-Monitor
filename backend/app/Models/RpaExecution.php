<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;

class RpaExecution extends Model
{
    use HasFactory;

    protected $fillable = [
        'public_id',
        'rpa_id',
        'agent_id',
        'triggered_by',
        'trigger_type',
        'scenario',
        'status',
        'started_at',
        'finished_at',
        'duration_ms',
        'total_items',
        'successful_items',
        'failed_items',
        'result_summary',
        'error_code',
        'error_message',
        'metadata',
    ];

    protected $casts = [
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
        'metadata' => 'array',
    ];

    public function rpa(): BelongsTo
    {
        return $this->belongsTo(Rpa::class);
    }

    public function agent(): BelongsTo
    {
        return $this->belongsTo(RpaAgent::class, 'agent_id');
    }

    public function responsibleUser(): BelongsTo
    {
        return $this->belongsTo(User::class, 'triggered_by');
    }

    public function logs(): HasMany
    {
        return $this->hasMany(ExecutionLog::class, 'execution_id');
    }

    public function incident(): HasOne
    {
        return $this->hasOne(Incident::class, 'execution_id');
    }
}
