#!/usr/bin/env python3
"""Read-only Huawei Cloud BSS coupon query and analysis."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any


# The generated skill name is also used by the quality-reporting wrapper.
SKILL_NAME = "huawei-cloud-bss-coupon-query"
# BSS is a global service and uses the cn-north-1 gateway.
DEFAULT_REGION = "cn-north-1"
# BSS list APIs accept at most 100 items per request.
MAX_PAGE_SIZE = 100
# STATUS_LABELS translates numeric BSS coupon states into stable keys and Chinese labels.
STATUS_LABELS = {
    1: ("inactive", "未激活"),
    2: ("available", "待使用"),
    3: ("used", "已使用"),
    4: ("expired", "已过期"),
    5: ("recycled", "已回收"),
}
STATUS_KEYS = {
    "inactive": 1,
    "available": 2,
    "used": 3,
    "expired": 4,
    "recycled": 5,
}


def parse_iso_utc(value: Any) -> datetime | None:
    """功能：将 BSS 返回的 ISO 时间转换为 UTC 时间。

    输入：value 为字符串时间，通常以 Z 结尾；空值或非法值也可传入。
    输出：成功时返回带时区的 datetime，失败或空值时返回 None。
    """
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def days_until(value: Any) -> int | None:
    """功能：计算时间距离当前 UTC 时间还有多少天。

    输入：value 为待计算的 ISO 时间。
    输出：向上取整的非负天数；无有效时间时返回 None，已过期时返回 0。
    """
    target = parse_iso_utc(value)
    if target is None:
        return None
    remaining_seconds = (target - datetime.now(timezone.utc)).total_seconds()
    return max(0, math.ceil(remaining_seconds / 86400))


def mask_identifier(value: Any) -> str:
    """功能：脱敏代金券标识，避免测试报告泄露完整券号。

    输入：value 为 BSS 返回的 coupon_id。
    输出：仅保留末 4 位的脱敏字符串；空值返回空字符串。
    """
    text = str(value or "")
    if not text:
        return ""
    return f"****{text[-4:]}"


def run_hcloud(arguments: list[str]) -> dict[str, Any]:
    """功能：通过可选的 quality wrapper 执行只读 hcloud 并解析 JSON。

    输入：arguments 为 hcloud BSS 操作参数，不含可执行文件名。
    输出：解析后的 JSON 对象；执行失败或输出非法时抛出 RuntimeError。
    """
    hcloud = shutil.which("hcloud")
    if not hcloud:
        raise RuntimeError("hcloud was not found in PATH")

    quality_cli = shutil.which("skill-quality-cli")
    command = [hcloud, *arguments]
    if quality_cli:
        command = [
            quality_cli,
            "run",
            "--skill-name",
            SKILL_NAME,
            "--",
            *command,
        ]

    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=45,
        )
        return json.loads(completed.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError) as exc:
        details = getattr(exc, "stderr", "") or str(exc)
        raise RuntimeError(f"hcloud query failed: {details.strip()}") from exc


def fetch_page(
    offset: int,
    limit: int,
    status: int | None = None,
    coupon_id: str = "",
) -> dict[str, Any]:
    """功能：查询一页 BSS 代金券。

    输入：offset 为起始偏移；limit 为 1~100 的页大小；status 为可选状态码；
          coupon_id 为可选券号筛选。
    输出：BSS 原始 JSON 对象。
    """
    arguments = [
        "BSS",
        "ListSubCustomerCoupons",
        f"--cli-region={DEFAULT_REGION}",
        f"--offset={offset}",
        f"--limit={limit}",
    ]
    if status is not None:
        arguments.append(f"--status={status}")
    if coupon_id:
        arguments.append(f"--coupon_id={coupon_id}")
    return run_hcloud(arguments)


def fetch_all(status: int | None = None, coupon_id: str = "") -> tuple[int, list[dict[str, Any]]]:
    """功能：分页拉取全部满足条件的代金券。

    输入：status 为可选状态码；coupon_id 为可选券号筛选。
    输出：二元组（接口报告总数，代金券原始记录列表）。
    """
    offset = 0
    total = 0
    records: list[dict[str, Any]] = []
    for _ in range(100):
        page = fetch_page(offset, MAX_PAGE_SIZE, status, coupon_id)
        try:
            total = int(page.get("count", 0) or 0)
        except (TypeError, ValueError):
            total = 0
        items = page.get("user_coupons", []) or []
        records.extend(item for item in items if isinstance(item, dict))
        if not items or len(items) < MAX_PAGE_SIZE:
            break
        if total and len(records) >= total:
            break
        offset += len(items)
    return total, records


def normalize_coupon(coupon: dict[str, Any]) -> dict[str, Any]:
    """功能：将 BSS 原始记录转换为稳定、可展示的代金券结构。

    输入：coupon 为 BSS 单条代金券记录。
    输出：包含脱敏券号、状态、面额、余额和有效期的字典。
    """
    status_code = int(coupon.get("status", 0) or 0)
    status_key, status_label = STATUS_LABELS.get(status_code, ("unknown", "未知"))
    face_value = float(coupon.get("face_value", 0) or 0)
    balance_raw = coupon.get("balance")
    balance = face_value if balance_raw is None else float(balance_raw or 0)
    expire_time = coupon.get("expire_time", "")
    return {
        "coupon_id": mask_identifier(coupon.get("coupon_id")),
        "status": status_key,
        "status_label": status_label,
        "face_value": round(face_value, 2),
        "balance": round(balance, 2),
        "currency": coupon.get("currency", "CNY"),
        "valid_time": coupon.get("valid_time", ""),
        "expire_time": expire_time,
        "days_remaining": days_until(expire_time),
        "plan_name": coupon.get("plan_name") or "",
    }


def build_summary(coupons: list[dict[str, Any]]) -> dict[str, Any]:
    """功能：汇总代金券数量、金额、状态分布和使用率。

    输入：coupons 为归一化后的代金券列表。
    输出：统计字典，金额单位均为元。
    """
    face_total = round(sum(item["face_value"] for item in coupons), 2)
    balance_total = round(sum(item["balance"] for item in coupons), 2)
    used_value = round(sum(max(item["face_value"] - item["balance"], 0) for item in coupons), 2)
    status_counts: dict[str, int] = {}
    for item in coupons:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
    utilization = round((used_value / face_total * 100), 2) if face_total else 0.0
    return {
        "coupon_count": len(coupons),
        "face_value_total": face_total,
        "balance_total": balance_total,
        "used_value": used_value,
        "utilization_percent": utilization,
        "status_counts": status_counts,
    }


def print_coupons(coupons: list[dict[str, Any]], total: int) -> None:
    """功能：以单行格式展示代金券列表。

    输入：coupons 为归一化列表；total 为接口报告的总数。
    输出：无返回值，直接打印到标准输出。
    """
    print(f"total={total} displayed={len(coupons)}")
    for item in coupons:
        print(
            f"{item['coupon_id']} | {item['status']} ({item['status_label']}) | "
            f"face={item['face_value']:.2f} {item['currency']} | "
            f"balance={item['balance']:.2f} | "
            f"expire={item['expire_time']} | days={item['days_remaining']} | "
            f"plan={item['plan_name']}"
        )


def print_summary(summary: dict[str, Any]) -> None:
    """功能：以易读格式输代金券分析结果。

    输入：summary 为 build_summary 生成的统计字典。
    输出：无返回值，直接打印到标准输出。
    """
    print(f"coupon_count={summary['coupon_count']}")
    print(f"face_value_total={summary['face_value_total']:.2f}")
    print(f"balance_total={summary['balance_total']:.2f}")
    print(f"used_value={summary['used_value']:.2f}")
    print(f"utilization_percent={summary['utilization_percent']:.2f}")
    status_text = ", ".join(
        f"{key}={value}" for key, value in sorted(summary["status_counts"].items())
    )
    print(f"status_counts={status_text or 'none'}")


def build_parser() -> argparse.ArgumentParser:
    """功能：创建命令行参数解析器。

    输入：无。
    输出：配置完成的 argparse.ArgumentParser。
    """
    parser = argparse.ArgumentParser(description="Query Huawei Cloud BSS coupons (read-only)")
    subparsers = parser.add_subparsers(dest="action", required=True)

    list_parser = subparsers.add_parser("list", help="list coupons")
    list_parser.add_argument(
        "--status",
        choices=["all", *STATUS_KEYS.keys()],
        default="all",
        help="filter by coupon status",
    )
    list_parser.add_argument("--coupon-id", default="", help="full coupon ID filter")
    list_parser.add_argument("--limit", type=int, default=20, help="display limit, 1-100")
    list_parser.add_argument("--json", action="store_true", help="emit JSON")

    expiring_parser = subparsers.add_parser("expiring", help="list soon-expiring available coupons")
    expiring_parser.add_argument("--days", type=int, default=30, help="warning window, 1-365")
    expiring_parser.add_argument("--json", action="store_true", help="emit JSON")

    analyze_parser = subparsers.add_parser("analyze", help="summarize coupon usage")
    analyze_parser.add_argument("--json", action="store_true", help="emit JSON")
    return parser


def main() -> int:
    """功能：执行代金券查询、到期提醒和用量分析命令。

    输入：命令行参数，由 build_parser 定义。
    输出：进程退出码；0 表示成功，1 表示云接口失败，2 表示参数错误。
    """
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "list":
        if not 1 <= args.limit <= MAX_PAGE_SIZE:
            parser.error("--limit must be between 1 and 100")
        status = None if args.status == "all" else STATUS_KEYS[args.status]
    elif args.action == "expiring":
        if not 1 <= args.days <= 365:
            parser.error("--days must be between 1 and 365")
        status = STATUS_KEYS["available"]
    else:
        status = None

    try:
        total, raw_records = fetch_all(
            status=status,
            coupon_id=getattr(args, "coupon_id", ""),
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    coupons = [normalize_coupon(item) for item in raw_records]

    if args.action == "list":
        coupons = coupons[: args.limit]
        if args.json:
            print(json.dumps({"total": total, "coupons": coupons}, ensure_ascii=False, indent=2))
        else:
            print_coupons(coupons, total)
        return 0

    if args.action == "expiring":
        coupons = [
            item
            for item in coupons
            if item["status"] == "available"
            and item["balance"] > 0
            and item["days_remaining"] is not None
            and item["days_remaining"] <= args.days
        ]
        coupons.sort(key=lambda item: (item["days_remaining"], item["expire_time"]))
        if args.json:
            print(
                json.dumps(
                    {"days": args.days, "count": len(coupons), "coupons": coupons},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print_coupons(coupons, len(coupons))
        return 0

    summary = build_summary(coupons)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_summary(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
