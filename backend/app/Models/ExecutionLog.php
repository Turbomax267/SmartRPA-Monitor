<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ExecutionLog extends Model
{
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'execution_id',
        'sequence_number',
        'level',
        'step',
        'message',
        'error_code',
        'context',
        'occurred_at',
        'created_at',
    ];

    protected $casts = [
        'context' => 'array',
        'occurred_at' => 'datetime',
        'created_at' => 'datetime',
    ];

    public function execution(): BelongsTo
    {
        return $this->belongsTo(RpaExecution::class, 'execution_id');
    }
}
