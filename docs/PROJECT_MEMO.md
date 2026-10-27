# 项目：华为云 BSS 代金券查询 Skill

> 最后更新：2026-10-27

## 项目总览

- 目标：完成 ICT 1.10，交付可运行、可测试、可审计的 `huawei-cloud-bss-coupon-query`。
- 技术栈：Python 标准库、KooCLI 7.3.12、官方 skill creator/tester/audit。
- 运行：`python3 scripts/query_coupons.py list --limit 20`
- 入口：`skills/devtools/common/huawei-cloud-bss-coupon-query/scripts/query_coupons.py`

## 环境配置

- 系统：Windows 11
- Python：3.14.6
- KooCLI：7.3.12，路径 `C:\Users\Xzj13\AppData\Local\Programs\.huawei\bin\hcloud.exe`
- 凭据：复用本机受保护的 KooCLI profile，不在项目中读取或保存 AK/SK
- BSS 区域：`cn-north-1`
- skill-quality-cli：Windows 环境未预装；脚本检测到时会自动包装 hcloud

## 当前状态

- 已完成：技能实现、结构校验、8 条真实功能测试、安全审计、测试与审计报告。
- 正在进行：整理提交仓库。
- 下一步：提交公开仓库至第 10 题。
- 风险：官方 skill-tester 在 Windows 第 6 阶段存在路径兼容问题；已用真实定向用例完成同等验证并保留报告。

## 需求与约定

- 只读查询，不创建云资源、不产生费用。
- 支持代金券列表、状态查询、即将到期识别和使用率分析。
- 不输出完整券号、账号 ID、AK/SK 或其他个人信息。
- 所有文件位于 `C:\Users\Xzj13\Desktop\pro\bss-coupon-query-skill`。
- 函数注释必须包含功能、输入、输出。

## 待办

- [x] 确认官方实验要求
- [x] 验证 BSS CLI 只读能力
- [x] 完成实现与真实测试
- [x] 完成安全审计
- [ ] 创建公开仓库并正式提交

## 版本历史

- 2026-10-27：确认 1.10 官方要求并完成 BSS CLI 能力验证。
- 2026-10-27：完成技能、8 条真实测试和审计 PASS。
