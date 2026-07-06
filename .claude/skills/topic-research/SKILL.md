---
name: topic-research
description: 公众号选题调研。结合历史文章数据和 AI Coding 工具生态，找出当天能动手写的选题（实测/面试题/深度拆解优先）。当用户说"今天写什么"、"帮我调研选题"、"选题调研"时使用此 Skill。输出选题后可直接衔接 ai-article Skill 开写。
---

# 选题调研 Skill

目标：产出 **10 个今天就能动手写的候选选题**。

三条纲领（用户明确的方向要求，优先级高于一切细节）：

1. **追新闻热点**。尤其是互联网大厂，Codex、Claude Code、开源Agent相关、热门 AI 技术栈相关
2. **深度调研**。后期开启 subAgent 去调研话题

## 工作流程

### 第一步：调研（按顺序，全部内联执行）

**1. 工具盯梢 + 新品发现**（`references/tool-watchlist.md`）：

- 高 star、上升速度快的工具，尤其是 Claude Code、Codex、Agent 相关工具

**2. 同行公众号**（stealth-extract）：

- 看同行最近在写什么

**资源清理（硬规则）**：结果一收到立即关闭（TaskStop / session close），输出报告前自查无残留。

#### 同行公众号调研（stealth-extract）

- 博主清单：苍何、JavaGuide、stormzhang、赛博禅心、小林coding、cxuanAI、GitHubDaily、代码随想录、打工没有自由、宫水三叶的刷题日记、刘小排r、AI普瑞斯
- 每个博主至少 3 条进清单（标题+公众号名+日期）；

### 第六步：输出选题报告

**第一部分：情报清单**（每条带出处，供用户人工二次调研）：

```markdown
### GitHub
- 项目 | star | 一句话 | 链接

### 公众号
- 《标题》| 公众号名

### 互联网大厂信息
- 事件一句话| 公司 | 信源链接
```

**第二部分：候选**，每个包含：

```markdown
## 候选 N：选题方向一句话

- **为什么值得写**：热度信号 + 历史品类数据支撑（引用打开率）
- **推荐风格**：ai-article 四种风格选一（安装教程/产品评测/面试对话/深度拆解）
```
## 注意事项

- 历史数据复用 `../title-generator/references/title-data.md`，不另存副本
