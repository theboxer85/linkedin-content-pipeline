# 9. Guardrails

These rules override anything else. The agent never breaks them.

## Accuracy

1. Every technical claim in a draft links to its source (CSP docs or release notes) in the PR description.
2. Prices and limits are dated ("as of November 2026").
3. Composites are fine, invented facts are not. Never make up numbers, outcomes, root causes, fixes or quotes that didn't happen. If the idea issue lacks a detail, leave a `[[NEEDS: ...]]` placeholder and say so in the PR description. The validator blocks merge-ready status while placeholders remain.
4. If a reader points out an error, it is corrected the same day: edit the post and reply in the comments (human task).

## Confidentiality

5. Every idea passes the sanitizing rules (playbook/03) before it becomes an issue, and again before it is published.
6. Diagrams are scrubbed by the same rules as text.

## Approval and automation

7. Nothing publishes without a merged PR.
8. The agent never comments, replies, sends DMs, sends connection requests or reacts on LinkedIn. All engagement is human.

## Tone

9. Criticize designs and decisions, never named companies, vendors or people.
10. No engagement bait ("Comment YES if...", "Agree?"). The closing question must be one people can actually answer.
11. Never imply a partnership, endorsement or insider status with a cloud provider.
