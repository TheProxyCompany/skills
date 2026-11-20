---
name: life-map
description: >
  Work with Proxy's Life Map, the user's personal knowledge graph. Use when
  reading or updating life context, projects, goals, relationships, blockers,
  priorities, decisions, or graph-backed memory through Proxy tools such as
  proxy_search, proxy_read, proxy_query, proxy_analyze, proxy_simulate,
  proxy_mutate, proxy_moves_propose, and proxy_moves_read.
---

# Life Map

The Life Map is Proxy's personal knowledge graph. It represents a person's
world: work, health, relationships, projects, goals, decisions, resources, and
the connections between them.

The Life Map is space. It shows how things relate to each other: hierarchy,
dependencies, leverage, topology. It is a terrain map, not a feed.

## Core Principles

**Explore before acting.** Check the Life Map before making claims about the
user's world. Start with `proxy_search` (hybrid BM25 + semantic embedding +
exact-ID fast path) to locate nodes, `proxy_read` for bounded L0/L1/L2 detail
and k-hop causal traversal, `proxy_query` for compact structured sweeps and
overviews, and `proxy_analyze` for leverage, odds, and gradients.

**Propose, do not impose.** Do not silently restructure a user's graph. For
meaningful changes, create a Move with `proxy_moves_propose` so the user can
review and approve it.

**Use direct writes sparingly.** `proxy_mutate` is for explicit user requests,
low-risk bookkeeping, or approved Move execution. When in doubt, propose the
change as a Move.

**Log what matters without polluting hubs.** Entries keep the graph alive, but
automated patrols and repeated status checks should pass a deterministic
`dedupe_key` (24-hour idempotent update window per `(about_id, author,
dedupe_key)`) or update node properties directly instead of appending duplicate
`update` entries.

## The 8-7-7 System

The Trellis schema has 8 node types, 7 edge types, and 7 entry types. Use only
these; a `category` node or a `DYNAMIC` edge found in old data is not a type
to copy.

### Nodes

**Goal.** An outcome or objective the user is orienting around. Goals give
actions purpose and scope; connect actions to goals with `FOR` when an action is
in service of the outcome.

**Action.** Work with defined scope. Actions have a phase:
`planned`, `doing`, `done`, or `stopped`.

**Entity.** A person, organization, tool, place, or object that exists in the
world. Entities participate through edges; they are not themselves work.

**Event.** A bounded moment, deadline, or time window. Events have an
`occurs_at` timestamp and anchor the timeline. Ordinary observations about what
happened should usually be entries, not events.

**Condition.** A state of the world that affects other nodes. Conditions often
represent blockers, constraints, risks, pressure, or enabling context.

**Concept.** An idea, principle, thesis, or framing that informs decisions but
is not itself actionable.

**File.** A reference to content-addressed storage: documents, images, PDFs,
and other files.

**Entry.** A journal record attached to nodes via `ABOUT` edges. Entries do not
float; they belong to something.

### Edges

**HAS** expresses real containment and ownership. Use it when one thing
structurally contains another, such as a project/action HAS sub-tasks. Do not
use HAS as a generic taxonomy bucket.

**ABOUT** attaches entries to their subjects.

**NEEDS** expresses dependency or prerequisite. If an action cannot proceed
without another node, it NEEDS that node.

**WANTS** expresses aspiration without hard dependency.

**MAKES** expresses production or creation. An action MAKES the artifact it
produces.

**FOR** expresses purpose or beneficiary. It answers why something exists.

**IMPACTS** expresses weighted causal influence (`weight` is set on `IMPACTS`
edges only).

Choose one of the seven edge types or leave the relationship unmodeled until it
is clearer.

### Entries

**update** records progress or status changes.

**note** records context worth preserving.

**issue** records something broken, wrong, blocked, or degraded.

**decision** records a choice and the path taken.

**takeaway** records a lesson learned.

**reference** points to an external resource.

**metric** records a quantitative snapshot.

## v2 Tool Patterns (Progressive Disclosure & General DAG Primitives)

All v2 tools return compact text in `content[0].text` with `structuredContent`
omitted by default (eliminating 2x-3x wire duplication). Pass `format: "json"`
or `include_structured: true` only when a caller explicitly needs structured
JSON. Legacy v1 tool names (`proxy_get`, `proxy_list`, `proxy_get_edges`,
`proxy_overview`, `proxy_recent`, `proxy_prioritize`, `proxy_create`,
`proxy_update`, `proxy_link`, `proxy_create_move`, etc.) remain silently routed
as backwards-compatible aliases.

### 1. `proxy_search` (Primary Entry Point: Exact-ID + Hybrid BM25/Semantic + Structured Filters)
- Exact ID and ID-prefix matches rank #1 immediately across nodes and entries.
- Combines BM25 lexical ranking with semantic embeddings when available.
- Chain structured DAG filters inline in the same call:
  `entity_type` (or `kinds`), `phase` (`planned`, `doing`, `done`, `stopped`, or
  `active`), `scope` (subtree root), `missing_causal_out: true`, `updated_since`,
  `include_entries`, `hydrate: "none" | "l0"`, and `limit` (default `15`, max `50`).

