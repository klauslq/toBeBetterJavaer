# AI Coding 工具盯梢清单

选题调研第四步用。逐个查最近 48 小时有没有新 release / 新版本 / 重大更新，有就进热点池。

**清单是参考不是边界**：下面列的是已知的固定盯梢对象，**上升速度快的新品同样是重点对象**——每轮调研都要跑一遍"新品发现"（见下），发现值得长期盯的就加进清单。清单可随时增删，按用户指示维护。

## 新品发现（每轮必跑）

用 GitHub Search API 找最近两周创建、star 增长快的 AI 工具（天然满足"创建 2 周内"的时效校验）：

```bash
SINCE=$(date -v-14d "+%Y-%m-%d")
curl -s "https://api.github.com/search/repositories?q=created:%3E$SINCE+agent+OR+claude+OR+copilot+OR+coding+in:name,description,topics&sort=stars&order=desc&per_page=15" \
  | python3 -c "
import json,sys
for r in json.load(sys.stdin).get('items',[]):
    print(r['stargazers_count'], '|', r['full_name'], '|', r['created_at'][:10], '|', (r.get('description') or '')[:60])"
```

新建仓库 star 过千即值得关注，过五千基本必进热点池（对照历史爆款：Hermes Agent 40.4k、OpenHarness 3.9k、MiniMax Skills 7.8k 都出过高打开率文章）。

## 查法

GitHub 开源项目（批量查最新 release 的发布时间和版本号）：

```bash
for repo in anthropics/claude-code anomalyco/opencode openai/codex google-gemini/gemini-cli charmbracelet/crush Aider-AI/aider cline/cline; do
  curl -s "https://api.github.com/repos/$repo/releases/latest" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('$repo', '|', d.get('tag_name','无release'), '|', d.get('published_at','')[:10])"
done
```

闭源工具查官方 changelog / 博客（用 web-access）。
IDEA 插件查 JetBrains Marketplace（按更新时间）：

```bash
curl -s "https://plugins.jetbrains.com/api/searchPlugins?search=claude&max=10" | python3 -m json.tool | grep -E '"name"|"date"'
```

## 清单

### Claude Code 本体与竞品 CLI

| 工具 | 查什么 |
|---|---|
| Claude Code | anthropics/claude-code 的 releases + CHANGELOG.md，新功能是稳定选题 |
| opencode | anomalyco/opencode releases（原 sst/opencode，已迁移），开源 Claude Code 竞品，182k star |
| Codex CLI | openai/codex releases + OpenAI 官方博客 |
| Gemini CLI | google-gemini/gemini-cli releases |
| Crush | charmbracelet/crush releases，终端 UI 出众 |
| aider | Aider-AI/aider releases |
| DeepSeek TUI | DeepSeek 官方公告（曾写过，打开率 11.04%，有新版本可跟进） |
| Qoder | 官方 changelog（闭源，写过多篇，读者熟悉） |

### 终端工具

| 工具 | 查什么 |
|---|---|
| Warp | warp.dev/changelog + 官方博客，Agent 相关新功能优先 |
| 其他 | Trending 里冒头的新终端（按"创建 2 周内"规则过滤） |

### IntelliJ IDEA AI 插件

| 工具 | 查什么 |
|---|---|
| CC-GUI | 插件更新 + 仓库动态（写过 cc-gui-idea，读者有认知基础） |
| JetBrains AI Assistant / Junie | blog.jetbrains.com + 版本公告 |
| Marketplace 新插件 | 用上面的 searchPlugins 接口搜 claude / agent / copilot，看有没有冒头的新插件（"又一个顶级 IDEA AI 插件诞生了！"是已验证品类） |
