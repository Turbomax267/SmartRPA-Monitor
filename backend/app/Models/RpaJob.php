<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class RpaJob extends Model
{
    use HasFactory;

    protected $fillable = [
        'public_id',
        'agent_id',
        'rpa_id',
        'requested_by',
        'execution_id',
        'command',
        'status',
        'payload',
        'result_message',
        'error_message',
        'requested_at',
        'started_at',
        'finished_at',
        'cancelled_at',
    ];

    protected $casts = [
        'payload' => 'array',
        'requested_at' => 'datetime',
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
        'cancelled_at' => 'datetime',
    ];

    public function agent(): BelongsTo
    {
        return $this->belongsTo(RpaAgent::class, 'agent_id');
    }

    public function rpa(): BelongsTo
    {
        return $this->belongsTo(Rpa::class);
    }

    public function requester(): BelongsTo
    {
        return $this->belongsTo(User::class, 'requested_by');
    }

    public function execution(): BelongsTo
    {
        return $this->belongsTo(RpaExecution::class, 'execution_id');
    }
}
