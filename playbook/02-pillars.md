# 2. Pillars and weekly arc

Three pillars cover what keeps leaders up at night: money, change and failure. Each week follows one scenario from a single pillar. Monday introduces the challenge, Thursday resolves it.

| Pillar (label) | Who it speaks to | What a post contains | Why they care |
| --- | --- | --- | --- |
| Financial concerns (`pillar:financial`) | Leaders who own verticals measured on performance, whose budgets get cut when they grow | Hidden cost drivers in a networking design, cost vs. performance trade-offs, questions to ask before approving a spend or design | Getting the performance without letting costs get out of hand, and without becoming the department finance targets for cuts |
| Adoption and migration risk (`pillar:adoption`) | Leaders moving parts of the business to technology the team doesn't know yet | What really changes when a workload moves to the cloud, where migrations quietly add risk (redesign, skills gaps, new operating models), how to adopt a framework without stalling, the cost of standing still | Redesign risk is a major cause of stalled innovation, and standing still is also a risk |
| Business continuity (`pillar:continuity`) | Leaders worried about security incidents and outages, who want to remain not famous | How designs hold up when something fails (outages, security incidents, region loss), what good DR and resilience look like in plain terms, how strong continuity design gets more projects approved | Designs that clearly cover real revenue loss get approved more often |

Hidden networking cost drivers worth knowing for the Financial pillar: data transfer (internet egress, inter-region, sometimes inter-AZ), per-GB processing on NAT gateways / firewalls / private endpoints / load balancers, always-on hourly resources (vWAN hubs, Azure Firewall, VPN gateways), hybrid circuits plus provider port fees. Never state exact prices without a date and a source.

## Weekly arc

- **Monday, the challenge:** a scenario drawn from real situations with identifying details changed. Lead with the consequence. Must stand on its own for readers who never see Thursday.
- **Thursday, the resolution:** one-line recap of Monday, what solved it and why, the question a leader should ask their team, one question for readers.
- **Pillar rotation:** Financial → Adoption → Continuity → repeat. The rotation is anchored in `data/rotation.yml`.
- **News:** route every CSP announcement into the pillar it affects ("this changes your costs", "this lowers your migration risk", "this closes a continuity gap"). A major announcement can take the Monday slot.

## Pace

- Weeks 1–4: 2 posts a week, Monday and Thursday.
- Move to 3 a week only after four weeks without a missed post. The third post is a standalone (e.g. a midweek news take).
- Never more than one post a day. Extra drafts stay as banked ideas.
