<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AiAnalysis extends Model
{
    use HasFactory;

    protected $fillable = [
        'incident_id',
        'provider',
        'model_name',
        'classification',
        'confidence',
        'probable_cause',
        'recommendation',
        'sanitized_log',
        'raw_response',
    ];

    protected $casts = [
        'confidence' => 'decimal:2',
        'raw_response' => 'array',
    ];

    public function incident(): BelongsTo
    {
        return $this->belongsTo(Incident::class);
    }
}
