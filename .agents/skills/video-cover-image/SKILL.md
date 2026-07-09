---
name: video-cover-image
description: Generate paired vertical and horizontal short-video cover images from toBeBetterJavaer video scripts or AI/Java technical topics. Use when the user asks for 视频封面, 封面图, 横版和竖版, 小红书/抖音/B站/快手封面, pure-text covers with 白色大字+黄色小字, reference-image-matched covers, or wants a repeatable cover workflow for Markdown scripts under docs/src/ai/video/.
---

# Video Cover Image

## Overview

Create a matched cover pair for one technical short-video script:

- Vertical cover: `3:4`, for 小红书、抖音、快手 and mobile feeds.
- Horizontal cover: `4:3`, for B站 and video thumbnails.

By default, generate both covers as a pair. Generate only one ratio when the user explicitly says only/只要/单独生成 one specific ratio.

Use the `itwanger-image` style rules when available. Keep prompt context isolated: use only the target script, user-provided reference images, and this skill's rules. Do not pull in unrelated browser/editor/window/history content.

If the user provides a reference image or asks for `纯文本`, `白色大字+黄色小字`, `黑色/黑灰背景`, or `参考图这种布局`, use the pure-text reference style below instead of the default illustrated style. Use deterministic rendering for this mode so Chinese text stays exact.

## Workflow

1. Resolve exactly one script or topic.
   - If the user provides a file path, read that file.
   - If the user gives a filename under `docs/src/ai/video/`, resolve it there.
   - If several files match, ask which one.
   - If the user asks to batch a directory, process one file at a time and produce one vertical/horizontal pair per script.

2. Extract cover material from the script.
   - Topic: one short phrase, usually the article/interview question.
   - Main title: 1 English or Chinese phrase that can be read at thumbnail size.
   - Two big punch lines: 2-6 Chinese characters each if possible.
   - Small tag: one short promise or rule of thumb.
   - Visual metaphor: one simple icon or scene, such as Agent flow, checklist, tool call, loop, search, or error trap.
   - Presenter expression: match the topic while keeping the same 二哥 character. Use confident/focused for architecture and collaboration, serious/alert for pitfalls and bugs, excited/energetic for tutorials and capability reveals, and skeptical/surprised for wrong-answer interview hooks.

3. Select the cover mode.
   - Use pure-text reference mode when the user asks for a text-only cover, provides a black/gray reference card, or corrects toward "one white title line plus yellow keyword lines".
   - Use default illustrated mode for normal knowledge-zone covers with presenter, icon, and blue-sky energy.

4. Keep text short enough for image generation.
   - Prefer 3-5 visible text blocks total.
   - Avoid long Chinese sentences, dense labels, and small body text.
   - If exact wording is critical, simplify the generated text first; if still unstable, generate a cleaner illustration and add text in a separate deterministic editing step.

5. For pure-text reference mode, render with `scripts/render_text_cover.py`.
   - Title: prefer the article title or the exact interview question, such as `什么是上下文工程?`.
   - If the white title becomes too small on one line, split it into two lines. Let the script auto-wrap, pass `\n` inside `--title`, or use repeated `--title-line` arguments for an intentional break.
   - Yellow text: one or two keyword lines. If one line is too small, split into two lines; do not force everything onto one line.
   - Example command:

```bash
python3 .agents/skills/video-cover-image/scripts/render_text_cover.py \
  --title "什么是 ReAct?" \
  --line "Thought、Action、Observation" \
  --line "CoT、工具调用、外部验证" \
  --prefix "what-is-react-cover"
```

6. For default illustrated mode, generate the vertical cover first with `image_gen`.
   - Ratio: `3:4`, target size similar to `1086 x 1448`.
   - Composition: top title, central visual icon, presenter in lower/right area, bottom tag.
   - Apply the default high-impact blue-sky knowledge-cover style.

7. For default illustrated mode, generate the horizontal cover with `image_gen`.
   - Ratio: `4:3`, target size similar to `1440 x 1080` or `1600 x 1200`.
   - Composition: left icon, center/right presenter, right or top punch lines.
   - Reuse the same title, punch lines, icon, character, color system, and topic framing as the vertical cover.

8. Run a quick visual quality gate before final response.
   - Aspect ratio is correct for each image.
   - The main topic is obvious at a glance.
   - Chinese text has no obvious garbling in the large title/punch lines.
   - In pure-text mode: black/gray textured background, one bold white title, one or two large yellow keyword lines, no blue background, no icon, no presenter, no outer white UI frame.
   - In default illustrated mode: the presenter is the correct 二哥 cartoon, short hair, glasses, yellow shirt, dark tie.
   - No female avatar, no unrelated fantasy costume, no real brand logo unless explicitly requested.
   - No outer frame, no rounded screenshot container, no dense small text.

