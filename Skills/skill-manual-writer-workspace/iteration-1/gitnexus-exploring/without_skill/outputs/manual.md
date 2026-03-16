# Manual: gitnexus-exploring

## Overview

The `gitnexus-exploring` skill is the entry point for understanding any codebase indexed by GitNexus. It provides a structured, 5-step workflow for navigating unfamiliar code — starting from a high-level repository overview, narrowing to relevant execution flows, and drilling into individual symbols with full call-graph context.

Use this skill whenever you need to answer questions like:
- "How does authentication work?"
- "What's the project structure?"
- "What calls this function?"
- "Where is the database logic?"
- "Show me the main execution flows"

---

## 5-Step Workflow

```
+-----------------------------------------------------------------------+
|                   GitNexus Exploring Workflow                         |
+-----------------------------------------------------------------------+
|                                                                       |
|  STEP 1                                                               |
|  READ gitnexus://repos                                                |
|  Discover all indexed repositories                                    |
|       |                                                               |
|       v                                                               |
|  STEP 2                                                               |
|  READ gitnexus://repo/{name}/context                                  |
|  Get codebase overview; verify index is not stale                     |
|       |                                                               |
|       | [If "Index is stale" warning] --> run: npx gitnexus analyze   |
|       |                                                               |
|       v                                                               |
|  STEP 3                                                               |
|  gitnexus_query({query: "<concept>"})                                 |
|  Find execution flows related to the concept you want to understand   |
|       |                                                               |
|       v                                                               |
|  STEP 4                                                               |
|  gitnexus_context({name: "<symbol>"})                                 |
|  360-degree view of a specific symbol: callers, callees, flows        |
|       |                                                               |
|       v                                                               |
|  STEP 5                                                               |
|  READ gitnexus://repo/{name}/process/{processName}                    |
|  Trace a full execution flow step-by-step                             |
|                                                                       |
+-----------------------------------------------------------------------+
```

### Step Details

| Step | Action | Purpose |
|------|--------|---------|
| 1 | `READ gitnexus://repos` | List all repositories indexed by GitNexus |
| 2 | `READ gitnexus://repo/{name}/context` | High-level overview: symbol count, process count, staleness check |
| 3 | `gitnexus_query({query: "..."})` | Semantic search — maps a concept to grouped execution flows and symbols |
| 4 | `gitnexus_context({name: "..."})` | Deep dive: incoming calls, outgoing calls, process participation |
| 5 | `READ gitnexus://repo/{name}/process/{name}` | Step-by-step execution trace for a named process |

---

## GitNexus Tools Used

### `gitnexus_query`

Finds execution flows related to a concept or keyword. Results are grouped by process and ranked by relevance.

**Signature:**
```
gitnexus_query({query: string})
```

**Returns:**
- List of matching execution flow (process) names
- Symbols within each flow, with file locations
- Grouped by process for easy scanning

**Example output:**
```
gitnexus_query({query: "payment processing"})
  -> Processes: CheckoutFlow, RefundFlow, WebhookHandler
  -> Symbols grouped by flow with file locations
```

**When to use:** Start here when you know the concept but not the code. This is the primary discovery tool.

---

### `gitnexus_context`

Provides a 360-degree view of a single named symbol: its callers, its callees, and every execution flow it participates in (with step position).

**Signature:**
```
gitnexus_context({name: string})
```

**Returns:**
- Incoming calls (who calls this symbol)
- Outgoing calls (what this symbol calls)
- Process participation: which flows include this symbol and at which step

**Example output:**
```
gitnexus_context({name: "validateUser"})
  -> Incoming calls: loginHandler, apiMiddleware
  -> Outgoing calls: checkToken, getUserById
  -> Processes: LoginFlow (step 2/5), TokenRefresh (step 1/3)
```

**When to use:** After `gitnexus_query` identifies a symbol of interest. Use this to understand the full dependency picture before making any changes.

---

## Resources Reference

Resources are read-only URI endpoints that return structured summaries.

| Resource URI | What you get | Approx. tokens |
|---|---|---|
| `gitnexus://repos` | All indexed repositories | ~50 |
| `gitnexus://repo/{name}/context` | Stats, staleness warning | ~150 |
| `gitnexus://repo/{name}/clusters` | All functional areas with cohesion scores | ~300 |
| `gitnexus://repo/{name}/cluster/{name}` | Area members with file paths | ~500 |
| `gitnexus://repo/{name}/process/{name}` | Step-by-step execution trace | ~200 |

### Choosing the right resource

```
+-------------------------+        +-------------------------------+
|  Want a broad overview? |        | Want a specific area's files? |
|  -> /context            |        | -> /clusters then /cluster/X  |
+-------------------------+        +-------------------------------+
           |                                    |
           v                                    v
+------------------------------+    +-------------------------------+
|  Want step-by-step trace?    |    | Want to check index health?   |
|  -> /process/{name}          |    | -> /context (staleness field) |
+------------------------------+    +-------------------------------+
```

---

## Usage Examples

### Example 1: "How does payment processing work?"

```
1. READ gitnexus://repo/my-app/context
   -> 918 symbols, 45 processes, index is fresh

2. gitnexus_query({query: "payment processing"})
   -> CheckoutFlow: processPayment -> validateCard -> chargeStripe
   -> RefundFlow:   initiateRefund -> calculateRefund -> processRefund

3. gitnexus_context({name: "processPayment"})
   -> Incoming:  checkoutHandler, webhookHandler
   -> Outgoing:  validateCard, chargeStripe, saveTransaction
   -> Processes: CheckoutFlow (step 3/6)

4. READ gitnexus://repo/my-app/process/CheckoutFlow
   -> Full step-by-step trace from entry to completion

5. Read src/payments/processor.ts for implementation details
```

