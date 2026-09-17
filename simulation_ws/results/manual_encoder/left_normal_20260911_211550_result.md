# Low-demand repeat with opto diagnostics

Two left-only stages, demand15, unchanged smooth floor18 / 20ms profile,
PI/heading/balance off. Main service temporarily isolated and then restored.
Normal v path, not q fixed-filter diagnostic. No firmware changes.

| Complete stage including ramp/coast | Hall | Opto raw | Accepted | Rejected |
|---|---:|---:|---:|---:|
| 1 | 217 | 277 | 208 | 69 |
| 2 | 216 | 277 | 207 | 70 |

Settled windows t=3..7.8: both repeats Hall134 / opto126 (~4.69s), -5.97%.
Right Hall/opto/raw all zero. Raw means counted ISR edges, not independently
verified physical slots. Excess raw edges and accepted deficit coexist; cannot
identify each rejected edge as noise or valid without timing/waveform evidence.
Final adaptive thresholds 22585us and 22259us are post-coast snapshots,
not assumed constant during movement. Full sampled j STAT retained in JSON.

Conclusion: low-demand discrepancy reproduced twice. Investigate filter timing
with one-variable bounded A/B before choosing any permanent change. The Hall
reference itself is filtered and is not absolute ground truth.
