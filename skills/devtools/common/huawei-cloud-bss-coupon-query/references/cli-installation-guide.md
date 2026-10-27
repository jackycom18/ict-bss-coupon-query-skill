# CLI Installation and Authentication

## KooCLI

Install a KooCLI 7.x release from the official Huawei Cloud KooCLI page and run
`hcloud configure list` to confirm that a protected profile is available.

Never write AK/SK values into this skill or pass them as command-line literals.

## Quality CLI

Run the idempotent installer:

```bash
bash scripts/ensure_cli.sh
```

If the automatic installer is unavailable, run:

```bash
bash scripts/install_cli.sh
```

Manual upgrade:

```bash
skill-quality-cli upgrade
```

Disable optional telemetry:

```bash
export SKILL_QUALITY_REPORT=0
```

## Required Profile

The active profile needs read-only BSS access. Use `cn-north-1` for the
`ListSubCustomerCoupons` operation.
