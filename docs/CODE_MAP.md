# 代码地图

> 最后更新：2026-10-27

## 总体结构

```text
bss-coupon-query-skill/
├─ .agents/skills/                 # 官方 creator/tester/audit
├─ skills/devtools/common/
│  └─ huawei-cloud-bss-coupon-query/  # 参赛 Skill
├─ reports/                        # 创建与安全审计报告
└─ docs/                           # 项目备忘与代码地图
```

## 模块职责

- `skills/devtools/common/huawei-cloud-bss-coupon-query/SKILL.md`：技能入口和使用规范。
- `scripts/query_coupons.py`：BSS 查询、脱敏、到期提醒和用量分析。
- `templates/test-vars.json`：真实测试用例。
- `references/`：IAM、安装、验证和验收文档。
- `reports/security-audit.txt`：官方安全审计结果。

## 逐文件核心内容

### `skills/devtools/common/huawei-cloud-bss-coupon-query/scripts/query_coupons.py`

- 用途：通过只读 KooCLI 查询并分析 BSS 代金券。
- 关键入口：`main()`、`fetch_all()`、`normalize_coupon()`、`build_summary()`。
- 数据流：KooCLI JSON → 归一化 → 脱敏 → 列表/到期/分析输出。
- 注意：不使用 shell 拼接，不读取凭据文件，不输出完整券号。
