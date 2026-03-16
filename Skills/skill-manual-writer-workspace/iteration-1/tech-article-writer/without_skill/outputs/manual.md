# tech-article-writer Skill — Technical Manual

## Overview

The `tech-article-writer` skill instructs an AI assistant to produce Traditional Chinese technology articles optimized for fast reading by enterprise colleagues. It targets a mixed audience — ranging from non-technical business users to seasoned engineers — and enforces a consistent, conversational writing style combined with a structured layout that supports scanning rather than linear reading.

The skill is defined entirely in a single `SKILL.md` file and relies on no external dependencies, libraries, or APIs. All logic is expressed as natural-language instructions that the AI model interprets at generation time.

---

## Workflow Diagram

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Trigger Detection                                  │
│  ─────────────────                                  │
│  Does the request involve writing an article        │
│  about tech, AI tools, or technical onboarding?    │
└──────────────────────────┬──────────────────────────┘
                           │ YES
                           ▼
┌─────────────────────────────────────────────────────┐
│  Topic Classification                               │
│  ────────────────────                               │
│  ┌───────────────────┐  ┌─────────────────────────┐ │
│  │ AI Tool Tutorial  │  │ Tech Adoption Guide     │ │
│  │ (usage scenarios, │  │ (before/after tables,   │ │
│  │  prompts, steps)  │  │  phases, challenges)    │ │
│  └───────────────────┘  └─────────────────────────┘ │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│  Article Construction                               │
│  ────────────────────                               │
│                                                     │
│   [Title]        Specific, informative, scannable  │
│       │                                             │
│   [Intro]        2-3 sentences, direct cut-in      │
│       │                                             │
│   [Body]         ## headings, 1 focus per section  │
│       │          ≥ 1 table required                 │
│       │                                             │
│   [Next Steps]   1-3 concrete action items         │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│  Output Format Selection                            │
│  ───────────────────────                            │
│                                                     │
│  No format specified ──────────────► Markdown (.md)│
│  User requests HTML  ──────────────► HTML (.html)  │
│  User requests both  ──► .md file + .html file     │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│  Quality Check (internal)                           │
│  ────────────────────────                           │
│  □ Title is specific and scannable                 │
│  □ Opening does not use empty filler phrases       │
│  □ Technical terms explained on first use          │
│  □ At least 1 table present                        │
│  □ Word count between 1000 – 2000 characters       │
│  □ Closing section has concrete next steps         │
│  □ Tone reads like colleague conversation          │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
                      Final Article
```

---

## Component Descriptions

### 1. Trigger Detection

The skill activates when a user request matches any of these patterns (not exhaustive):

- Explicit article requests: "幫我寫一篇…", "寫一篇介紹…", "寫篇教學文章"
- Topic-based triggers: mentions of AI tools (ChatGPT, Claude, Copilot, etc.), technology onboarding, internal newsletters, technical concepts
- Implicit triggers: "幫我解釋 XXX 給同事看" where XXX is a tech/AI topic

Even vague requests like "幫我寫一篇關於 XXX 的文章" trigger this skill when the subject involves technology or AI.

### 2. Tone Guidelines

The skill enforces a collegial, conversational tone — as if explaining something interesting to a coworker in the break room. Key rules:

| Rule | Allowed | Avoided |
|------|---------|---------|
| Address reader | 你 (you) | 讀者 / 用戶 |
| Transitions | 說白了、換句話說、重點來了 | 綜上所述、由此可見 |
| Term handling | Define on first use, then use freely | Either always define or never define |
| Sentence style | Active, concise | Passive academic constructions |

### 3. Article Structure

Every article follows a three-part skeleton:

**Intro (2-3 sentences)**
- States the topic immediately
- Explains why the reader should care
- Forbidden: opening with "隨著科技的發展…" or similar empty phrases

**Body (variable sections)**
- Each `##` section covers exactly one point
- At least one Markdown table is mandatory per article
- Tables are preferred for comparisons, step lists, pros/cons, and before/after contrasts

**Next Steps**
- 1 to 3 concrete, actionable recommendations
- Not a summary — must tell the reader what to *do* next

### 4. Output Formats

| Requested format | Output |
|-----------------|--------|
| Not specified | Single `.md` file |
| HTML | Single `.html` file with embedded CSS |
| Both | One `.md` + one `.html` file |

The HTML output includes specific styling requirements:
- Font stack: `-apple-system, "Microsoft JhengHei", sans-serif`
- Line height: 1.8
- Tables: borders + alternating row background colors
- Max width: 800 px, centered
- Responsive design for mobile

### 5. Topic-Specific Writing Guidance

**AI Tool Tutorials**
Focus: what can this tool do for me, and how do I start?
- Open with a concrete use scenario (not abstract capabilities)
- Provide step-by-step instructions
- Include prompt examples or screenshot descriptions
- Warn about common pitfalls

**Technology Adoption Guides**
Focus: is this worth adopting, what changes, and where do I start?
- Before/after comparison table
- Prerequisites and resource requirements
- Phased rollout suggestions
- Honest disclosure of limitations and challenges

### 6. Quality Checklist

The skill embeds a self-check the AI must perform before finalizing output:

```
□ Title: specific, topic is clear at a glance
□ Opening: direct, no filler phrases
□ Terms: defined on first appearance
□ Tables: at least 1 present
□ Length: 1000–2000 characters
□ Closing: concrete next steps (not just a summary)
□ Tone: collegial, not academic
```

---

## Trigger Phrases (Usage Examples)

The following examples illustrate natural language requests that activate this skill and the expected behavior.

### Example 1 — AI Tool Tutorial

**User input:**
> 幫我寫一篇介紹 Claude 給公司同事看的文章，他們大多數都沒用過 AI

