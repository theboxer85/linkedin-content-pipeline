# 7. Cadence

Posts go live at 7:45 AM Central on Monday and Thursday. All times are America/Chicago; the workflows handle daylight saving time.

| When | What happens | Who |
| --- | --- | --- |
| Daily, ~6 AM | Scan CSP announcements and subreddits; file ideas as issues | `scan.yml` |
| Any time | `/idea` and `/mine-sessions` file sanitized field ideas | You, in local Claude Code |
| Friday, by 3:00 PM | Monday draft opened as a pull request | `draft.yml` |
| Friday to Sunday | Review, edit and merge the Monday PR | You |
| Monday, 7:45 AM | Monday post publishes | `publish.yml` |
| Monday, 7:45–8:45 AM | Reply window | You |
| Tuesday, by 6:00 PM | Thursday draft opened as a pull request | `draft.yml` |
| Wednesday | Review, edit and merge the Thursday PR | You |
| Thursday, 7:45 AM | Thursday post publishes | `publish.yml` |
| Thursday, 7:45–8:45 AM | Reply window | You |
| Friday, ~3:30 PM | Weekly review issue | `weekly-review.yml` |

**Rule:** nothing publishes without a merged PR. Only files on `main` are ever published. If a draft isn't merged by posting time, the slot is skipped, never filled automatically. A post more than 6 hours late is never published; the pipeline opens an issue instead.

**Holidays:** dates in `data/skip_dates.txt` are skipped. Never start a Monday/Thursday pair in a week that can't finish it.
