# IoTShield AI - Security Report
**SAFE SIMULATION ONLY – NO REAL RANSOMWARE IS RUNNING.**

Generated: 2026-11-20T21:59:34  |  Seed: 42  |  Simulated windows: 18

> All data in this report is SYNTHETIC simulation output from a dummy environment. It is not real network traffic and not evidence of real-world detection performance.

## Overview
- Devices: 4 | Healthy: 3 | Suspicious: 0 | Quarantined: 1 | Threat level: CONTAINED

## Devices
| ID | Name | Type | Address | Criticality | Status | Security |
|---|---|---|---|---|---|---|
| CAM-01 | Smart Security Camera | IoT | 10.10.1.11 | MEDIUM | ONLINE | HEALTHY |
| TEMP-01 | Smart Temperature Sensor | IoT | 10.10.1.12 | LOW | ONLINE | HEALTHY |
| PLC-01 | Industrial PLC | IIoT | 10.10.2.21 | HIGH | QUARANTINED | QUARANTINED |
| GW-01 | Industrial Network Gateway | IIoT infrastructure | 10.10.2.1 | HIGH | ONLINE | HEALTHY |

## Alerts
- 2026-11-20T21:59:33.403 | PLC-01 | tick 12 | RANSOMWARE_LIKE p=1.000 | risk HIGH | top features: file_rename_rate z=10.57; failed_connection_rate z=13.19; device_activity_score z=9.12

## Response history (virtual, reversible)
- 2026-11-20T21:59:33.426 | PLC-01 | QUARANTINE | approved by analyst (scripted approval) | High ransomware-like risk (approved)

## Blocked simulated events
- Total blocked simulated outbound connections: 182
- Total blocked simulated outbound bytes: 2,330,607

## Event log
- 2026-11-20T21:59:31.760 | tick 0 | - | INFO | SYSTEM | Environment reset (SCEN-002): 4 virtual devices ONLINE, dummy files restored.
- 2026-11-20T21:59:31.799 | tick 10 | - | INFO | TRAFFIC | Normal simulation: 10 windows generated for all devices
- 2026-11-20T21:59:33.233 | tick 11 | PLC-01 | HIGH | ATTACK | Safe ransomware-like SIMULATION started on PLC-01 (dummy files only)
- 2026-11-20T21:59:33.403 | tick 12 | PLC-01 | HIGH | ALERT | HIGH risk: RANSOMWARE_LIKE p=1.000, criticality=HIGH. Top features: file_rename_rate (z=10.57), failed_connection_rate (z=13.19), device_activity_score (z=9.12)
- 2026-11-20T21:59:33.404 | tick 12 | PLC-01 | HIGH | APPROVAL | Quarantine of PLC-01 requested - waiting for analyst approval
- 2026-11-20T21:59:33.426 | tick 12 | PLC-01 | HIGH | RESPONSE | PLC-01 QUARANTINED (virtual only) - approved by analyst (scripted approval). High ransomware-like risk (approved)
- 2026-11-20T21:59:33.437 | tick 13 | PLC-01 | MEDIUM | BLOCKED | [BLOCKED_BY_QUARANTINE] Blocked 36 simulated outbound connections (326,699 bytes) from quarantined PLC-01
- 2026-11-20T21:59:33.539 | tick 14 | PLC-01 | MEDIUM | BLOCKED | [BLOCKED_BY_QUARANTINE] Blocked 39 simulated outbound connections (375,830 bytes) from quarantined PLC-01
- 2026-11-20T21:59:33.719 | tick 15 | PLC-01 | MEDIUM | BLOCKED | [BLOCKED_BY_QUARANTINE] Blocked 17 simulated outbound connections (491,491 bytes) from quarantined PLC-01
- 2026-11-20T21:59:33.792 | tick 16 | PLC-01 | MEDIUM | BLOCKED | [BLOCKED_BY_QUARANTINE] Blocked 25 simulated outbound connections (342,380 bytes) from quarantined PLC-01
- 2026-11-20T21:59:33.861 | tick 17 | PLC-01 | MEDIUM | BLOCKED | [BLOCKED_BY_QUARANTINE] Blocked 26 simulated outbound connections (317,973 bytes) from quarantined PLC-01
- 2026-11-20T21:59:33.930 | tick 18 | PLC-01 | MEDIUM | BLOCKED | [BLOCKED_BY_QUARANTINE] Blocked 39 simulated outbound connections (476,234 bytes) from quarantined PLC-01

## Safety statement
Quarantine is a change of simulated state only. No real network, firewall, routing or device was modified. No real ransomware was used; only dummy files in the sandbox were renamed.