9. Deliver both images.
   - Show both images with Markdown image tags.
   - Include absolute generated file paths and dimensions.
   - Do not move images into the repo unless the user explicitly asks.

## Default Style

- Bright blue sky/cloud background with speed lines or a clean energetic gradient.
- Thick white English or Chinese title, black 3D shadow.
- Large yellow Chinese punch lines with black outline.
- One glowing white rounded square icon with a blue/purple technical symbol.
- 二哥 cartoon presenter: Q-version big head, short hair, glasses, yellow shirt, dark tie, holding a pointer or laptop.
- Presenter expression changes with the topic, but the character identity stays fixed; avoid exaggerated meme faces, angry faces, horror expressions, or changing the presenter into a different person.
- Knowledge-zone feel: normal, clean, platform-ready, not neon cyberpunk, not overly AI-looking.

## Pure Text Reference Style

Use this style when matching a text-only reference card:

- Background: black/charcoal gray texture, center slightly lighter, edges darker. Avoid blue gradients, decorative symbols, characters, icons, or screenshots.
- Typography: use a real bold Chinese font if available, preferably `Hiragino Sans GB W6`; fall back to `PingFang SC Semibold`. Avoid heavy faux-bold offsets that deform Chinese glyphs.
- White title: prioritize the article title or question. Use one centered line when it stays large; use two centered lines when a single line would shrink too much. The title block should visually read as the main article title, not a loose topic label.
- Yellow keyword block: one or two centered lines. If one line makes the yellow text small, split to two lines. The whole yellow block should occupy roughly 20-23% of the reference card height.
- Horizontal `4:3`: place the white title around 29-31% of height; place yellow lines around 52-63% of height.
- Vertical `3:4`: place the white title around 34% of height; place yellow lines around 52-60% of height.
- Keep the overall composition concentrated in the middle/upper-middle. Do not fill every corner; the reference layout relies on negative space.
- Prefer concise keyword lines extracted from the script, such as `Thought、Action、Observation` and `CoT、工具调用、外部验证`.

## Prompt Pattern

Build two prompts from the same extracted payload.

Vertical prompt outline:

```text
生成一张竖版中文短视频封面图，比例 3:4，适合小红书、抖音、快手和B站竖版物料。
主题来自口播稿：{topic}
核心关键词：{keywords}
画面风格：高冲击中文知识封面，明亮蓝色天空和云层背景，速度线和光效，厚重立体字。
主视觉：二哥卡通讲解员，短发、眼镜、黄色衬衫、深色领带，表情根据主题设为 {expression}，拿教鞭指向 {visual_icon}。
封面文字必须少而大：
顶部主标题：{main_title}
中部黄色大字：{punch_line_1}
下一行黄色大字：{punch_line_2}
底部小标签：{small_tag}
要求：文字清楚，人物脸不被挡，安全边距足够，不要白底，不要外层边框，不要密集小字。
```

Horizontal prompt outline:

```text
生成一张横版中文短视频封面图，比例 4:3，适合B站横版视频封面。
主题来自口播稿：{topic}
核心关键词：{keywords}
画面风格：延续竖版同一套风格，明亮蓝色天空和云层背景，速度线和放射光效。
横版构图：左侧 {visual_icon}，中间偏右二哥卡通讲解员，表情根据主题设为 {expression}，右侧或顶部放大标题和黄色中文爆点。
封面文字必须少而大：
主标题：{main_title}
黄色大字：{punch_line_1} / {punch_line_2}
底部小标签：{small_tag}
要求：中文清楚，人物脸不被挡，横版安全区充足，不要白底，不要外层边框，不要密集小字。
```

## Extraction Examples

For `docs/src/ai/video/plan-and-execute.md`:

- Topic: Agent 面试题 Plan-and-Execute
- Main title: `Plan & Execute`
- Punch lines: `强模型想` / `弱模型干`
- Small tag: `五步以上先规划`
- Icon: glowing Agent flow icon with Planner / Executor / Replanner nodes

For a script about ReAct death loops:

- Topic: Agent 为什么会死循环
- Main title: `ReAct 死循环`
- Punch lines: `越跑越偏` / `怎么打断`
- Small tag: `观察不等于修正`
- Icon: glowing loop arrow plus stuck task card or STOP hand symbol

For a script about Skill hit rate:

- Topic: Skills 太多如何保证命中率
- Main title: `Skill 命中率`
- Punch lines: `别靠硬匹配` / `要看语义`
- Small tag: `description 决定入口`
- Icon: search radar selecting one highlighted skill card
