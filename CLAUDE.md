# CLAUDE.md

## 项目概况

「二哥的Java进阶之路」内容仓库（VuePress 站点），主要工作是写公众号/网站技术文章。

## 作者与项目

- 作者：沉默王二（二哥），程序员，GitHub：https://github.com/itwanger
- 网站：javabetter.cn（本仓库的部署站点）、paicoding.com（技术派社区）
- 实战项目源码都在本地 `/Users/itwanger/Documents/GitHub/` 下，文章中涉及项目细节时直接读源码，不要凭空编造：
  - 技术派（`paicoding`）— 前后端分离的技术社区系统，即 paicoding.com
  - PaiCLI（`paicli`）— 对标 Claude Code 的 Java Agent 命令行工具
  - PaiAgent（`PaiAgent-one`）— LangGraph4j + Spring AI 的工作流编排平台
  - 派聪明（`PaiSmart`）— 基于 ES 混合搜索的 RAG 知识库
  - PaiFlow（`PaiFlow`）— 可视化 AI Agent 工作流编排平台，类 Dify/Coze/n8n
  - PmHub（`pmhub`）— 基于 SpringCloud & LLM 的智能项目管理系统

## 目录地图

- `docs/src/sidebar/itwanger/ai/` — AI 类文章
- `docs/src/sidebar/itwanger/qiuzhi/` — 求职/面试类文章
- `docs/src/ai/video/` — AI Agent 面试题的逐题答案文章（兼作视频口播素材）

## 常用命令

- `npm run sidebar:check` / `npm run sidebar:sync` — 校验/同步侧边栏配置
- `npm run images:cdn` — mdnice 图片转 CDN 链接
- 写作前先运行 `date "+%Y年%m月%d日"` 确认日期

## 写作工作流

1. 出选题/搜热点 → topic-research Skill；写 AI 文章 → ai-article Skill；求职文 → job-article Skill；口播稿 → video-script Skill
2. 侧边栏同步（`npm run sidebar:sync`）在部署到 javabetter.cn 时由用户统一处理，写完文章不需要主动执行
3. 抓取微信公众号等需登录/动态渲染页面：用 Chrome DevTools MCP 或 web-access Skill，不用 WebFetch

## 硬约束

- 文件名：小写字母 + 连字符，如 `my-tutorial.md`
- 书面用语，语义准确；技术论述不口语化
- 正文（含文章、帖子、评论等一切非代码文本）禁用半角双引号 `"`，一律用全角双引号 “”；代码块和行内代码不受此限制
- 模型相关数据以当前一代（Opus 4.8 / GPT-5.5）为准，禁止引用过时模型数据