**Expected behavior:**
- Skill activates (AI tool tutorial topic detected)
- Opens with a concrete scenario (e.g., using Claude to summarize meeting notes)
- Includes a table comparing what users can ask Claude to do vs. what it cannot reliably do
- Word count 1000–2000 characters
- Closes with steps to start: "你可以先試著這樣做…"
- Output: Markdown by default

---

### Example 2 — Technology Adoption Guide

**User input:**
> 寫一篇給非技術主管看的技術導入指南，主題是在團隊內引入 GitHub Copilot

**Expected behavior:**
- Skill activates (technical adoption guide topic detected)
- Includes before/after table: current workflow vs. Copilot-assisted workflow
- Lists prerequisites (GitHub Enterprise license, IDE support)
- Provides phased rollout (pilot team → wider rollout)
- Acknowledges limitations (not suitable for all languages, requires code review discipline)
- Output: Markdown by default

---

### Example 3 — Internal Tech Newsletter

**User input:**
> 幫我寫一篇 IT 內部通訊，解釋什麼是向量資料庫，給完全不懂技術的同仁看

**Expected behavior:**
- Skill activates (tech concept explanation for non-technical audience)
- Defines "向量資料庫" in plain terms on first use
- Uses analogy or comparison table (traditional DB vs. vector DB)
- Avoids deep math / embedding theory
- Output: Markdown by default

---

### Example 4 — HTML Output Request

**User input:**
> 寫一篇關於 Prompt Engineering 基礎的教學文章，要 HTML 格式，要放到內部 Wiki

**Expected behavior:**
- Skill activates
- Output: single `.html` file
- Includes embedded CSS with the required styling (JhengHei font, 800px max width, responsive, styled tables)
- Content follows all standard structure rules

---

### Example 5 — Dual Output Request

**User input:**
> 幫我寫一篇介紹 RAG（Retrieval-Augmented Generation）的文章，兩種格式都要

**Expected behavior:**
- Skill activates
- Defines RAG in accessible terms
- Output: one `.md` file + one `.html` file with full CSS

---

## Developer Guide — Customizing the Skill

### File Location

```
Skills/tech-article-writer/
└── SKILL.md          ← the entire skill definition
```

### Skill File Format

The `SKILL.md` uses a YAML front-matter block followed by Markdown content:

```yaml
---
name: tech-article-writer
description: >
  <one or more paragraphs describing when the skill activates>
---
```

The `description` field is what the skill routing layer reads to decide whether to invoke this skill. The body of the file is the instruction set the AI model receives when the skill is active.

### Modifying the Article Template

The article template is defined under the `## 文章模板` section of `SKILL.md`. To change the default structure, edit the fenced Markdown block in that section. Be specific: the model follows the template literally when the topic allows.

### Adding a New Topic Category

To add a third topic type (e.g., "Security Awareness Articles"):

1. Add a new subsection under `## 常見主題的寫作提示` in `SKILL.md`:

```markdown
### 資安意識文章

讀者想知道：這個威脅跟我有什麼關係？我應該怎麼做？

- 用真實案例（但匿名化）開場
- 強調行為改變，而非技術細節
- 附上快速行動清單
- 結尾連結內部資安政策
```

2. Update the `description` front-matter to add the new trigger condition so the routing layer activates the skill for security articles.

### Changing the Length Range

The 1000–2000 character target is stated in the `### 長度：1000 到 2000 字` section. To adjust (e.g., for a more concise internal format):

```markdown
### 長度：600 到 1000 字

這個字數範圍適合快速內部更新——短到讓人願意讀，長到說清楚一件事。
```

Update the corresponding item in the quality checklist at the bottom of the file to match.

### Modifying the HTML Output Specification

The HTML styling rules are under `## 輸出格式`. To change the layout or font stack, edit the bullet list in that section. For example, to switch to a narrower reading column:

Find:
```
- 最大寬度 800px，置中顯示
```
Replace with:
```
- 最大寬度 640px，置中顯示
```

The model will incorporate the new constraint into generated HTML.

### Extending the Quality Checklist

The checklist under `## 品質檢查清單` drives the AI's self-review step. To enforce additional requirements, add items with the `- [ ]` prefix:

```markdown
- [ ] 是否避免提及競爭對手產品的品牌名稱？
- [ ] 文章是否符合公司資訊安全規範（不含客戶資料、不含機密系統名稱）？
```

### Disabling the HTML Output Option

If you want to restrict output to Markdown only (e.g., for a wiki pipeline that only accepts `.md`), remove or replace the `## 輸出格式` section with:

```markdown
## 輸出格式

一律輸出 Markdown（.md）格式。不支援 HTML 輸出。
```

### Testing Changes

After editing `SKILL.md`, test with at minimum:

1. A basic AI tool tutorial request (no format specified) — verify Markdown output and table presence.
2. A request with `要 HTML 格式` — verify HTML with embedded CSS is generated.
3. A borderline topic (e.g., project management without tech focus) — verify the skill does *not* activate incorrectly.
4. A complex topic — verify the model suggests splitting into a series rather than exceeding 2000 characters.

---

## Skill Metadata Reference

| Field | Value |
|-------|-------|
| Skill name | `tech-article-writer` |
| Language | Traditional Chinese (繁體中文) |
| Target audience | Enterprise colleagues, mixed technical backgrounds |
| Default output format | Markdown |
| Optional output format | HTML (standalone, with embedded CSS) |
| Article length target | 1000–2000 characters |
| Minimum tables per article | 1 |
| Supported topic categories | AI tool tutorials, technology adoption guides, tech concept explainers |
| External dependencies | None |
| Skill definition file | `Skills/tech-article-writer/SKILL.md` |