---

### Example 2: "What calls validateUser?"

```
1. READ gitnexus://repo/my-app/context
   -> Index is fresh, 344 symbols

2. gitnexus_query({query: "user validation authentication"})
   -> LoginFlow, TokenRefreshFlow, ApiMiddlewareFlow

3. gitnexus_context({name: "validateUser"})
   -> Incoming calls: loginHandler, apiMiddleware
   -> Outgoing calls: checkToken, getUserById
   -> Processes: LoginFlow (step 2/5), TokenRefresh (step 1/3)

   Answer: validateUser is called by loginHandler and apiMiddleware.
```

---

### Example 3: "Show me the project structure / main components"

```
1. READ gitnexus://repo/my-app/context
   -> Overview of symbol count and process count

2. READ gitnexus://repo/my-app/clusters
   -> All functional areas: Auth, Payments, DataLayer, API, etc.
   -> Cohesion scores for each area

3. READ gitnexus://repo/my-app/cluster/Auth
   -> All symbols in the Auth area with file paths

4. READ gitnexus://repo/my-app/cluster/Payments
   -> All symbols in the Payments area with file paths
```

---

### Example 4: "Where is the database logic?"

```
1. gitnexus_query({query: "database queries persistence"})
   -> DataAccessFlow, MigrationFlow, CacheLayer

2. gitnexus_context({name: "saveTransaction"})
   -> Outgoing: db.query, db.transaction
   -> Processes: CheckoutFlow (step 5/6)

3. Read the file paths returned above for implementation details
```

---

## Handling a Stale Index

If step 2 returns a staleness warning:

```
READ gitnexus://repo/my-app/context
-> WARNING: Index is stale. Commit hash has changed since last analyze.
```

Run the following in your terminal before continuing:

```bash
npx gitnexus analyze
```

If embeddings were previously generated (check `.gitnexus/meta.json` — `stats.embeddings` field), preserve them:

```bash
npx gitnexus analyze --embeddings
```

After re-indexing, retry step 2 to confirm freshness.

---

## Developer Guide

### When to invoke this skill

Invoke `gitnexus-exploring` at the start of any task that requires understanding code before acting on it. It is a prerequisite for:

- Impact analysis (know what a symbol does before assessing blast radius)
- Debugging (understand the execution flow before identifying fault points)
- Refactoring (understand callers and callees before moving or renaming code)

### Relationship to other GitNexus skills

```
gitnexus-exploring  <-- always first: understand the code
       |
       +--> gitnexus-impact-analysis  (before editing)
       |
       +--> gitnexus-debugging        (when tracing errors)
       |
       +--> gitnexus-refactoring      (when restructuring)
```

Exploring answers the question "what is here and how does it connect?" The other skills build on that understanding to answer "what is safe to change?" and "what is broken?"

### Depth strategy

Not every exploration requires all 5 steps. Use this decision tree:

```
Question type?
  |
  +-- "What is the structure?"       --> Steps 1, 2, /clusters, /cluster
  |
  +-- "How does X work?"             --> Steps 2, 3, 5
  |
  +-- "What calls function Y?"       --> Steps 3, 4 (gitnexus_context only)
  |
  +-- "Trace full flow from entry"   --> Steps 3, 5 (/process resource)
```

### Output interpretation

**`gitnexus_query` output:**
- "Processes" are named execution flows (e.g., `LoginFlow`, `CheckoutFlow`). Each represents a traceable path through the codebase.
- Symbols listed under a process are the key participants, not an exhaustive list.
- Use process names from `query` output as arguments to `/process/{name}` for the full trace.

**`gitnexus_context` output:**
- "Incoming calls" = direct callers. These WILL BREAK if you modify the symbol's interface (depth=1 in impact analysis).
- "Outgoing calls" = dependencies. These are what the symbol depends on.
- "Processes: X (step N/M)" tells you both which flow this symbol belongs to and where in the flow it sits. A symbol at step 1/5 is an entry point; step 5/5 is a terminal step.

### Token budget awareness

When working within a constrained context window, prefer resources in order of token cost (lowest first):

1. `/context` (~150 tokens) — always start here
2. `gitnexus_query` — focused results, typically 100-300 tokens
3. `/process/{name}` (~200 tokens per process)
4. `gitnexus_context` — varies by symbol connectivity
5. `/clusters` (~300 tokens)
6. `/cluster/{name}` (~500 tokens per cluster)

### Checklist (copy this for each exploration session)

```
- [ ] READ gitnexus://repos  (confirm repo name)
- [ ] READ gitnexus://repo/{name}/context  (check staleness)
- [ ] gitnexus_query for the concept you want to understand
- [ ] Review returned processes (execution flows)
- [ ] gitnexus_context on key symbols for callers/callees
- [ ] READ /process/{name} for full execution traces
- [ ] Read source files for implementation details
```

---

## Quick Reference Card

```
+--------------------------------------------------+
|  gitnexus-exploring  —  Quick Reference          |
+--------------------------------------------------+
|                                                  |
|  DISCOVER           READ gitnexus://repos        |
|  OVERVIEW           READ .../context             |
|  FIND FLOWS         gitnexus_query({query:""})   |
|  INSPECT SYMBOL     gitnexus_context({name:""})  |
|  TRACE FLOW         READ .../process/{name}      |
|  LIST AREAS         READ .../clusters            |
|  AREA DETAIL        READ .../cluster/{name}      |
|                                                  |
|  STALE INDEX?       npx gitnexus analyze         |
+--------------------------------------------------+
```
