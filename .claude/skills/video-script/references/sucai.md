你说得对。深入核对 OpenAI 官方工程文章、Responses API 文档和 `openai/codex` 源码后，上一版需要明显修正。

## 最准确的结论

Codex 的短期记忆分成两层：

1. 上下文重放：正常情况下，把当前线程的历史项目重新提交给模型。
2. 上下文压缩：快超出窗口时，用压缩后的“替代历史”取代原始历史。

而且新版 Codex 的压缩主路径，已经不只是“生成一段文字摘要”，而是服务端生成不透明的加密 `compaction` 项。

## 第一层：Codex 每次调用仍然是无状态的

Codex CLI 使用 Responses API。官方明确说，Codex 当前不依赖 `previous_response_id` 串联历史，而是让请求保持完全无状态，以兼容 Zero Data Retention。

因此每次调用时，Codex 都要重新构造 `input`。但它并不是简单的 Chat Completions `messages` 数组，而是一个异构项目列表，可能包含：

- `message`
- `reasoning`
- `function_call`
- `function_call_output`
- 图片、文件等输入
- `compaction`

另外，模型指令放在 `instructions`，工具定义放在 `tools`，也不全在 `input` 里面。[OpenAI 官方的 Codex Agent Loop 拆解](https://openai.com/index/unrolling-the-codex-agent-loop/)

第一轮大致是：

```text
instructions：模型基础指令
tools：Shell、apply_patch、MCP 等工具定义
input：
  权限和沙箱说明
  用户配置的开发者指令
  AGENTS.md、Skill 元数据等项目指令
  cwd、shell 等环境信息
  用户消息
```

模型返回 `reasoning`、`function_call` 后，Codex 执行工具，再把 `function_call_output` 追加进去。下一次推理时，旧输入、模型输出和工具结果都会成为新请求的前缀。

所以更准确的说法是：

> Codex 的即时短期记忆，是由客户端维护并反复提交的 Responses API 项目序列，而不只是一个 `messages` 数组。

官方还特别说明，旧 prompt 会成为新 prompt 的精确前缀，以便命中 Prompt Caching。缓存只是减少重复计算，并不是另一种记忆。[Codex Agent Loop：工具调用与上下文增长](https://openai.com/index/unrolling-the-codex-agent-loop/)

## 第二层：超过阈值后自动压缩

上下文窗口包含输入、输出和推理 token。随着工具调用和对话增加，Codex 会在超过 `auto_compact_limit` 时自动压缩。

触发阈值可以由 `model_auto_compact_token_limit` 控制，但它与模型上下文大小有关，不能笼统说成一个永远固定的 token 数。[Codex 官方配置 Schema](https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json)

压缩存在两条实现路径。

### 标准 OpenAI 模型：远程压缩

这是大多数 Codex 用户现在走的主路径。

Codex 把当前完整上下文提交给：

```http
POST /v1/responses/compact
```

服务端返回一个新的、体积更小的上下文窗口，其中通常包含：

```json
[
  {
    "type": "message",
    "role": "user",
    "content": "部分被保留的内容"
  },
  {
    "type": "compaction",
    "encrypted_content": "gAAAAA..."
  }
]
```

这里的 `encrypted_content`：

- 对客户端和用户是不透明的；
- 不是一段可以直接阅读的 Markdown 摘要；
- 用更少的 token 携带此前对话中的关键状态和推理；
- 可能与部分被保留的原始项目一起返回。

随后 Codex 使用这个压缩结果替换旧历史，作为后续请求的正式上下文。OpenAI 文档明确要求：`/responses/compact` 的返回结果就是下一轮的标准上下文，不应自行删改。[OpenAI Compaction 官方文档](https://developers.openai.com/api/docs/guides/compaction)、[Responses Compact API](https://platform.openai.com/docs/api-reference/responses/compacted-object)

当前官方源码中的 `compact_remote.rs` 也能验证这个流程：服务端返回 `new_history` 后，Codex 对其进行必要过滤，然后调用 `replace_compacted_history`，把它安装为当前线程的新历史。[Codex 远程压缩源码](https://github.com/openai/codex/blob/main/codex-rs/core/src/compact_remote.rs)

因此，对新版 Codex 来说，这句话更准确：

> 压缩后的记忆不是单纯的文字摘要，而是“部分保留项目 + 不透明的加密 compaction 状态”。

### 自定义模型提供商：本地摘要压缩

如果模型提供商不支持 `/responses/compact`，Codex 才走传统的本地摘要路径。

这条路径会：

1. 把压缩提示词追加到当前历史。
2. 再调用一次模型，生成交接摘要。
3. 收集原始用户消息。
4. 从后往前保留最多约 20,000 token 的用户消息。
5. 追加生成的摘要。
6. 用这些内容替换原历史。

官方源码中的限制是：

```rust
const COMPACT_USER_MESSAGE_MAX_TOKENS: usize = 20_000;
```

重新构造的历史主要是：

```text
近期用户原始消息，最多约 20K token
+ 模型生成的交接摘要
+ 必要的初始上下文
```

工具调用、工具输出和旧 assistant 消息不会作为原始项目直接保留下来；重要内容能否延续，取决于有没有进入摘要。[Codex 本地压缩源码](https://github.com/openai/codex/blob/main/codex-rs/core/src/compact.rs)

源码甚至会向用户发出警告：

> 长线程和多次压缩可能降低模型准确性，应尽量保持线程短小、目标集中。

## 压缩后哪些内容会重新注入？

官方源码能够确认的是：

- 权限和沙箱信息
- 当前环境上下文
- AGENTS.md 等项目指令
- 当前有效的开发者指令
- 工具定义
- Skill 相关上下文
- 压缩后的替代历史

这些属于当前会话的标准初始上下文，会在压缩边界后重新构造。

但我没有找到官方证据支持下面这个说法：

> Codex 会固定恢复最近读取的 5 个文件。

文件内容通常来自工具输出。压缩后，工具输出可能不再以原文存在；如果压缩状态没有保住其中的细节，Codex就需要重新读取文件。

这也解释了为什么长线程压缩后，Codex有时会再次执行 `sed`、`rg` 或读取相同文件。

## 本地聊天记录不等于模型记忆

Codex默认会把会话记录保存在 `CODEX_HOME`，通常是 `~/.codex`。用户可以通过 `/resume` 恢复保存的聊天。[Codex 高级配置文档](https://learn.chatgpt.com/docs/config-file/config-advanced)

但需要区分：

```text
聊天记录写在磁盘
≠
模型当前已经看到全部聊天记录
```

磁盘记录负责恢复和审计；模型真正能使用的内容，仍然必须进入当前 Responses API 上下文。恢复超长线程时，也可能继续使用已经压缩过的替代历史。

## Codex Memories 是另一套长期记忆

Codex现在还有一套可选的本地 Memories 功能，但它不是同一线程里的短期记忆。

启用后，Codex会在聊天空闲一段时间后：

1. 从符合条件的旧聊天中提取有用信息。
2. 生成详细记忆和精简摘要。
3. 对秘密信息进行脱敏。
4. 保存到 `~/.codex/memories/`。
5. 在未来相关会话中注入这些记忆。

官方文档明确说，本地 Memories 默认关闭，而且应该把它当作辅助召回层；必须遵守的项目规则仍应写进 `AGENTS.md` 或仓库文档。[Codex Memories 官方文档](https://learn.chatgpt.com/docs/customization/memories)、[Memories Pipeline 源码说明](https://github.com/openai/codex/blob/main/codex-rs/core/src/memories/README.md)

## 对上一篇回答的纠正

| 之前的说法 | 调研后的结论 |
|---|---|
| 短期记忆就是 `messages` 数组 | 过度简化。Codex使用Responses API异构 `input` 项目序列，另有 `instructions` 和 `tools` |
| 压缩就是生成一份文字摘要 | 只适用于本地回退路径；标准OpenAI路径主要使用加密 `compaction` 项 |
| 压缩后保留最近对话和摘要 | 不完整。远程压缩结果还可能包含服务端选择保留的原始项目 |
| 固定重新注入最近5个文件 | 没有找到Codex官方依据 |
| 使用 Boundary Marker 丢弃此前历史 | Codex官方源码使用 `replacement_history` 和 `compaction` 项，没有发现叫这个名字的机制 |
| 线程恢复就是模型长期记住了 | 错。恢复的是本地记录；最终仍要构造成当前模型上下文 |
| Memories就是短期上下文压缩 | 错。Memories是独立的跨聊天持久化机制 |

你这台机器当前绑定的是 ChatGPT App 内置的 `codex-cli 0.144.5`。上面的实现判断以2026年7月20日的公开官方文档和 `openai/codex` 当前源码为准；桌面App内部构建仍可能包含尚未公开的小范围改动。

一句话最终总结：

> Codex的短期记忆，正常阶段靠客户端重放Responses API上下文；接近窗口上限时，标准OpenAI路径通过 `/responses/compact` 把原始历史替换成“保留项目 + 加密压缩状态”；跨聊天记忆则由另一套本地 Memories 管道完成。