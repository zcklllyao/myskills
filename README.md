# myskills

个人 AI Agent 技能集合。每个子目录是一个独立技能（遵循 `SKILL.md` + 脚本的技能规范），可直接挂载到支持 Skills 的 Agent（如 OpenCode、Claude Code 等）使用。

## 技能列表

| 技能 | 简介 |
|------|------|
| [build-paper-reports](./build-paper-reports) | 论文研读报告：按论文列表搜索/下载 PDF、校验完整性、逐篇精读，产出一篇篇有据可依的中文 Markdown 报告，支持提交回 Git 仓库 |
| [foreign-company-due-diligence](./foreign-company-due-diligence) | 外企背调：基于公开可核验信息评估海外公司（B2B 销售 / 供应商 / 合作 / 信用场景），输出带证据等级的尽调报告与行动建议 |
| [training-log-visualization](./training-log-visualization) | 训练日志可视化：从 torchtitan / torchtitan-npu 日志按 step 提取 loss / grad_norm / memory / tps / mfu 等指标绘图，支持双日志对比与误差曲线 |

## 使用方式

将本仓库克隆到 Agent 的技能目录（如 `.agents/skills/`），Agent 会根据对话内容自动匹配触发对应技能，也可在对话中直接点名调用。

```bash
git clone https://github.com/zcklllyao/myskills.git .agents/skills/myskills
```
