# Huawei Cloud BSS Coupon Query Skill

This repository contains the ICT 1.10 work for
`huawei-cloud-bss-coupon-query`, a read-only Huawei Cloud BSS skill.

## Features

- List account coupons.
- Filter by coupon status.
- Report coupons that expire within a configurable window.
- Analyze count, face value, remaining balance, and utilization.
- Mask coupon identifiers and never print credentials.

## Skill Location

```text
skills/devtools/common/huawei-cloud-bss-coupon-query/
```

## Quick Start

```powershell
python -X utf8 scripts/query_coupons.py list --limit 5
python -X utf8 scripts/query_coupons.py expiring --days 30
python -X utf8 scripts/query_coupons.py analyze
```

Run the commands from the skill directory. The underlying operation is the
read-only KooCLI command:

```text
hcloud BSS ListSubCustomerCoupons --cli-region=cn-north-1
```

## Deliverables

- [Functional test report](skills/devtools/common/huawei-cloud-bss-coupon-query/references/test-report.md)
- [Security audit report](reports/security-audit.txt)
- [Creation report](reports/creation-report.md)
- [Project memo](docs/PROJECT_MEMO.md)
- [Code map](docs/CODE_MAP.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

## Safety

- No cloud resources are created.
- No coupon is claimed, deducted, transferred, or deleted.
- No AK/SK, token, password, account ID, or full coupon ID is stored.
