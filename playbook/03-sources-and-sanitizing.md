# 3. Sources and sanitizing

Scenarios come from field work and from subreddits. Every idea lands as a GitHub issue labeled `idea`, and nothing reaches a draft until it passes the sanitizing rules.

## Sources

- **Field work in Claude Code:** the local `/mine-sessions` command reads recent Claude Code session transcripts and proposes problem-and-resolution candidates. Transcripts contain real client details, so sanitizing happens on the laptop, before any issue is filed. `/idea` files a single note.
- **Subreddits:** r/AZURE, r/aws, r/googlecloud, r/networking. Look for questions where leaders or engineers are visibly struggling. Never copy a post's wording or identify the poster.
- **CSP announcements:** Azure updates, AWS What's New, GCP release notes. Routed to a pillar.

## Idea issues

A good idea issue for a Monday/Thursday pair has: what broke, the business impact, what was in place / already ruled out, the root cause, the fix, and the evidence. If the root cause or fix is missing, the idea can be used for a Monday post only after the human adds them, because Thursday may never be invented.

## Sanitizing rules (apply before filing an issue and again before drafting)

- **Company names:** always Contoso, Fabrikam or Northwind Traders, or no company name at all ("a recent move to GCP").
- **Never shared:** vendor contract details, people's names, addresses, any other personal or sensitive information.
- **Technical identifiers:** client IP ranges, hostnames, subscription IDs and tenant IDs are left out or replaced with generic ranges such as 10.0.0.0/16. Public, documented provider ranges (for example Google's 35.199.192.0/19 for Cloud DNS forwarding, Azure's 168.63.129.16) are fine and are listed in `data/allowed_ranges.txt`.
- **Screenshots and diagrams:** scrubbed by the same rules as text.
- **Identifying combinations:** generalize or change at least one of industry, location or scale, so the client can't be recognized even without a name.
- **Dates:** leave out the dates of real incidents or outages.
