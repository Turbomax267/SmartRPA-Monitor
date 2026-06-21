<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;

class Incident extends Model
{
    use HasFactory;

    protected $fillable = [
        'code',
        'execution_id',
        'rpa_id',
        'assigned_to',
        'title',
        'category',
        'severity',
        'status',
        'description',
        'probable_cause',
        'detected_at',
        'resolved_at',
        'resolution_notes',
    ];

    protected $casts = [
        'detected_at' => 'datetime',
        'resolved_at' => 'datetime',
    ];

    public function execution(): BelongsTo
    {
        return $this->belongsTo(RpaExecution::class, 'execution_id');
    }

    public function rpa(): BelongsTo
    {
        return $this->belongsTo(Rpa::class);
    }

    public function assignedUser(): BelongsTo
    {
        return $this->belongsTo(User::class, 'assigned_to');
    }

    public function alerts(): HasMany
    {
        return $this->hasMany(Alert::class);
    }

    public function aiAnalysis(): HasOne
    {
        return $this->hasOne(AiAnalysis::class);
    }
}
