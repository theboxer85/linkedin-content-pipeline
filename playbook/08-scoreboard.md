# 8. Scoreboard and learning loop

Every post is logged in `data/scoreboard.csv`. The 7-day read decides whether it worked. The main question is whether decision-makers are reading, not just how many people.

## Columns

`post_id, date, day, pillar, scenario, test_variable, read, impressions, reactions, comments, reposts, saves, sends, pct_manager_plus, top_titles, followers_gained, profile_views_week, decision_maker_conversations, notes`

- `read` is `24h` or `7d`.
- Leave a number blank if LinkedIn doesn't show it. Never estimate.
- `decision_maker_conversations` and `notes` are logged by the human, sanitized.

## How numbers get in

LinkedIn does not give personal-profile analytics to self-serve API apps, so reads are manual: the pipeline opens a "Metrics" issue at 24 hours and at 7 days with a table to fill in from the post's analytics page. Closing the issue writes the row to the scoreboard.

## Rules

1. Two reads, at 24 hours and at 7 days. No verdict before the 7-day read.
2. One test at a time. Change one variable per post and name it in `test_variable`. First test: hook style.
3. Weekly review on Friday: best and worst post, viewer seniority trend, one lesson.
4. Lessons become rules in `data/learning.md` under Wins, Losses or Current rules. Drafts follow the current rules.
