# LinkedIn content pipeline

Ideas go in as issues, an agent drafts posts as pull requests, you review and merge, and merged posts publish to LinkedIn on schedule. Nothing publishes without your merge.

```
 ideas ──► draft PR ──► you review + merge ──► publishes at 7:45 AM CT ──► metrics issues ──► weekly review
 (issues)   (Fri / Tue)                          (Mon / Thu)                 (24h, 7d)          (Fri)
```

The rules the agent follows are in [`playbook/`](playbook) and [`CLAUDE.md`](CLAUDE.md). Change the playbook and the drafts change with it.

## What runs when (all times Central)

| Workflow | When | What it does |
| --- | --- | --- |
| `scan.yml` | Daily ~6 AM | Pulls Azure, AWS and GCP announcements plus r/AZURE, r/aws, r/googlecloud, r/networking. The agent files at most 3 relevant ideas as issues. |
| `draft.yml` | Fri ~2–3 PM, Tue ~5–6 PM | The agent picks an idea (Monday) or resolves Monday's post (Thursday), writes the post and diagram, and opens a PR with the rendered image, sources and a sanitizing checklist. |
| `checks.yml` | When you push edits to a draft PR | Re-renders the diagram and re-checks the post against the playbook rules. |
| `publish.yml` | Mon and Thu mornings | Publishes merged posts whose time has come. A post more than 6 hours late is skipped, never posted at an odd hour. |
| `metrics.yml` | Daily, and when you close a Metrics issue | Opens a Metrics issue 24 hours and 7 days after each post. Closing it writes the numbers to `data/scoreboard.csv`. Also warns a week before the LinkedIn token expires. |
| `weekly-review.yml` | Fri ~3:30 PM | The agent writes the weekly review as an issue, and proposes new rules for `data/learning.md` as a PR. |

## Your weekly routine

1. **Fri–Sun:** review the Monday draft PR. Edit the text in `post.md` or the diagram in `diagram.drawio` right in the PR if you want changes. Merge when it's right.
2. **Mon 7:45–8:45 AM:** reply to comments.
3. **Wednesday:** review and merge the Thursday draft PR.
4. **Thu 7:45–8:45 AM:** reply to comments.
5. **When a Metrics issue appears:** open the post's analytics on LinkedIn, edit the issue to fill in the table, and close it.
6. **Any time:** file ideas with `/idea` or `/mine-sessions` in Claude Code, or with the Idea issue form on your phone.

Don't merge a PR whose Checks are red, or that still has `[[NEEDS: ...]]` placeholders.

## One-time setup

### 1. Let Actions open pull requests

Settings → Actions → General → Workflow permissions: choose **Read and write permissions** and tick **Allow GitHub Actions to create and approve pull requests**.

### 2. Agent credential for Actions

On your laptop:

```
claude setup-token
gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo theboxer85/linkedin-content-pipeline
```

Paste the token when `gh` asks.

### 3. LinkedIn app (about 10 minutes)

1. Go to [linkedin.com/developers/apps](https://www.linkedin.com/developers/apps) and create an app. LinkedIn requires the app to be associated with a Company Page; any page you admin works (it does not post as the page).
2. On the **Products** tab, add **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**. Both are self-serve.
3. On the **Auth** tab, add the redirect URL `http://localhost:8765/callback`, and copy the Client ID and Client Secret.
4. On your laptop, from a clone of this repo:

```
pip install requests
export LINKEDIN_CLIENT_ID=...
export LINKEDIN_CLIENT_SECRET=...
python scripts/linkedin_auth.py --repo theboxer85/linkedin-content-pipeline
```

It opens LinkedIn, you approve, and it saves the token and your member id to the repo. **LinkedIn tokens last about 60 days.** You'll get an issue a week before it expires; renew by running the same command.

### 4. Optional: private denylist

Add a secret `SANITIZE_DENYLIST` with real client names, people and hostnames you never want published, comma-separated. The checks fail any post or diagram that contains one. It stays private to the repo's secrets.

### 5. Local commands

```
bash local/install.sh
```

Adds `/idea` (file the problem you just worked on) and `/mine-sessions` (find ideas in the last week of sessions). Both sanitize and show you the text before filing anything.

### 6. Test it

Actions → **Publish** → Run workflow, with **Dry run** ticked. It prints exactly what would be posted for anything due, without posting.

## Files

- `posts/<date>-<scenario>-<mon|thu>/`: `post.md` (front matter + text), `diagram.drawio`, and the rendered `diagram.png` or `carousel.pdf`.
- `data/scoreboard.csv`: every 24h and 7d read. `data/learning.md`: rules learned from the weekly review.
- `data/rotation.yml`: pillar rotation. `data/skip_dates.txt`: holidays with no posts. `data/sources.yml`: feeds, subreddits and keywords. `data/allowed_ranges.txt`: public provider IP ranges posts may mention.

## Known limits

- **Analytics are manual.** LinkedIn doesn't give personal-profile analytics to self-serve apps, so numbers come from Metrics issues you fill in.
- **Reddit may block GitHub's runners.** The scan logs it and carries on with the CSP feeds.
- **Carousels:** document posts use the Documents API with the same permission as images. If LinkedIn rejects one, the publish run opens an issue, and you can switch that post to `format: image`.
- **Merge protection:** branch protection isn't available for private repos on GitHub Free, so red Checks warn but don't block a merge.
