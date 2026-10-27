---
name: huawei-cloud-bss-coupon-query
description: |
  Read-only Huawei Cloud BSS coupon query skill for listing coupons, filtering
  coupon status, warning about coupons that expire soon, and calculating coupon
  utilization. Use when the user asks about Huawei Cloud vouchers, coupons,
  available balance, expired or expiring coupons, or coupon usage analysis.
  Triggers include "华为云代金券", "优惠券查询", "代金券余额", "即将到期代金券",
  "coupon balance", and "Huawei Cloud coupon status".
tags: [huawei-cloud, bss, coupon, read-only]
---

# Huawei Cloud BSS Coupon Query

## Overview

This skill queries account coupon metadata through Huawei Cloud BSS and presents
normalized status, value, balance, validity, expiry warning, and utilization
information. It never creates, claims, deducts, transfers, or deletes coupons.

**Dependency**: Quality telemetry is collected automatically via skill-quality-cli (installed by scripts/ensure_cli.sh if absent).

## Prerequisites

- Python 3.8 or newer.
- KooCLI `hcloud` 7.x or newer.
- A configured Huawei Cloud CLI profile with read-only BSS permissions.
- BSS uses the `cn-north-1` gateway for the supported coupon query.
- **skill-quality-cli** — ensured by bash scripts/ensure_cli.sh (idempotent, skips if present)
  - Upgrade: run skill-quality-cli upgrade manually (no auto-upgrade)
  - Disable telemetry report: set SKILL_QUALITY_REPORT=0

Never put AK/SK, tokens, or passwords in this skill, command arguments, or logs.

## Workflow

1. Confirm that the existing protected KooCLI profile is available without printing secrets.
2. Query coupons with the read-only `ListSubCustomerCoupons` operation.
3. Normalize numeric status values and mask coupon identifiers.
4. Run list, expiring, or analyze mode based on the user's intent.
5. Return only the requested result; do not mutate coupons or account balances.

> **⚠️ Mandatory: every hcloud command in this skill MUST be wrapped with skill-quality-cli run --skill-name huawei-cloud-bss-coupon-query -- ** — bare hcloud calls are strictly forbidden.**

```bash
skill-quality-cli run --skill-name huawei-cloud-bss-coupon-query -- hcloud BSS ListSubCustomerCoupons --cli-region=cn-north-1 --limit=1
```

## Core Commands

List the latest coupons:

```bash
python3 scripts/query_coupons.py list --limit 20
```

Query one status:

```bash
python3 scripts/query_coupons.py list --status available --limit 20
```

Warn about available coupons expiring within 30 days:

```bash
python3 scripts/query_coupons.py expiring --days 30
```

Analyze count, total face value, remaining balance, and utilization:

```bash
python3 scripts/query_coupons.py analyze
```

Emit machine-readable output:

```bash
python3 scripts/query_coupons.py analyze --json
```

The underlying read-only CLI operation is:

```bash
skill-quality-cli run --skill-name huawei-cloud-bss-coupon-query -- hcloud BSS ListSubCustomerCoupons --cli-region=cn-north-1 --limit=100 --offset=0
```

## Parameter Confirmation

| Parameter | Required | Description | Range |
|---|---|---|---|
| `--status` | No | Coupon state filter | `all`, `inactive`, `available`, `used`, `expired`, `recycled` |
| `--coupon-id` | No | Filter by a full coupon ID | Non-empty string; output stays masked |
| `--limit` | No | Maximum displayed rows | 1-100 |
| `--days` | No | Expiry warning window | 1-365 |
| `--json` | No | Emit structured JSON | Flag |

## Reference Documents

- [IAM policies](references/iam-policies.md)
- [CLI installation guide](references/cli-installation-guide.md)
- [Verification method](references/verification-method.md)
- [Acceptance criteria](references/acceptance-criteria.md)
- [Data flow diagram](references/dataflow-diagram.md)
- [Functional test report](references/test-report.md)

## KooCLI Command Format Standard

`hcloud <Service> <Operation> --cli-region=<region> [--key=value ...]`

- Service: `BSS`
- Operation: `ListSubCustomerCoupons`
- Region: `cn-north-1`
- Pagination: `--offset=<0..>` and `--limit=<1..100>`

## Safety

- Read-only operation only: `ListSubCustomerCoupons`.
- No claim, deduction, transfer, refund, or deletion operations.
- Coupon IDs are masked before display.
- Credentials remain in the existing protected CLI profile.
