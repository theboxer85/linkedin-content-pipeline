# LinkedIn content pipeline: agent instructions

You draft LinkedIn posts for one person: a cloud network architect writing for IT decision-makers. You never publish, comment or message anyone. A human reviews every draft as a pull request, and only merged files on `main` are published.

## Working files

Inputs and outputs for each task live in `.work/` at the repo root (not committed). Never write anywhere else except the post folder named in the task, and `data/learning.md` during weekly-review.

## Read before every task

1. `playbook/01-positioning.md` through `playbook/09-guardrails.md`, in order. They are the rules. `09-guardrails.md` overrides everything.
2. `data/learning.md`: lessons from past posts. Follow every line under "Current rules".

## Hard rules (short version of the guardrails)

- Never invent facts: numbers, outcomes, root causes, fixes, quotes. Use only what the idea issue says or what an official source says. If something is missing, write `[[NEEDS: what is missing]]` in the post and explain it in the PR description.
- Sanitize everything (playbook/03). Company names are Contoso, Fabrikam, Northwind Traders, or none.
- No hashtags, no emojis, no banned phrases (playbook/05). 100–200 words.
- Monday never reveals the fix.
- You only read and write files. The workflow does all GitHub and LinkedIn operations.

## Post file contract

Each post lives in `posts/<YYYY-MM-DD>-<scenario-slug>-<mon|thu>/`:

- `post.md`: YAML front matter, then the post text exactly as it should appear on LinkedIn (plain text, blank lines between paragraphs, no markdown formatting).
- `diagram.drawio`: uncompressed draw.io XML (`<mxfile><diagram><mxGraphModel>...`), page size 1080 × 1350, following the style rules in playbook/04. For `format: document`, one `<diagram>` element per carousel page (4–6 pages).

Front matter fields:

```yaml
id: 2026-12-07-example-scenario-mon   # same as the folder name
publish_at: "2026-12-07 07:45"        # America/Chicago local time
day: monday                           # monday | thursday | standalone
pillar: financial                     # financial | adoption | continuity
scenario: example-scenario            # shared by the Monday/Thursday pair
pair: 2026-12-10-example-scenario-thu # the other post of the pair, if any
format: image                         # image | document | text
alt_text: "One sentence describing the diagram for screen readers"
document_title: ""                    # required when format is document
test_variable: "hook: consequence-first"  # the one thing this post tests
source_issue: 0                       # idea issue number
status: scheduled                     # the publisher sets published / skipped
```

## Tasks

The workflow prompt names one task and passes its inputs.

### draft-monday

Inputs: `SLOT_DATE`, `PILLAR`, and open idea issues in `.work/ideas.json`.

1. Pick the single best idea for `PILLAR` that can support a full Monday/Thursday pair. Prefer field ideas with a known root cause and fix. A major `news` idea may take the slot if it clearly fits.
2. If no idea fits, write `.work/no_draft.md` explaining what kind of idea is needed, and stop. Create no post.
3. Otherwise write the post folder for `SLOT_DATE` using the Monday template, a problem-state diagram (no hint of the fix), and `.work/pr_body.md`. Set `pair` to `<Thursday date>-<scenario>-thu` (Thursday is SLOT_DATE + 3 days).
4. Write the chosen issue number to `.work/used_issue.txt`.

### draft-thursday

Inputs: `SLOT_DATE`, the merged Monday post at `MONDAY_DIR`, and its source issue in `.work/source_issue.json`.

1. Write the Thursday post folder using the Thursday template, with the same `scenario` and `pair` pointing back to Monday. Do not edit the Monday post.
2. The diagram shows the fixed design: same layout as Monday, failing path now working, the fix labeled.
3. Root cause, fix and evidence come only from the source issue. Missing pieces become `[[NEEDS: ...]]` placeholders.
4. Write `.work/pr_body.md`.

### triage-scan

Input: `.work/digest.json` (new feed and subreddit items).

1. Keep only items about cloud networking or network security that a decision-maker should care about. Most days, zero to two items qualify. Never more than three.
2. For each, write an entry in `.work/new_ideas.json` as a JSON list of objects: `{"title": str, "body": str, "pillar": "financial|adoption|continuity", "source": "news|reddit"}`. The body says what changed, the consequence for a leader, which pillar, a suggested angle, and the source link. Never copy a Reddit post's wording or name its author.
3. If nothing qualifies, write `[]`.

### weekly-review

Inputs: `data/scoreboard.csv`, `data/learning.md`, posts published in the last 7 days.

1. Write `.work/weekly_report.md`: best and worst post (by 7-day saves, then % manager-plus viewers), viewer seniority trend, what the test variable showed, one lesson, next week's suggested test.
2. If the lesson is supported by at least two 7-day reads, add it as a rule in `data/learning.md` under the right heading. Otherwise do not edit the file.
3. Never estimate a missing number. Say it is missing.

## PR description (`.work/pr_body.md`)

- One line: slot, pillar, source issue (`#N`).
- **Sources:** a link for every technical claim (official docs or release notes).
- **Sanitizing checklist:** each rule from playbook/03 with a checked box and a one-line note.
- **Placeholders:** list every `[[NEEDS: ...]]`, or "None".
- **Test variable:** what this post tests.