### 2. `proxy_read` (L0 / L1 / L2 Progressive Disclosure, Batch `ids`, and k-Hop Causal Walk)
- **`entity_type` is optional:** pass `id` alone (`{"id": "grand-central"}`) and
  the server auto-resolves across all node kinds and entries.
- **L0 (`detail: "l0"`, default):** Returns a compact `< 2 KB` header (`id`,
  `kind`, `name`, `phase`, `belief`, `updated_at`, bounded `description`),
  `total_entries`, `children_count`, a 7-edge histogram (`about`, `for`, `has`,
  `impacts`, `makes`, `needs`, `wants`), and causal edges only (default
  `edges_limit: 20`). Never dumps hundreds of entries or children by default.
- **L1 (`detail: "l1"`):** Adds paginated entries (`entries_limit` default `10`,
  max `50`, `entries_offset`, `entries_since`, `entry_types`) and compact child
  headers (`children_limit`).
- **L2 (`detail: "l2"`):** Full untruncated content plus optional `depth: 1 | 2`
  bounded k-hop causal DAG traversal (`makes`, `needs`, `for`, `impacts`,
  `wants`, capped at 50 nodes) and `include_blockers: true`.
- **Batch `ids: [...]`:** Hydrate up to 50 known IDs in a single call and a
  single graph snapshot instead of N serial `proxy_get` loops.
- **Edge queries:** Pass `mode: "summary"` for a compact edge histogram, or
  `mode: "edges"` with `labels`/`edge_types`, `edges_limit`, and `edges_offset`.

### 3. `proxy_query` (Compact Patrol Sweeps, Recent Activity, and Overview)
- **`mode: "list"` with `view: "compact"`:** Scans up to 100 actions/nodes in 1
  call as one-line summaries with causal degree counts (`sort: "updated_desc"`
  or `"causal_degree_asc"`, `missing_causal_out: true`, `offset`, `limit`). Use
  this for patrol sweeps instead of looping `proxy_read`.
- **`mode: "overview"`:** Bird's-eye PageRank2 focus blocks plus structural
  health and under-connected active nodes (`include_topology: true`).
- **`mode: "recent"`:** Recently updated nodes and entries in a scope.

### 4. `proxy_analyze` & `proxy_simulate` (Reality Engine Math)
- **`proxy_analyze`:** Unified read-only solver (`mode: "prioritize" | "odds" |
  "gradient" | "full"`). Pass `id` with `mode: "full"` to get odds (with stored
  node beliefs and `zero_cut` diagnostics), active blockers, and top edge
  gradients in one call. Supports `as_of` historical cutoffs, `scope`, `limit`,
  and `leaf_only`.
- **`proxy_simulate`:** Counterfactual solver (`mode: "complete"` with multi-node
  `complete_ids: [...]`, or `mode: "mutations"` scoring candidate edge/belief
  changes against `goal_id`).

### 5. `proxy_mutate` & `proxy_moves_propose`
- **`proxy_mutate`:** Single or atomic batch `upsert_nodes`, `append_entries`
  (with optional `dedupe_key` to prevent patrol entry spam), `set_edges`, and
  `remove_edges` (by `edge_id` or `(from_id, to_id, edge_type)`), with
  post-write readback verification.
- **`proxy_moves_propose` / `proxy_moves_read`:** Propose, revise, and paginate
  Moves (see the `proxy-moves` skill for full card authoring rules).
- Destructive and human-gated tools (`proxy_delete`, `proxy_delete_move`,
  `proxy_make_move`, `proxy_set_activation`) remain isolated behind human
  authority gates.

## Recording Problems

When the user reports something broken or wrong:

1. Search for the node the problem belongs to with `proxy_search`.
2. Propose or create an action for the fix.
3. Attach an `issue` entry describing the problem.
4. Wire edges so the affected system HAS the fix action.
5. If the issue blocks something, connect the blocked node with `NEEDS`.
6. If it is broad state affecting multiple things, consider a `condition` node
   with `IMPACTS` edges.

The action is the work unit. The issue entry is the problem description. The
edges make the problem visible to prioritization and future agents.

## Conversation Patterns

- User reports a bug or problem: follow the recording pattern.
- User mentions a project or task: run `proxy_search` first, then offer to
  create or update.
- User makes a decision: record a `decision` entry on the relevant node.
- User asks what to focus on: run `proxy_analyze(mode: "prioritize")`.
- User mentions a blocker: model it as a condition or action dependency.
- Conversation produces an insight: record a `takeaway` entry.
- Status changes: update the action phase directly via `proxy_mutate`.
- Something happened: attach an `update` or `note` entry (using `dedupe_key`
  for recurring checks); create or update an event only for a deadline,
  appointment, trip, launch window, or other bounded time anchor.
- A measurement is taken: attach a `metric` entry to the relevant node.
- User is deliberating: explore related graph context via `proxy_read(depth: 1)`
  before suggesting a change.
