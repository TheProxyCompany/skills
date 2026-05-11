---
name: life-map
description: >
  Work with Proxy's Life Map, the user's personal knowledge graph. Use when
  reading or updating life context, projects, goals, relationships, blockers,
  priorities, decisions, or graph-backed memory through Proxy tools such as
  proxy_overview, proxy_list, proxy_search, proxy_recent, proxy_prioritize,
  proxy_create_move, proxy_create, proxy_update, and proxy_link.
---

# Life Map

The Life Map is Proxy's personal knowledge graph. It represents a person's
world: work, health, relationships, projects, goals, decisions, resources, and
the connections between them.

The Life Map is space. It shows how things relate to each other: hierarchy,
dependencies, leverage, topology. It is a terrain map, not a feed.

## Core Principles

**Explore before acting.** Check the Life Map before making claims about the
user's world. Use `proxy_search` to find relevant nodes, `proxy_overview` for
the big picture, `proxy_recent` for recent changes, and `proxy_prioritize` for
highest-leverage work.

**Propose, do not impose.** Do not silently restructure a user's graph. For
meaningful changes, create a Move with `proxy_create_move` so the user can
review and approve it.

**Use direct writes sparingly.** `proxy_create`, `proxy_update`, and
`proxy_link` are for explicit user requests, low-risk bookkeeping, or approved
Move execution. When in doubt, propose the change as a Move.

**Log what matters.** Entries keep the graph alive. They are the journal:
cheap, lightweight records attached to the things they are about.

## The 8-8-7 System

### Nodes

**Category.** A domain or territory: Work, Health, People, Money, Fun.
Categories group things through `HAS` edges. They are containers, not tasks.

**Action.** Work with defined scope. Actions have a phase:
`planned`, `doing`, `done`, or `stopped`.

**Entity.** A person, organization, tool, place, or object that exists in the
world. Entities participate through edges; they are not themselves work.

**Event.** Something that happened or will happen at a specific moment. Events
have an `occurs_at` timestamp and anchor the timeline.

**Condition.** A state of the world that affects other nodes. Conditions often
represent blockers, constraints, risks, pressure, or enabling context.

**Concept.** An idea, principle, thesis, or framing that informs decisions but
is not itself actionable.

**File.** A reference to content-addressed storage: documents, images, PDFs,
and other files.

**Entry.** A journal record attached to nodes via `ABOUT` edges. Entries do not
float; they belong to something.

### Edges

**HAS** expresses containment and ownership. A category HAS actions. A project
HAS sub-tasks.

**ABOUT** attaches entries to their subjects.

**NEEDS** expresses dependency or prerequisite. If an action cannot proceed
without another node, it NEEDS that node.

**WANTS** expresses aspiration without hard dependency.

**MAKES** expresses production or creation. An action MAKES the artifact it
produces.

**FOR** expresses purpose or beneficiary. It answers why something exists.

**IMPACTS** expresses weighted causal influence.

**DYNAMIC** is a freeform edge for relationships that do not fit the standard
types. Use it rarely.

### Entries

**update** records progress or status changes.

**note** records context worth preserving.

**issue** records something broken, wrong, blocked, or degraded.

**decision** records a choice and the path taken.

**takeaway** records a lesson learned.

**reference** points to an external resource.

**metric** records a quantitative snapshot.

## Tool Patterns

Use `proxy_overview` when the user asks about the broad shape of their world,
priorities, or current terrain.

Use `proxy_search` before creating anything that may already exist.

Use `proxy_list` for structured inspection by entity type, phase, or entry
type.

Use `proxy_recent` when recency matters.

Use `proxy_prioritize` when the user asks what matters, what to do next, or
where leverage is highest.

Use `proxy_create_move` for proposed graph changes that should be reviewed
before they become real.

Use `proxy_create`, `proxy_update`, and `proxy_link` only when the user has
clearly asked for a direct edit or when executing an approved Move.

## Recording Problems

When the user reports something broken or wrong:

1. Search for the node the problem belongs to.
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
- User mentions a project or task: search for an existing action, then offer to
  create or update.
- User makes a decision: record a `decision` entry on the relevant node.
- User asks what to focus on: run `proxy_prioritize`.
- User mentions a blocker: model it as a condition or action dependency.
- Conversation produces an insight: record a `takeaway` entry.
- Status changes: update the action phase.
- Something happened: create or update an event with `occurs_at`.
- A measurement is taken: attach a `metric` entry to the relevant node.
- User is deliberating: explore related graph context before suggesting a
  change.
