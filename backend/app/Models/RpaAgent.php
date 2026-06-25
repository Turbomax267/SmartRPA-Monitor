<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class RpaAgent extends Model
{
    use HasFactory;

    protected $fillable = [
        'code',
        'name',
        'hostname',
        'ip_address',
        'environment',
        'version',
        'connection_status',
        'api_key_hash',
        'last_seen_at',
        'is_active',
    ];

    protected $casts = [
        'last_seen_at' => 'datetime',
        'is_active' => 'boolean',
    ];

    public function defaultRpas(): HasMany
    {
        return $this->hasMany(Rpa::class, 'default_agent_id');
    }

    public function jobs(): HasMany
    {
        return $this->hasMany(RpaJob::class, 'agent_id');
    }
}
