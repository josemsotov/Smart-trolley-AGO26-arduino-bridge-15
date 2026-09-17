# Left-only normal velocity handler test

Suspended bench authorized by user. Three stages: equivalent feedforward
demands 15/20/25, 2-second ramp, command to second 8, 3-second zero rest.
Only left requested: linear=wheel_speed/2, angular=wheel_speed/0.82.
Isolated bridge retained 350ms command watchdog and firmware watchdog;
normal v handler, smooth PWM floor18, PI/heading/balance disabled. No q
fixed-filter diagnostic. Serial restart required reapplying the bench profile.

Analysis uses settled windows t=3..7.8, approximately 4.67 seconds each:

| Demand | Hall left | Opto left | Opto-Hall | Right Hall/opto |
|---|---:|---:|---:|---:|
| 15 | 134 | 125 | -9 (-6.72%) | 0/0 |
| 20 | 163 | 163 | 0 | 0/0 |
| 25 | 217 | 217 | 0 | 0/0 |

Demand is NOT constant applied PWM: below18 the profile pulse-modulates,
and startup uses a bounded boost. No claim of uniform encoder reliability.
At low demand opto undercount appears, unlike earlier powered diagnostic
overcounts. Cause not established. Next: repeat low-demand capture including
raw/accepted/rejected edge statistics to separate filtering from other causes.
Main service restored active; both motor PWM/RPM zero; bench runtime profile
reapplied after serial reopen. Raw data and summary retained alongside this file.
