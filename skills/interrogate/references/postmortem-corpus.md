# Production Postmortem Failure Corpus

Audit every `Track M` and `Track L` design against these ten historical failure classes during Pre-Code Design Mode in `interrogate`.

| # | Failure Class | Real-World Precedents | Required Probe or Mechanical Defense |
| --- | --- | --- | --- |
| 1 | **Bad Global Config** | Cloudflare regex outage, Facebook backbone config, Fastly | Treat config as schema-validated code with canary waves, last-known-good local cache, and Static Stability. |
| 2 | **Downstream Gray Failure** | AWS DynamoDB or S3 partial stalls, GitHub DB slowdowns | Enforce per-attempt and total deadlines, per-dependency bulkheads, adaptive concurrency limits, and latency-triggered circuit breakers. |
| 3 | **Retry and Reconnect Amplification Storm** | AWS Kinesis or Cognito, Stripe, Slack reconnect storms | Enforce a client adaptive retry token bucket (`<= 10%` overhead), retry at one layer only with full jitter, and rate-limit reconnect handshakes. |
| 4 | **Cache Cold-Start** | Memcached or Redis cluster flush, simultaneous TTL expiry | Use `singleflight` or lease coalescing, jittered soft TTLs serving stale on upstream error, and backing-store admission control. |
| 5 | **Poison-Pill Input** | Catastrophic regex backtracking, Kafka consumer crash loops | Enforce ingress payload size and structural bounds, linear-time parsing, and Dead-Letter Queue quarantine after `N_max` attempts. |
| 6 | **Clock Drift** | Negative elapsed durations on NTP step or leap second | Use `CLOCK_MONOTONIC` for timeouts. Never order cross-node writes by wall clock without bounded-uncertainty wait (`2 * epsilon`) or monotonic fencing tokens. |
| 7 | **Asymmetric Network Partition** | Split-brain primary writes, zombie lease holders | Require quorum `ReadIndex` or bounded leases for reads, majority write quorums, and storage-checked monotonic fencing tokens. |
| 8 | **Storage Compaction** | Postgres TXID wraparound, RocksDB L0 compaction write stalls | Monitor freeze age and L0 file depth, bound row sizes, partition time-series tables for `DROP PARTITION`, and provision IOPS headroom. |
| 9 | **Hidden Resource Exhaustion** | Kubernetes conntrack full, NAT ephemeral port exhaustion, DNS drops | Size pools by Little's Law at degraded `p99`, reuse keep-alive connections, cache DNS locally with stale fallback, and emit USE saturation metrics. |
| 10 | **Rolling Deploy Wire Incompatibility** | Protobuf or JSON enum mismatch, destructive column rename | Enforce forward and backward additive compatibility verified by cross-version contract tests (`N-1` client against `N` server and reverse). |
