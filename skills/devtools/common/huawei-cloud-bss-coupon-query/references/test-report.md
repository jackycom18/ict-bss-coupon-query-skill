# Functional Test Report

- Skill: `huawei-cloud-bss-coupon-query`
- Test date: 2026-10-27
- Region: `cn-north-1`
- Environment: Windows 11, Python 3.14.6, KooCLI 7.3.12
- Credential handling: existing protected KooCLI profile; no credential value printed
- Cloud resource cost: 0 CNY

## Result Summary

| Metric | Value |
|---|---:|
| Executed cases | 8 |
| Passed | 8 |
| Failed | 0 |
| Created resources | 0 |
| Modified resources | 0 |
| Deleted resources | 0 |

## Test Cases

| ID | Case | Command | Result |
|---|---|---|---|
| TC-01 | Real BSS read-only query | `hcloud BSS ListSubCustomerCoupons --cli-region=cn-north-1 --limit=1` | PASS |
| TC-02 | List normalized coupons | `python scripts/query_coupons.py list --limit 5` | PASS |
| TC-03 | Available status filter | `python scripts/query_coupons.py list --status available --limit 5` | PASS |
| TC-04 | Expiring coupon warning | `python scripts/query_coupons.py expiring --days 30` | PASS |
| TC-05 | Usage analysis | `python scripts/query_coupons.py analyze` | PASS |
| TC-06 | JSON analysis output | `python scripts/query_coupons.py analyze --json` | PASS |
| TC-07 | Invalid limit rejection | `python scripts/query_coupons.py list --limit 101` | PASS: exit code 2 |
| TC-08 | Wrapper help smoke test | `bash scripts/test-cli-commands.sh --help` | PASS |

## Observed Results

- The real BSS query returned a valid response with `count` and `user_coupons`.
- Coupon identifiers were masked before output.
- The status filter returned only the requested state.
- The expiry command correctly applied the 30-day warning window.
- The analysis output contained count, face value, balance, used value,
  utilization percentage, and status distribution.
- The negative case returned exit code 2 with a range validation message.
- No cloud resource was created, modified, or deleted.

## Additional Validation

The official skill-creator validator reported:

- Critical failures: 0
- High-priority failures: 0
- Warnings: 2

The warnings state that PyYAML is not installed and that the quality-wrapped
CLI command is not recognized as a bare KooCLI command. Both are environment
parser limitations; all executable read-only cases passed.

## Conclusion

All functional cases passed against the real BSS API. The skill is ready for
security audit and submission.
