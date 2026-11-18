---
description: File a sanitized post idea to the LinkedIn content pipeline
argument-hint: <rough note, or leave blank to use what we just worked on>
allowed-tools: Bash(gh issue create:*), Bash(gh issue list:*)
---

Turn a problem from my field work into a post idea for my LinkedIn pipeline repo `__REPO__`.

My note: $ARGUMENTS

If the note is blank or thin, use what we worked on in this session: the problem, what it broke, what was ruled out, the root cause, the fix and the evidence.

## 1. Draft the idea

Fill these sections, briefly and in plain words. Leave a section as "Unknown" rather than guessing.

- **Pillar:** financial (cost), adoption (migration and change risk), or continuity (outages, security, DR)
- **What broke or what's the topic**
- **Business impact:** what it cost, who saw it
- **What was in place / already ruled out**
- **Root cause**
- **Fix and the evidence that confirmed it**

## 2. Sanitize it (every rule, no exceptions)

- Company names become Contoso, Fabrikam or Northwind Traders, or no name at all.
- Remove people's names, addresses, vendor contract details and any other personal or sensitive information.
- Remove client IP ranges, hostnames, subscription and tenant IDs. Replace with generic ranges like 10.0.0.0/16 only if the range matters to the story. Public, documented provider ranges (such as Google's 35.199.192.0/19) may stay.
- Change or generalize at least one of industry, location or scale.
- Remove dates of real incidents.

## 3. Confirm with me

Show me the exact issue title (starting with "Idea: ") and body you will file, and list what you changed while sanitizing. Do not file anything until I say yes.

## 4. File it

When I confirm, run:

```
gh issue create --repo __REPO__ --label idea,field,pillar:<pillar> --title "<title>" --body "<body>"
```

Use `--label idea,field` alone if the pillar is unclear. Reply with the issue link.
