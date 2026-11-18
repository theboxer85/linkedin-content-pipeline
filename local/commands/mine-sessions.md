---
description: Find post ideas in my recent Claude Code sessions and file the sanitized ones I pick
argument-hint: [days to look back, default 7]
allowed-tools: Bash(find:*), Bash(ls:*), Bash(gh issue list:*), Bash(gh issue create:*), Read, Grep
---

Look through my recent Claude Code sessions for problems worth a LinkedIn post, then file the ones I choose to my pipeline repo `__REPO__`.

Days to look back: $ARGUMENTS (use 7 if blank).

## 1. Find the sessions

List transcripts modified in that window:

```
find ~/.claude/projects -name '*.jsonl' -mtime -<days>
```

Transcripts can be large. Use Grep first to find promising ones, with patterns like `root cause`, `the issue was`, `turned out`, `fixed`, `timeout`, `asymmetric`, `no route`, `denied`, `reset`, `cost`, `egress`. Then Read only the relevant parts. Ignore tool output noise; focus on what the problem was and how it got solved.

## 2. Pick candidates

Keep up to 5 cloud networking or network security problems with a clear problem → cause → fix story that an IT decision-maker should care about. Skip routine work with no lesson.

Check what's already filed so you don't repeat it:

```
gh issue list --repo __REPO__ --label idea --state all --limit 100 --json title
```

## 3. Sanitize every candidate

- Company names become Contoso, Fabrikam or Northwind Traders, or no name at all.
- Remove people's names, addresses, vendor contract details and any other personal or sensitive information.
- Remove client IP ranges, hostnames, subscription and tenant IDs. Public, documented provider ranges may stay.
- Change or generalize at least one of industry, location or scale.
- Remove dates of real incidents.

## 4. Show me, then file what I pick

Show a numbered list. For each: a one-line title, the pillar (financial, adoption or continuity), and the sanitized sections (what broke, business impact, what was in place, root cause, fix and evidence, with "Unknown" where the session doesn't say). Note anything you weren't sure how to sanitize.

Ask which numbers to file. Do not file anything until I answer. For each one I pick:

```
gh issue create --repo __REPO__ --label idea,field,pillar:<pillar> --title "Idea: <title>" --body "<body>"
```

Reply with the issue links.
