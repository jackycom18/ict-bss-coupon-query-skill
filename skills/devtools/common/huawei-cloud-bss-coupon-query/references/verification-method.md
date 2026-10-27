# Verification Method

## 1. Credential Profile

```bash
skill-quality-cli run --skill-name huawei-cloud-bss-coupon-query -- hcloud configure list
```

Verify the profile exists without printing credentials.

## 2. Real Read-Only API Call

```bash
skill-quality-cli run --skill-name huawei-cloud-bss-coupon-query -- hcloud BSS ListSubCustomerCoupons --cli-region=cn-north-1 --limit=1
```

Expected: JSON containing `count` and `user_coupons`.

## 3. Functional Cases

```bash
python3 scripts/query_coupons.py list --limit 5
python3 scripts/query_coupons.py list --status available --limit 5
python3 scripts/query_coupons.py expiring --days 30
python3 scripts/query_coupons.py analyze
```

Expected: only masked coupon identifiers are displayed; status filters and
summary values are internally consistent.

## 4. Negative Case

```bash
python3 scripts/query_coupons.py list --limit 101
```

Expected: exit code 2 and a range validation error.

## 5. Structure Validation

Use the installed skill creator validator:

```bash
bash scripts/validate-skill.sh -s ../huawei-cloud-bss-coupon-query
```
