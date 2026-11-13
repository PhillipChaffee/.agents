# Quantitative Envelope Reference

Run these equations before drawing system diagrams on `Track M` and `Track L` designs. Ground every throughput, storage, and concurrency choice in measured limits instead of guesses.

## Contents

- [Phase 0 feasibility checks](#phase-0-feasibility-checks)
- [Phase 1 capacity and queueing equations](#phase-1-capacity-and-queueing-equations)
- [2026 cloud hardware reference numbers](#2026-cloud-hardware-reference-numbers)
- [Runnable envelope calculator](#runnable-envelope-calculator)

## Phase 0 feasibility checks

1. **Serial availability.** Multiply synchronous dependency availabilities: `A_serial = prod(A_i)`. Reject any synchronous call chain whose product falls below the target SLO.
2. **Data Gravity and reversibility.** Estimate migration duration `T_migration = (D_bytes * WriteAmplification) / (B_sustained * (1 - rho_prod))`. If `T_migration` exceeds the recovery time objective, classify the decision as a Type-1 one-way door.

## Phase 1 capacity and queueing equations

1. **Peak QPS and bandwidth.** `QPS_design = QPS_avg * M_peak * M_safety`, and `BW = QPS_design * S_payload * Amplification`. Compare against network NIC and cross-AZ egress budgets.
2. **RUM Storage sizing (3-year).** `S_total(t) = (R_write * S_row * t) * (1 + IndexOverhead) * SA`. Balance Read, Update (`WA`), and Memory (`SA`) overhead along B-Tree (`SA ~ 1.3-1.5`) vs. LSM-Tree (`SA ~ 1.1-1.25`) trade-offs.
3. **Little's Law at degraded p99.** `L_max = lambda_peak * W_degraded_p99`. Always size connection pools, thread pools, and bounded channels using degraded tail latency, never median (`p50`) latency.
4. **Kingman queueing knee.** `E(W_q) ~ (rho / (1 - rho)) * ((c_a^2 + c_s^2) / 2) * tau`. Because `rho / (1 - rho)` explodes above `0.70` (`2.3x` at `0.70`, `9x` at `0.90`, `19x` at `0.95`), provision steady-state peak utilization `rho <= 0.70` on latency-sensitive paths.
5. **Universal Scalability Law.** `C(N) = N / (1 + alpha * (N - 1) + beta * N * (N - 1))`. When cross-node coordination (`beta > 0`) exists, throughput peaks at `N_max = floor(sqrt((1 - alpha) / beta))` and degrades above `N_max`.
6. **Tail-Latency Fan-Out.** `P(Root > T) = 1 - p^k` across `k` parallel leaf RPCs. A 50-way fan-out at `p = 0.99` puts `39.5%` of root requests in the `p99` tail unless mitigated by co-location or `p95` hedged requests.

## 2026 cloud hardware reference numbers

Baseline physical envelopes adapted from `sirupsen/napkin-math` (measured on AWS `m8i` and `m8g`, local NVMe, EBS, and S3 Express One Zone):

| Operation | Latency | Throughput or Cost Note |
| --- | --- | --- |
| L1, L2, and L3 cache read (64 B) | `2 ns`, `5 ns`, `50 ns` | `200 GiB/s`, `150 GiB/s`, `40 GiB/s` |
| DRAM random read and cross-socket NUMA | `100 ns` and `250 ns` | `20 GiB/s` (1 thread) to `200 GiB/s` (all cores) |
| Protobuf or JSON serialize and deserialize (256 B) | `200 ns` and `500 ns` | `2 GiB/s` and `500 MiB/s` (1 thread) |
| Local NVMe write (`pwrite` + `fdatasync`) and 8 KiB read | `30 us` and `100 us` | `3 GiB/s` write and `5 GiB/s` random read |
| Same-AZ and Cross-AZ network round-trip (32-64 KiB) | `100 us` and `500 us` | `3 GiB/s` (cross-AZ egress adds `$0.01-$0.02` per GB) |
| Network disk (EBS or Hyperdisk) zonal vs. regional | `500 us` vs. `1 ms` | `1 GiB/s` per volume |
| S3 Express One Zone read vs. conditional CAS write | `50 ms` vs. `100 ms` | Supports WAL-on-object-storage engines (`SlateDB`) |

## Runnable envelope calculator

Copy and adjust the input constants, then execute via `node -e` before writing `docs/designs/` or `docs/adr/`:

```javascript
const input = {
	qpsAvg: 1200,
	peakMultiplier: 3,
	safetyMultiplier: 1.5,
	payloadBytes: 2048,
	writeRatio: 0.3,
	years: 3,
	indexOverhead: 0.4,
	spaceAmplification: 1.25,
	degradedP99Sec: 0.25,
	uslAlpha: 0.02,
	uslBeta: 0.001,
	leafSuccessProb: 0.99,
	fanoutCount: 25,
	targetUtilizationRho: 0.65,
};

const qpsPeak = input.qpsAvg * input.peakMultiplier * input.safetyMultiplier;
const peakBandwidthMBps = Number(((qpsPeak * input.payloadBytes) / 1e6).toFixed(2));
const writesPerYear = input.qpsAvg * input.writeRatio * 365 * 86400;
const threeYearStorageTB = Number(
	((writesPerYear * input.years * input.payloadBytes * (1 + input.indexOverhead) * input.spaceAmplification) / 1e12).toFixed(3),
);
const littlesLawDegradedConcurrency = Math.ceil(qpsPeak * input.degradedP99Sec);
const kingmanMultiplier = Number((input.targetUtilizationRho / (1 - input.targetUtilizationRho)).toFixed(2));
const uslMaxNodes = input.uslBeta > 0 ? Math.floor(Math.sqrt((1 - input.uslAlpha) / input.uslBeta)) : Infinity;
const fanoutTailProbPct = Number(((1 - Math.pow(input.leafSuccessProb, input.fanoutCount)) * 100).toFixed(2));

console.log(
	JSON.stringify(
		{
			qpsPeak,
			peakBandwidthMBps,
			threeYearStorageTB,
			littlesLawDegradedConcurrency,
			kingmanMultiplier,
			uslMaxNodes,
			fanoutTailProbPct,
		},
		null,
		2,
	),
);
```
